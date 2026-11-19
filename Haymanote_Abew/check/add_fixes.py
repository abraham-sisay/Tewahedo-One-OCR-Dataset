"""Append fixes to fixes.json from stdin lines: ch|v|old|new|note  (scan label = argv[1]).
"join" as old adds a join fix. "\\n" in new is a verse split."""
import json, sys
from pathlib import Path

sys.stdin.reconfigure(encoding="utf-8")
F = Path(__file__).resolve().parent / "fixes.json"
fixes = json.loads(F.read_text(encoding="utf-8"))
scan = sys.argv[1]
for line in sys.stdin:
    if not line.strip():
        continue
    ch, v, old, new, note = line.rstrip("\n").split("|")
    if old == "join":
        f = {"ch": int(ch), "v": v, "old": "", "new": "", "join": True}
    else:
        f = {"ch": int(ch), "v": v, "old": old, "new": new.replace("\\n", "\n")}
    fixes.append({**f, "scan": scan, "note": note})
F.write_text(json.dumps(fixes, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(len(fixes), "fixes")
