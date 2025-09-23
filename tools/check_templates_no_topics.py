#!/usr/bin/env python3
from common import *

tmpl_dir = pathlib.Path("registry/model/v1/templates")
if not tmpl_dir.exists():
    print("[INFO] No templates directory yet; skipping.")
    raise SystemExit(0)

bad = []
topic_like = re.compile(r"(module/v1/ff/|^ccu/|fts/v1/ff/|/j1/txt/1/)")
for p in tmpl_dir.glob("*.yml"):
    txt = p.read_text(encoding="utf-8")
    if topic_like.search(txt):
        bad.append(p)

if bad:
    print("[ERROR] Found topic strings inside templates (must live in mapping.yml):")
    for p in bad:
        print(f" - {p}")
    sys.exit(1)

print("[OK] No topic strings found inside templates.")
