from core import (
    build_graphics_model,
    classify_statement,
    code_to_graphics,
    extract_title,
    graphics_to_code,
    graphics_to_svg,
    render_svg,
    strip_inline_comment,
)
from core.svg import draw_line, draw_rect, draw_text
import xml.etree.ElementTree as ET


def test_code_to_graphics_returns_dict() -> None:
    model = code_to_graphics("package Example {}")
    assert isinstance(model, dict)
    assert model["type"] == "sysml-diagram"
    assert model["nodes"]


def test_graphics_to_code_roundtrip() -> None:
    model = {"content": "package Example {}"}
    code = graphics_to_code(model)
    assert "package Example" in code


def test_graphics_to_svg_contains_svg_root() -> None:
    model = code_to_graphics("package Example {}\npart def A {}")
    svg = graphics_to_svg(model)
    assert svg.startswith("<?xml")
    assert "<svg" in svg
    assert "Example" in svg
    assert "fill=\"#bfdbfe\"" in svg or "fill=\"#dcfce7\"" in svg


def test_layout_helpers_build_expected_graphics_model() -> None:
    assert strip_inline_comment("part def A {} // comment") == "part def A {}"
    assert classify_statement("package Example {}") == "package"
    assert extract_title(["package Example {}", "part def A {}"]) == "Example"

    model = build_graphics_model("package Example {}\npart def A {}")
    assert model["title"] == "Example"
    assert len(model["nodes"]) == 2
    assert len(model["edges"]) == 1
    assert "<svg" in render_svg(model)


def test_svg_structure_snapshot_style() -> None:
    model = build_graphics_model(
        "package Example {}\npart def Vehicle {}\nVehicle -> Engine"
    )
    svg = render_svg(model)
    root = ET.fromstring(svg)
    ns = {"svg": "http://www.w3.org/2000/svg"}
    rects = root.findall(".//svg:rect", ns)
    assert rects[1].attrib["width"] == "520"
    assert rects[2].attrib["width"] != rects[3].attrib["width"]
    relationship_rect = rects[3].attrib
    assert relationship_rect["stroke-dasharray"] == "6 4"
    assert relationship_rect["fill"] == "#f8fafc"


def test_svg_primitives_use_defaults() -> None:
    root = ET.Element("svg")
    rect = draw_rect(root, 10, 20, 100, 40)
    line = draw_line(root, 5, 6, 7, 8)
    text = draw_text(root, 12, 34, "Hello")

    assert rect.attrib["fill"] == "#ffffff"
    assert rect.attrib["stroke"] == "#0f172a"
    assert rect.attrib["stroke-width"] == "1.5"
    assert "stroke-dasharray" not in rect.attrib
    assert line.attrib["stroke"] == "#64748b"
    assert line.attrib["stroke-width"] == "2"
    assert text.attrib["font-family"] == "Arial, sans-serif"
    assert text.attrib["font-size"] == "14"
    assert text.text == "Hello"
