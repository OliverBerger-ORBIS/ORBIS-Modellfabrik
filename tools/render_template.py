#!/usr/bin/env python3
from common import *
parser = argparse.ArgumentParser()
parser.add_argument("--topic", required=True)
args = parser.parse_args()

mapping_file = find_file("registry","model","v1","mapping.yml")
mapping = load_yaml(mapping_file)

m, vars = resolve_mapping(args.topic, mapping)
if not m:
    die(f"No mapping match for topic: {args.topic}", 3)

out = {
    "topic": args.topic,
    "template": m["template"],
    "direction": m.get("direction", mapping.get("defaults",{}).get("direction","inbound")),
    "vars": vars,
    "meta": m.get("meta")
}
print(json.dumps(out, indent=2, ensure_ascii=False))
