from core import code_to_graphics, graphics_to_code


def test_code_to_graphics_returns_dict() -> None:
    model = code_to_graphics("package Example {}")
    assert isinstance(model, dict)
    assert model["type"] == "sysml-diagram"


def test_graphics_to_code_roundtrip() -> None:
    model = {"content": "package Example {}"}
    code = graphics_to_code(model)
    assert "package Example" in code
