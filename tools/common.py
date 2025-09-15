import pathlib
import re
import sys
from typing import Any, Dict

import yaml

ROOT = pathlib.Path(".")
REG = ROOT / "registry" / "model" / "v1"
SCHEMAS = ROOT / "registry" / "schemas"


def die(msg: str, code: int = 1):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def load_yaml(p: pathlib.Path):
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_file(*rel):
    p = ROOT.joinpath(*rel)
    if not p.exists():
        die(f"Missing file: {p}")
    return p


def ensure_deps():
    try:
        import jsonschema  # noqa
        import yaml  # noqa
    except Exception:
        die("Please install deps: pip install pyyaml jsonschema", 2)


def compile_pattern(pat: str):
    esc = re.escape(pat)
    regex = re.sub(r"\\{([a-zA-Z0-9_]+)\\}", r"(?P<\1>[^/]+)", esc)
    return re.compile("^" + regex + "$")


def resolve_mapping(topic: str, mapping: Dict[str, Any]):
    exact = []
    patterns = []
    for m in mapping.get("mappings", []):
        if "topic" in m:
            exact.append(m)
        elif "pattern" in m:
            patterns.append(m)
    for m in exact:
        if m["topic"] == topic:
            return m, {}
    for m in patterns:
        rgx = compile_pattern(m["pattern"])
        mobj = rgx.match(topic)
        if mobj:
            return m, mobj.groupdict()
    return None, None
