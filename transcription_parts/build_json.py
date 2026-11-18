"""Convert the transcription_parts/pNNN-NNN.md files into two JSON files.

  ../kidase_geez_amharic.json   Ge'ez + Amharic text
  ../kidase_english.json        English text

Both files are grouped into the same divisions (contents, Preparatory Service,
each anaphora, commentary), with the same pages and the same entry ids (e.g. "p109-03"), so an
entry in one can be joined to its counterpart in the other by id.
Run:  python -W ignore build_json.py
"""
import glob
import json
import os
import re
import sys

import prep_parts

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)

FIELD_KEYS = {'ግዕዝ': 'geez', 'አማርኛ': 'amharic', 'English': 'english'}
FIELD_RE = re.compile(r'^\*\*(ግዕዝ|አማርኛ|English):\*\*[ \t]?(.*)$')
PAGE_RE = re.compile(r'^## Page (\d+) \((.*?)\) — (.*)$')
PAGE_NOTE_RE = re.compile(r'^## PDF Page (\d+) \(printed (\S+) / (\d+)\) — (.*)$')
PRINTED_RE = re.compile(r'^printed (\S+) / (\d+)$')
NUM_RE = re.compile(r'^(\S+) / (\d+)(?: \((continued[^)]*)\))?$')
MARK = '⟦?'


def parse_heading(text):
    """Return (kind, number, geez_numeral, continued, heading_note)."""
    t = text.strip()
    if t.startswith('[RUBRIC]'):
        note = t[len('[RUBRIC]'):].strip()
        return 'rubric', None, None, None, note.strip('()') or None
    if t == '[CONTENTS]':
        return 'contents', None, None, None, None
    if t == '[NOTE]':
        return 'note', None, None, None, None
    m = re.match(r'^\[(\d+)\]$', t)
    if m:
        return 'commentary', int(m.group(1)), None, None, None
    if t == '(unnumbered)':
        return 'paragraph', None, None, None, 'unnumbered'
    m = NUM_RE.match(t)
    if m:
        return 'paragraph', int(m.group(2)), m.group(1), m.group(3), None
    raise ValueError('unknown heading: ' + text)


def split_title(title):
    """'ቅዳሴ ሐዋርያት / The Anaphora of the Apostles (note)' -> parts."""
    geez, _, english = title.partition(' / ')
    note = None
    m = re.match(r'^(.*?)\s*\((.*)\)\s*$', english)
    if m:
        english, note = m.group(1), m.group(2)
    return geez.strip(), english.strip(), note


def finish_block(block, page, problems):
    if block is None:
        return
    fields = block['fields']
    for k, lines in list(fields.items()):
        while lines and not lines[-1].strip():
            lines.pop()
        fields[k] = '\n'.join(lines)
    body = block['body']
    while body and not body[-1].strip():
        body.pop()
    block['text'] = '\n'.join(body) if body else None
    page['blocks'].append(block)


def parse_files():
    pages = []
    problems = []
    for path in sorted(glob.glob(os.path.join(HERE, 'p*.md'))):
        page = None
        block = None
        field = None
        fname = os.path.basename(path)
        for ln, raw in enumerate(open(path, encoding='utf-8').read().split('\n'), 1):
            line = raw.rstrip('\r')
            m = PAGE_RE.match(line)
            n = PAGE_NOTE_RE.match(line)
            if m or n:
                finish_block(block, page, problems)
                block = field = None
                if m:
                    pdf, paren, title = int(m.group(1)), m.group(2), m.group(3)
                    pm = PRINTED_RE.match(paren)
                    printed_geez, printed_num = (pm.group(1), int(pm.group(2))) if pm else (None, None)
                    front = None if pm else paren
                    duplicate_of = None
                else:
                    pdf, printed_geez, printed_num = int(n.group(1)), n.group(2), int(n.group(3))
                    title, front, duplicate_of = n.group(4), None, None
                    if 'DUPLICATE' in title:
                        duplicate_of = pdf - 1
                g, e, note = split_title(title)
                page = {
                    'pdf_page': pdf, 'printed_page_geez': printed_geez,
                    'printed_page': printed_num, 'section_geez': g,
                    'section_english': e, 'page_note': front or note,
                    'duplicate_of_pdf_page': duplicate_of, 'blocks': [],
                    '_file': fname,
                }
                if m is None:
                    page['section_geez'] = page['section_english'] = None
                    page['page_note'] = title
                pages.append(page)
                continue
            if line.startswith('## '):
                problems.append((fname, ln, 'unparsed page header: ' + line[:80]))
                continue
            if line.startswith('### '):
                finish_block(block, page, problems)
                kind, num, gnum, cont, hnote = parse_heading(line[4:])
                block = {'kind': kind, 'number': num, 'geez_numeral': gnum,
                         'continued': cont, 'heading_note': hnote,
                         'fields': {}, 'body': []}
                field = None
                continue
            if line.strip() == '---':
                finish_block(block, page, problems)
                block = field = None
                continue
            fm = FIELD_RE.match(line)
            if fm:
                if block is None:
                    problems.append((fname, ln, 'field outside block'))
                    continue
                field = FIELD_KEYS[fm.group(1)]
                if field in block['fields']:
                    problems.append((fname, ln, 'duplicate field ' + field))
                    block['fields'][field].append(fm.group(2))
                else:
                    block['fields'][field] = [fm.group(2)]
                continue
            if block is None:
                if line.strip() and page is not None and not page['blocks']:
                    # note printed under the page header, before the first block
                    page['page_note'] = (page['page_note'] + '; ' if page['page_note'] else '') + line.strip()
                elif line.strip():
                    problems.append((fname, ln, 'text outside block: ' + line[:60]))
                continue
            if field is not None:
                block['fields'][field].append(line)
            else:
                block['body'].append(line)
        finish_block(block, page, problems)
    return pages, problems


def build(pages):
    seen = set()
    ga_pages, en_pages = [], []
    for p in pages:
        if p['pdf_page'] in seen:
            raise SystemExit('duplicate pdf page %d' % p['pdf_page'])
        seen.add(p['pdf_page'])
        head = {k: v for k, v in p.items() if k not in ('blocks', '_file')}
        ga_e, en_e = [], []
        for i, b in enumerate(p['blocks'], 1):
            base = {'id': 'p%03d-%02d' % (p['pdf_page'], i), 'kind': b['kind'],
                    'number': b['number'], 'geez_numeral': b['geez_numeral'],
                    'continued': b['continued'], 'heading_note': b['heading_note']}
            f = b['fields']
            ga = dict(base, geez=f.get('geez'), amharic=f.get('amharic'))
            en = dict(base, english=f.get('english'))
            if b['text'] is not None:
                ga['note'] = en['note'] = b['text']
            ga['uncertain'] = any(MARK in (ga[k] or '') for k in ('geez', 'amharic'))
            en['uncertain'] = MARK in (en['english'] or '')
            ga_e.append(ga)
            en_e.append(en)
        ga_pages.append(dict(head, entries=ga_e))
        en_pages.append(dict(head, entries=en_e))
    return ga_pages, en_pages


DIVISION_KIND = {'ማውጫ': 'contents', 'ሥርዓተ ቅዳሴ': 'preparatory_service', 'ሐተታ': 'commentary'}
DIVISION_ENGLISH = {'ቅዳሴ ባስልዮስ': 'The Anaphora of St. Basil'}


def group_divisions(pages):
    """Group consecutive pages into divisions: contents, preparatory service,
    each anaphora, commentary. A page with no section (the p110 duplicate-scan
    note) stays in the division before it."""
    divisions = []
    for p in pages:
        key = p['section_geez']
        if key is None or (divisions and divisions[-1]['name_geez'] == key):
            divisions[-1]['pages'].append(p)
            continue
        divisions.append({
            'id': 'd%02d' % (len(divisions) + 1),
            'kind': DIVISION_KIND.get(key, 'anaphora'),
            'name_geez': key,
            'name_english': DIVISION_ENGLISH.get(key, p['section_english']),
            'pages': [p],
        })
    for d in divisions:
        nums = [p['pdf_page'] for p in d['pages']]
        d['first_pdf_page'], d['last_pdf_page'] = nums[0], nums[-1]
        d['page_count'] = len(nums)
        d['entry_count'] = sum(len(p['entries']) for p in d['pages'])
        for p in d['pages']:
            p['division'] = d['id']
    return divisions


def slug(text):
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')


def write_by_division(doc, lang):
    """One small file per division in ../Full_Kidase_by_division/NN_name/."""
    root = os.path.join(OUT, 'Full_Kidase_by_division')
    index = []
    for d in doc['divisions']:
        folder = '%s_%s' % (d['id'][1:], slug(d['name_english'].replace('The Anaphora of', '').replace('Anaphora of', '')) or d['kind'])
        if d['kind'] != 'anaphora':
            folder = '%s_%s' % (d['id'][1:], d['kind'])
        os.makedirs(os.path.join(root, folder), exist_ok=True)
        part = {k: v for k, v in doc.items() if k not in ('divisions', 'page_count', 'entry_count', 'division_count')}
        part['division'] = d
        with open(os.path.join(root, folder, lang + '.json'), 'w', encoding='utf-8') as fh:
            json.dump(part, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        index.append({k: v for k, v in d.items() if k != 'pages'} | {'folder': folder})
    with open(os.path.join(root, 'index.json'), 'w', encoding='utf-8') as fh:
        json.dump({'title': 'Full Kidase', 'divisions': index}, fh, ensure_ascii=False, indent=1)
        fh.write('\n')


SUBDIVISION_SOURCES = [
    {'title': 'The Divine Liturgy (Ethiopian Orthodox Tewahedo Church)',
     'url': 'https://www.ethiopianorthodox.org/english/church/divineliturgydoc.html',
     'used_for': 'names of the rite stages (preparation, vesting, offertory, absolution, incensing, readings, Gospel, Liturgy of the Faithful, Kiss of Peace)'},
    {'title': 'Ethiopian Orthodox liturgy outline',
     'url': 'https://eotbible.com/liturgy.html',
     'used_for': 'cross-check of the overall order (preparation, word, faithful)'},
]


def write_preparatory(ga_doc, en_doc):
    """ONE json for the Preparatory Service: chapters -> parts -> entries, with
    Ge'ez, Amharic and English side by side."""
    ga = next(d for d in ga_doc['divisions'] if d['kind'] == 'preparatory_service')
    en = next(d for d in en_doc['divisions'] if d['kind'] == 'preparatory_service')
    en_by_id = {e['id']: e for p in en['pages'] for e in p['entries']}
    entries = []
    for p in ga['pages']:
        for e in p['entries']:
            m = {k: e[k] for k in ('id', 'kind', 'number', 'geez_numeral', 'continued', 'heading_note')}
            m['geez'], m['amharic'] = e['geez'], e['amharic']
            m['english'] = en_by_id[e['id']]['english']
            if 'note' in e:
                m['note'] = e['note']
            m['uncertain'] = e['uncertain'] or en_by_id[e['id']]['uncertain']
            entries.append(m)
    if len(entries) != len(en_by_id):
        raise SystemExit("Ge'ez/Amharic and English entry counts differ")
    chapters = prep_parts.build_parts(entries)
    covered = [e['id'] for c in chapters for pt in c['parts'] for e in pt['entries']]
    if covered != [e['id'] for e in entries]:
        raise SystemExit('sub-division does not cover every entry exactly once')
    doc = {
        'title': 'Full Kidase - Preparatory Service (ሥርዓተ ቅዳሴ)',
        'division': ga['id'], 'name_geez': ga['name_geez'], 'name_english': ga['name_english'],
        'source': ga_doc['source'], 'ids': ga_doc['ids'], 'uncertain_marker': ga_doc['uncertain_marker'],
        'first_pdf_page': ga['first_pdf_page'], 'last_pdf_page': ga['last_pdf_page'],
        'page_count': ga['page_count'], 'entry_count': len(entries),
        'chapter_count': len(chapters), 'part_count': sum(c['part_count'] for c in chapters),
        'how_divided': ('Chapters I-IV are the chapters printed in the book. Parts are the prayers and rite steps '
                        'inside them, named from the headings of the book itself and rubrics; rite_stage groups them under the '
                        'stage names used by the Ethiopian Orthodox Church for the Ordo Communis (see sources). '
                        'The names of CHAPTER III and IV (printed with no title) and the part boundaries are the '
                        'judgment of the transcriber, not a published table.'),
        'sources': SUBDIVISION_SOURCES,
        'chapters': chapters,
    }
    folder = os.path.join(OUT, 'Full_Kidase_by_division', '02_preparatory_service')
    with open(os.path.join(folder, 'preparatory_service.json'), 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print('preparatory_service.json', doc['chapter_count'], 'chapters', doc['part_count'], 'parts', doc['entry_count'], 'entries')


def lang_key(name):
    return 'ga' if 'geez' in name else 'en'


def main():
    pages, problems = parse_files()
    if problems:
        for pr in problems:
            print('PROBLEM', pr, file=sys.stderr)
    ga_pages, en_pages = build(pages)
    docs = {}
    meta = {
        'source': 'Full Kidase.pdf (PDF pages 8-420; page numbers are the PDF page numbers)',
        'ids': 'Entry ids are shared between the two files: pNNN-NN = PDF page, entry order on that page.',
        'uncertain_marker': 'Text between ⟦? and ?⟧ is a word the transcriber could not read with confidence.',
    }
    for name, lang, pg in (('kidase_geez_amharic.json', 'Ge\'ez (ግዕዝ) and Amharic (አማርኛ)', ga_pages),
                           ('kidase_english.json', 'English', en_pages)):
        doc = dict(title='Full Kidase', language=lang, **meta,
                   page_count=len(pg), entry_count=sum(len(p['entries']) for p in pg),
                   division_count=0, divisions=group_divisions(pg))
        doc['division_count'] = len(doc['divisions'])
        with open(os.path.join(OUT, name), 'w', encoding='utf-8') as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
            fh.write('\n')
        write_by_division(doc, 'geez_amharic' if 'geez' in name else 'english')
        docs[lang_key(name)] = doc
        print(name, doc['division_count'], 'divisions', doc['page_count'], 'pages', doc['entry_count'], 'entries')
    write_preparatory(docs['ga'], docs['en'])


if __name__ == '__main__':
    main()
