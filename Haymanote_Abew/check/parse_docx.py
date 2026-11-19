"""Split haymanote_abew_church_completed.docx into chapters/verses -> docx_parsed.json."""
import json, re, sys, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOCX = HERE.parent / "haymanote_abew_church_completed.docx"

ONES = {c: i + 1 for i, c in enumerate("፩፪፫፬፭፮፯፰፱")}
TENS = {c: (i + 1) * 10 for i, c in enumerate("፲፳፴፵፶፷፸፹፺")}

def geez_num(s):
    total, cur = 0, 0
    for ch in s:
        if ch == "፻":
            total += (cur or 1) * 100; cur = 0
        elif ch == "፼":
            total = (total + cur or 1) * 10000; cur = 0
        else:
            cur += ONES.get(ch) or TENS.get(ch) or 0
    return total + cur

x = zipfile.ZipFile(DOCX).read("word/document.xml").decode()
paras = []
for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
    style = re.search(r'<w:pStyle w:val="([^"]+)"', p)
    text = re.sub(r"<[^>]+>", "", p).strip()
    if text:
        paras.append((style.group(1) if style else "", text))

front, chapters, cur = [], [], None
verse_re = re.compile(r"^([፩-፼]+)\s*[፤፡:፣]\s*(.*)$", re.S)
for style, t in paras:
    m = re.match(r"^ምዕራፍ\s+([፩-፼]+)$", t)
    if m:
        cur = {"chapter": len(chapters) + 1, "printed": m.group(1), "headings": [], "verses": []}
        chapters.append(cur); continue
    if cur is None:
        front.append({"style": style, "text": t}); continue
    v = verse_re.match(t)
    if v:
        cur["verses"].append({"n": geez_num(v.group(1)), "printed": v.group(1), "am": v.group(2)})
    elif cur["verses"]:
        cur["verses"][-1].setdefault("extra", []).append({"style": style, "text": t})
    else:
        cur["headings"].append({"style": style, "text": t})

out = {"front": front, "chapters": chapters}
(HERE / "docx_parsed.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
print(len(front), "front paras;", len(chapters), "chapters;", sum(len(c["verses"]) for c in chapters), "verses")
print("printed chapter number wrong:", [(c["chapter"], c["printed"]) for c in chapters if geez_num(c["printed"]) != c["chapter"]])
for c in chapters:
    ns = [v["n"] for v in c["verses"]]
    bad = [b for a, b in zip([0] + ns, ns) if b != a + 1]
    extra = sum(len(v.get("extra", [])) for v in c["verses"])
    if bad or extra or c["headings"]:
        print("ch", c["chapter"], "verses", len(ns), "jumps", bad[:6], "extra-lines", extra, "headings", [h["text"][:40] for h in c["headings"]])
