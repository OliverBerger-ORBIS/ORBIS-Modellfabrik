#!/usr/bin/env python3
from common import *

mapping_file = find_file("registry","model","v1","mapping.yml")
mapping = load_yaml(mapping_file)

compiled = []
for m in mapping.get("mappings", []):
    if "topic" in m:
        compiled.append(("exact", m["topic"], None, m))
    else:
        rgx = compile_pattern(m["pattern"])
        compiled.append(("pattern", m["pattern"], rgx, m))

errors = 0
exact_topics = [t for kind,t,_,_ in compiled if kind=="exact"]
dups = set([t for t in exact_topics if exact_topics.count(t)>1])
if dups:
    errors += 1
    print("[ERROR] Duplicate exact topics:", ", ".join(sorted(dups)))

for kind,t,rgx,m in compiled:
    if kind!="exact": continue
    hits = 0
    for kind2,pat,rgx2,m2 in compiled:
        if kind2!="pattern": continue
        if rgx2.match(t):
            hits += 1
    if hits>0:
        print(f"[WARN] Exact topic '{t}' is also matched by {hits} pattern(s). Resolution order should prefer exact.")

if errors==0:
    print("[OK] No blocking collisions detected. (Patterns may overlap; exact will win).")
else:
    sys.exit(1)
