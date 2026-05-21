from core import code_to_graphics, graphics_to_code, graphics_to_svg


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
