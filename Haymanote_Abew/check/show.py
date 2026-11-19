"""usage: show.py <chapter> [from_verse] [to_verse] - print docx_parsed verses for comparing with the scan."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads((Path(__file__).parent / "docx_parsed.json").read_text(encoding="utf-8"))
c = d["chapters"][int(sys.argv[1]) - 1]
a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
b = int(sys.argv[3]) if len(sys.argv) > 3 else 999
print("ch", c["chapter"], "printed", c["printed"], [h["text"] for h in c["headings"]])
for v in c["verses"]:
    if a <= v["n"] <= b:
        print(f'{v["printed"]}| {v["am"]}')
        for e in v.get("extra", []): print("   +", e["text"])
