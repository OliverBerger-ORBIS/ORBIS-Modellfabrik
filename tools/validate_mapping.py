#!/usr/bin/env python3
import json

from common import *

ensure_deps()
from jsonschema import validate

mapping_file = find_file("registry", "model", "v1", "mapping.yml")
schema_file = find_file("registry", "schemas", "mapping.schema.json")

mapping = load_yaml(mapping_file)
schema = json.loads(schema_file.read_text(encoding="utf-8"))

validate(instance=mapping, schema=schema)
print("[OK] mapping.yml validated against mapping.schema.json")
