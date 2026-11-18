"""Sub-division of the Preparatory Service (division d02, PDF pages 9-110).

Level 1 = the four chapters the book itself prints (CHAPTER 1, II, III, IV).
Level 2 = parts: each prayer / rite step, named from the book's own headings and
          rubrics. 'rite' tags the part with the stage of the Ethiopian Ordo
          Communis it belongs to (stage names follow ethiopianorthodox.org,
          "The Divine Liturgy" article).
A part runs from its start entry id to the entry before the next part's start.
"""

CHAPTERS = [
    # (number, name_english, name_source, first part start id)
    ('I', 'Consecration of new vessels', 'book heading', 'p009-01'),
    ('II', 'Preparatory service for the Liturgy', 'book heading', 'p013-01'),
    ('III', 'From the entrance to the Gospel reading (Liturgy of the Catechumens)', 'book prints only "CHAPTER III"', 'p043-03'),
    ('IV', 'From the dismissal of the Catechumens to the Kiss of Peace (Liturgy of the Faithful)', 'book prints only "CHAPTER IV"', 'p096-03'),
    ('end', 'Opening of the Anaphora of the Apostles (printed on the last page of this section)', 'book heading', 'p109-05'),
]

PARTS = [
    # (start id, rite stage, name_english)
    ('p009-01', 'Consecration of new vessels', 'Prayer at the consecration of the Paten'),
    ('p010-05', 'Consecration of new vessels', 'Prayer at the consecration of the Chalice'),
    ('p011-04', 'Consecration of new vessels', 'Prayer at the consecration of the Cross-spoon'),
    ('p013-01', 'Rite of Preparation', 'Opening exhortation to the priest and the faithful'),
    ('p015-03', 'Rite of Preparation', 'Prayer of Penitence'),
    ('p015-05', 'Rite of Preparation', 'Psalm 25'),
    ('p017-09', 'Rite of Preparation', 'Psalm 61'),
    ('p018-07', 'Rite of Preparation', 'Psalm 102'),
    ('p021-05', 'Rite of Preparation', 'Psalm 103'),
    ('p024-01', 'Rite of Preparation', 'Psalm 129'),
    ('p024-10', 'Rite of Preparation', 'Psalm 130'),
    ('p025-03', 'Rite of Preparation', 'Prayer for the Holy Spirit to descend on the church, the ark and the vessels'),
    ('p026-03', 'Rite of Preparation', 'Prayer of Gregory before entering within the Veil'),
    ('p027-04', 'Rite of Preparation', 'Prayer of Basil over the cupboards'),
    ('p028-05', 'Rite of Preparation', 'Prayer of John'),
    ('p030-04', 'Rite of Preparation', 'Prayer over all the Vessels of the Church'),
    ('p031-04', 'Rite of Preparation', 'Prayer over the Coverings'),
    ('p032-01', 'Rite of Preparation', 'Prayer over the Paten'),
    ('p032-05', 'Rite of Preparation', 'Prayer over the Chalice'),
    ('p033-03', 'Rite of Preparation', 'Prayer over the Cross-spoon'),
    ('p034-03', 'Rite of Preparation', 'Prayer over the Masob'),
    ('p035-01', 'Rite of Preparation', 'Dressing the ark; prayer of the priest'),
    ('p036-03', 'Rite of Preparation', 'Prayer of the Father'),
    ('p037-02', 'Vesting', 'Psalm verses before the priest\'s vesting'),
    ('p039-01', 'Vesting', 'The Canon (rules for the celebrant and the people)'),
    ('p042-03', 'Introit', 'Songs of the people (Monday-Friday, Saturdays, Sundays)'),
    ('p043-03', 'Introit', 'Entrance: awe at the sacrifice, call to stand in quietness, Halleluia'),
    ('p044-03', 'Offertory', 'Procession with the Host and blessing of the bread'),
    ('p047-03', 'Offertory', 'Blessing of the chalice'),
    ('p049-04', 'Offertory', 'Doxology and Psalm 116'),
    ('p050-03', 'Offertory', 'Prayer of Thanksgiving of St. Basil'),
    ('p052-04', 'Offertory', 'Prayer of Oblation by the assistant priest'),
    ('p054-03', 'Offertory', 'Prayer of Oblation by the priest'),
    ('p056-01', 'Offertory', 'Prayer of the Wrappings (covering the bread and the chalice)'),
    ('p057-01', 'Absolution', 'Prayer of Absolution to the Son'),
    ('p060-05', 'Litanies', 'Deacon\'s litanies ("For ... we beseech")'),
    ('p065-04', 'Incensing', 'Taking up the incense'),
    ('p068-04', 'Incensing', 'Prayer of the Incense and intercessions'),
    ('p072-01', 'Incensing', 'Censing the altar, the church and the priests'),
    ('p074-04', 'Readings', 'Epistles of St. Paul (prayer and reading)'),
    ('p078-01', 'Readings', 'Catholic Epistles (prayer and reading)'),
    ('p079-02', 'Readings', 'Acts of the Apostles (prayer and reading)'),
    ('p080-03', 'Readings', 'Prayer over the offering (the sacrifice of Abraham)'),
    ('p080-06', 'Readings', 'Prayer for the church, with praises of the Holy Virgin Mary'),
    ('p082-03', 'Gospel', 'Hymns while the ministers go out of the sanctuary'),
    ('p084-04', 'Gospel', 'Trisagion and praise of the Holy Trinity'),
    ('p085-03', 'Gospel', 'Prayer of the Gospel'),
    ('p088-01', 'Gospel', 'Gospel procession and announcement'),
    ('p090-01', 'Gospel', 'Prayer of the assistant priest (intercessions, "Remember, Lord ...")'),
    ('p093-04', 'Gospel', 'Reading of the Gospel and the closing rules'),
    ('p096-03', 'Dismissal of the Catechumens', 'Dismissal of the Catechumens and prayer of Basil'),
    ('p097-04', 'Liturgy of the Faithful', 'Prayer for the peace of the church'),
    ('p098-06', 'Liturgy of the Faithful', 'Prayer for the Patriarch and the bishops'),
    ('p100-05', 'Liturgy of the Faithful', 'Prayer for the congregation'),
    ('p102-03', 'Liturgy of the Faithful', 'The Creed (Amakniyou of the Apostles)'),
    ('p105-03', 'Liturgy of the Faithful', 'Uncovering the gifts and washing of the hands'),
    ('p107-03', 'Kiss of Peace', 'Prayer of Salutation (Kiss of Peace) of Basil'),
    ('p109-05', 'Anaphora', 'First lines of the Anaphora of the Apostles (also on the duplicate scan, PDF page 110)'),
]


def build_parts(entries):
    """entries: list of merged entry dicts (division d02, in order).
    Returns chapters -> parts -> entries. Raises if a start id is missing or
    out of order, so the table can never silently drop or duplicate entries."""
    pos = {e['id']: i for i, e in enumerate(entries)}
    starts = [s for s, _, _ in PARTS]
    for s in starts:
        if s not in pos:
            raise SystemExit('part start id not found: ' + s)
    if [pos[s] for s in starts] != sorted(set(pos[s] for s in starts)):
        raise SystemExit('part start ids are not in increasing order')
    if starts[0] != entries[0]['id']:
        raise SystemExit('first part must start at the first entry')
    chapter_starts = {c[3]: c for c in CHAPTERS}
    chapters, n = [], 0
    for k, (sid, rite, name) in enumerate(PARTS):
        end = pos[PARTS[k + 1][0]] if k + 1 < len(PARTS) else len(entries)
        chunk = entries[pos[sid]:end]
        if sid in chapter_starts:
            num, cname, csrc, _ = chapter_starts[sid]
            chapters.append({'chapter': num, 'name_english': cname,
                             'name_source': csrc, 'parts': []})
        n += 1
        head = entries[pos[sid]]
        heading = head if head['kind'] == 'rubric' and len(head.get('english') or '') < 90 else None
        chapters[-1]['parts'].append({
            'part': n, 'name_english': name, 'rite_stage': rite,
            'book_heading_geez': heading and heading.get('geez'),
            'book_heading_english': heading and heading.get('english'),
            'first_entry': chunk[0]['id'], 'last_entry': chunk[-1]['id'],
            'first_pdf_page': int(chunk[0]['id'][1:4]),
            'last_pdf_page': int(chunk[-1]['id'][1:4]),
            'entry_count': len(chunk), 'entries': chunk})
    for c in chapters:
        allp = c['parts']
        c['first_entry'], c['last_entry'] = allp[0]['first_entry'], allp[-1]['last_entry']
        c['part_count'] = len(allp)
        c['entry_count'] = sum(p['entry_count'] for p in allp)
    return chapters
