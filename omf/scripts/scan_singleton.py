import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DASH = ROOT / "omf" / "omf" / "dashboard"

viol = 0

# 1) verbotene Instanzen in Dashboard
pat = re.compile(r"\b(OmfMqttClient|mqtt\.Client)\s*\(")
for py in DASH.rglob("*.py"):
    s = py.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(s.splitlines(), 1):
        if pat.search(line):
            print(f"[ERROR] Client-Instanzierung in {py}:{i} :: {line.strip()}")
            viol += 1

# 2) st.rerun in Dashboard
pat2 = re.compile(r"\bst\.rerun\s*\(")
for py in DASH.rglob("*.py"):
    s = py.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(s.splitlines(), 1):
        if pat2.search(line.replace(" ", "")):
            print(f"[ERROR] st.rerun() in {py}:{i} :: {line.strip()}")
            viol += 1

# 3) mehrfaches basicConfig im Projekt
bc = 0
for py in ROOT.rglob("*.py"):
    s = py.read_text(encoding="utf-8", errors="ignore")
    if "basicConfig(" in s:
        bc += 1
        print(f"[INFO] basicConfig in {py}")

if bc > 1:
    print(f"[WARN] {bc}x basicConfig() gefunden – ideal ist 1x.")

sys.exit(1 if viol else 0)
