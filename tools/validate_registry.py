#!/usr/bin/env python3
from common import *
ensure_deps()
from jsonschema import validate

def vfile(path_parts, schema_name):
    f = find_file(*path_parts)
    schema = json.loads(find_file("registry","schemas",schema_name).read_text(encoding="utf-8"))
    data = load_yaml(f)
    validate(instance=data, schema=schema)
    print(f"[OK] {f} valid")

vfile(("registry","model","v1","modules.yml"), "modules.schema.json")
vfile(("registry","model","v1","enums.yml"), "enums.schema.json")
wp = pathlib.Path("registry/model/v1/workpieces.yml")
if wp.exists():
    schema = json.loads(find_file("registry","schemas","workpieces.schema.json").read_text(encoding="utf-8"))
    data = load_yaml(wp)
    validate(instance=data, schema=schema)
    print(f"[OK] {wp} valid")

print("[INFO] For mapping.yml use: make validate-mapping")
