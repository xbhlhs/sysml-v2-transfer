from pathlib import Path
import xml.etree.ElementTree as ET

from core import (
    build_graphics_model,
    classify_statement,
    code_to_graphics,
    extract_title,
    graphics_to_code,
    graphics_to_svg,
    parse_sysml,
    parse_sysml_events,
    render_svg,
    strip_inline_comment,
)
from core.ast import DefinitionNode, FlowNode, UsageNode
from core.text_layout import wrap_text
from core.svg import DEFAULT_THEME, SVGTheme, draw_line, draw_rect, draw_text


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
    assert "fill=\"#dbeafe\"" in svg or "fill=\"#dcfce7\"" in svg


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
    relationship_rect = rects[3].attrib
    assert relationship_rect["stroke-dasharray"] == "6 4"
    assert relationship_rect["fill"] == "#f8fafc"


def test_svg_primitives_use_defaults() -> None:
    root = ET.Element("svg")
    rect = draw_rect(root, 10, 20, 100, 40)
    line = draw_line(root, 5, 6, 7, 8)
    text = draw_text(root, 12, 34, "Hello")

    assert rect.attrib["fill"] == "#ffffff"
    assert rect.attrib["stroke"] == "#1f2937"
    assert rect.attrib["stroke-width"] == "1.5"
    assert "stroke-dasharray" not in rect.attrib
    assert line.attrib["stroke"] == "#475569"
    assert line.attrib["stroke-width"] == "2"
    assert text.attrib["font-family"] == "Arial, sans-serif"
    assert text.attrib["font-size"] == "14"
    assert text.text == "Hello"


def test_svg_theme_defaults() -> None:
    theme = DEFAULT_THEME

    assert isinstance(theme, SVGTheme)
    assert theme.fill_for_kind("package") == "#dbeafe"
    assert theme.fill_for_kind("relationship") == "#f8fafc"
    assert theme.stroke_for_kind("relationship") == "#64748b"
    assert theme.stroke_width_for_kind("package") == "2"
    assert theme.dasharray_for_kind("relationship") == "6 4"
    assert theme.font_size_for_kind("package") == "16"


def test_layout_filters_syntax_noise() -> None:
    model = code_to_graphics(Path(".local-test/pla.sysml").read_text())
    labels = [node["label"] for node in model["nodes"]]

    assert model["nodes"]
    assert all(node["kind"] != "statement" for node in model["nodes"])
    assert all("flow of" not in label.lower() for label in labels)
    assert all(not label.lower().startswith("from ") for label in labels)
    assert all(not label.lower().startswith("to ") for label in labels)
    assert "doc" not in {label.lower() for label in labels}


def test_doc_blocks_are_preserved_as_metadata() -> None:
    model = code_to_graphics(
        "package Example {\npart def A {\ndoc /* Preserves the semantic note. */\n}\n}"
    )
    node = next(item for item in model["nodes"] if item["kind"] == "definition")
    svg = graphics_to_svg(model)

    assert node["label"] == "A"
    assert node["documentation"] == "Preserves the semantic note."
    assert "<desc>Preserves the semantic note.</desc>" in svg
    assert "Preserves the semantic note." in svg


def test_long_documentation_wraps_to_fit_box() -> None:
    long_doc = (
        "doc /* This description is intentionally long so that the renderer must "
        "wrap it across many lines instead of clipping it before it can overflow "
        "the card frame. */"
    )
    model = code_to_graphics(f"package Example {{\npart def A {{\n{long_doc}\n}}\n}}")
    svg = graphics_to_svg(model)

    assert "..." not in svg
    assert "This description is intentionally long so" in svg
    assert "that the renderer must wrap it across many" in svg
    assert "overflow the card frame." in svg


def test_svg_height_grows_with_long_wrapped_content() -> None:
    model = code_to_graphics(
        "package VeryLongPackageNameThatShouldWrapBecauseItIsMuchLongerThanTheCardWidthExample {}"
    )
    svg = graphics_to_svg(model)
    root = ET.fromstring(svg)
    package = model["nodes"][0]

    assert int(root.attrib["height"]) >= package["y"] + package["height"] + 40


def test_wrap_text_splits_camel_case_words() -> None:
    lines = wrap_text("ProcessLifecycleAgent", 8)

    assert lines == ["Process", "Lifecycle", "Agent"]


def test_wrap_text_keeps_chinese_punctuation_out_of_bad_positions() -> None:
    lines = wrap_text("这是一个测试，看看标点（是否正确）以及结束。", 6)

    assert lines
    assert all(not line.startswith(("，", "。", "】", "）", "》", "：", "、")) for line in lines)
    assert all(not line.endswith(("（", "【", "《", "（", "：")) for line in lines)


def test_package_height_grows_for_long_camel_case_title() -> None:
    model = code_to_graphics(
        "package VeryLongPackageNameThatShouldWrapBecauseItIsMuchLongerThanTheCardWidthExample {}"
    )

    package = model["nodes"][0]
    assert package["kind"] == "package"
    assert package["height"] > 76


def test_parser_builds_ast_for_pla_model() -> None:
    document = parse_sysml(Path(".local-test/pla.sysml").read_text())
    assert document.package is not None
    assert document.package.name == "AirborneSoftwarePLA"

    definitions = [member for member in document.package.members if isinstance(member, DefinitionNode)]
    pla = next(member for member in definitions if member.name == "ProcessLifecycleAgent")
    ports = [member for member in pla.members if isinstance(member, UsageNode) and member.keyword == "port"]
    parts = [member for member in pla.members if isinstance(member, UsageNode) and member.keyword == "part"]
    flows = [member for member in pla.members if isinstance(member, FlowNode)]

    assert pla.documentation.startswith("Represents the core PLA component")
    assert {port.name for port in ports} >= {"constraintIn", "daRequestOut", "daResponseIn", "evidenceOut"}
    assert {part.name for part in parts} >= {"perception", "decision", "execution", "correction", "stability"}
    assert len(flows) == 12
    assert flows[0].item_type == "ConstraintInput"
    assert flows[0].source == "constraintIn"
    assert flows[0].target == "perception.constraintIn"


def test_parser_exposes_events_for_pla_model() -> None:
    events = parse_sysml_events(Path(".local-test/pla.sysml").read_text())
    kinds = [event.kind for event in events]
    flow_events = [event for event in events if event.kind == "flow"]

    assert kinds[0] == "enter_package"
    assert kinds.count("enter_definition") == 18
    assert kinds.count("usage") == 34
    assert len(flow_events) == 16
    assert flow_events[0].item_type == "ConstraintInput"
    assert flow_events[0].source == "constraintIn"
    assert flow_events[0].target == "perception.constraintIn"


def test_graphics_model_uses_ast_for_pla_model() -> None:
    model = code_to_graphics(Path(".local-test/pla.sysml").read_text())
    labels = {node["label"] for node in model["nodes"]}
    flow_nodes = [node for node in model["nodes"] if node["kind"] == "relationship"]

    assert model["title"] == "AirborneSoftwarePLA"
    assert "ProcessLifecycleAgent" in labels
    assert "perception" in labels
    assert "airborneSystem" in labels
    assert len(flow_nodes) == 16
    assert all("flow of" not in node["label"].lower() for node in flow_nodes)
    assert any(node["secondary_label"] == "constraintIn -> perception.constraintIn" for node in flow_nodes)
