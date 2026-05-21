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
    assert "package Example" in svg
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
