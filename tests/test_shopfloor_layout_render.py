import json
from pathlib import Path

from examples.shopfloor_test_app import route_utils
from examples.shopfloor_test_app.app import render_shopfloor_svg

HERE = Path(__file__).parent
LAYOUT_PATH = Path("examples/shopfloor_test_app/shopfloor_layout.json")


def test_layout_file_exists():
    assert LAYOUT_PATH.exists(), "layout json missing"


def test_render_contains_component_names():
    layout = json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))
    svg = render_shopfloor_svg(layout)
    # ensure important module names appear in svg tooltips
    assert "DRILL" in svg or "DRILL" in svg, "DRILL name missing in SVG"
    assert "COMPANY" in svg, "COMPANY missing in SVG"
    assert "INTERSECTION-1" in svg or "1" in svg, "Intersection label missing"


def test_route_utils_basic_path():
    layout = json.loads(LAYOUT_PATH.read_text(encoding="utf-8"))
    g = route_utils.build_graph(layout)
    # Ensure some expected connections exist
    assert "1" in g
    assert "2" in g
    # find a path between intersection 1 and 2
    p = route_utils.find_path(g, "1", "2")
    assert p and isinstance(p, list), "find_path returned empty or non-list"
