"""Apply check/fixes.json (scan-verified corrections) to the docx, then re-parse.

Always works from the untouched backup check/orig/haymanote_abew_church_completed.docx,
so it can be re-run any number of times. Writes the corrected docx back to
../haymanote_abew_church_completed.docx and regenerates docx_parsed.json.

Each fix: {"ch": <chapter position in the docx>, "v": "<printed verse number>" | "heading",
           "old": "...", "new": "...", "scan": "<pdf page/col>", "note": "..."}
"old" must occur exactly once inside that one paragraph. A "\n" in "new" splits the
paragraph (for verses the docx merged); later fixes to the split-off verse still
address the original paragraph, since positions come from the backup.
"v": "p1", "p2"... = the chapter's unnumbered paragraphs (ክፍል line, unnumbered first verse).
"v": "<numeral>#2" = the 2nd proper paragraph of that chapter carrying the same numeral,
"v": "<numeral>~" = a numeral-with-space-only paragraph ("፲፯ ሰውነትህን") that clashes with a proper verse.
"join": true (old/new empty) appends the next paragraph to this one (a verse the docx broke).
"""
import json, re, shutil, subprocess, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCX = HERE.parent / "haymanote_abew_church_completed.docx"
ORIG = HERE / "orig" / DOCX.name
sys.stdout.reconfigure(encoding="utf-8")

if not ORIG.exists():
    ORIG.parent.mkdir(exist_ok=True)
    shutil.copy2(DOCX, ORIG)

fixes = json.loads((HERE / "fixes.json").read_text(encoding="utf-8"))
z = zipfile.ZipFile(ORIG)
x = z.read("word/document.xml").decode()

verse_re = re.compile(r"^([፩-፼]+)\s*[፤፡:፣]")
para_re = re.compile(r"<w:p[ >].*?</w:p>", re.S)

# map (chapter position, printed verse | "heading") -> paragraph span in x
# loose: verse number + space but no separator ("፲፱ ይኸውም"), used only if no proper match
# unnumbered paragraphs (ክፍል line, an unnumbered first verse) are "p1", "p2"... per chapter
index, loose, nextp, ch, prev, extra = {}, {}, {}, 0, None, 0
seen = {}
for m in para_re.finditer(x):
    if prev:
        nextp[prev] = m.span()
    prev = m.span()
    text = re.sub(r"<[^>]+>", "", m.group()).strip()
    if re.match(r"^ምዕራፍ\s+[፩-፼]+$", text):
        ch += 1
        extra = 0
        index[(ch, "heading")] = m.span()
    elif ch and (v := verse_re.match(text)):
        # a numeral repeated in one chapter (docx mis-numbered a verse): 1st keeps the plain key,
        # later ones are addressable as "<numeral>#2", "<numeral>#3"...
        seen[(ch, v.group(1))] = seen.get((ch, v.group(1)), 0) + 1
        n = seen[(ch, v.group(1))]
        index.setdefault((ch, v.group(1) if n == 1 else f"{v.group(1)}#{n}"), m.span())
    elif ch and (v := re.match(r"^([፩-፼]+)[\s፥]", text)):
        loose.setdefault((ch, v.group(1)), m.span())
    elif ch and text:
        extra += 1
        index[(ch, f"p{extra}")] = m.span()
for k, span in loose.items():
    # a loose paragraph whose numeral is also a proper verse (docx mis-numbered it) is "<numeral>~"
    if k in index:
        index.setdefault((k[0], k[1] + "~"), span)
    else:
        index[k] = span

def run_texts(p):
    return re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", p, re.S)

# group fixes by paragraph; each fix must hit exactly one place inside one run
groups, failed = {}, []
for f in fixes:
    span = index.get((f["ch"], f["v"]))
    if not span:
        failed.append((f, "paragraph not found")); continue
    groups.setdefault(span, []).append(f)

# apply back-to-front so earlier spans stay valid
for span in sorted(groups, reverse=True):
    p, end = x[span[0]:span[1]], span[1]
    # "join": true = pull the following paragraph's text onto the end of this one
    # (one join per following paragraph: two joins pull in the next two)
    cur = span
    for _ in range(sum(1 for f in groups[span] if f.get("join"))):
        cur = nextp[cur]
        end = cur[1]
        tail = re.sub(r"<[^>]+>", "", x[cur[0]:end]).strip()
        i = p.rfind("</w:t>")
        p = p[:i] + " " + tail + p[i:]
    for f in groups[span]:
        if f.get("join"):
            continue
        if sum(t.count(f["old"]) for t in run_texts(p)) != 1:
            failed.append((f, "old text not found exactly once in one run")); continue
        # "\n" in new = start a new paragraph with the same paragraph/run properties
        ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S)
        rpr = re.search(r"<w:rPr>.*?</w:rPr>", p, re.S)
        brk = ('</w:t></w:r></w:p><w:p>' + (ppr.group() if ppr else "") + "<w:r>"
               + (rpr.group() if rpr else "") + '<w:t xml:space="preserve">')
        new = f["new"].replace("\n", brk)
        p = re.sub(r"(<w:t(?: [^>]*)?>)(.*?)(</w:t>)",
                   lambda m: m.group(1) + m.group(2).replace(f["old"], new) + m.group(3)
                   if f["old"] in m.group(2) else m.group(), p, flags=re.S)
    x = x[:span[0]] + p + x[end:]

tmp = DOCX.with_suffix(".tmp")
with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
    for item in z.infolist():
        data = x.encode() if item.filename == "word/document.xml" else z.read(item)
        out.writestr(item, data)
tmp.replace(DOCX)

print(f"applied {len(fixes) - len(failed)}/{len(fixes)} fixes -> {DOCX.name}")
for f, why in failed:
    print("FAILED", f["ch"], f["v"], f["old"], "-", why)
subprocess.run([sys.executable, "-I", str(HERE / "parse_docx.py")], check=True)
