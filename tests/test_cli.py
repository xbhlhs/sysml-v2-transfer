from typer.testing import CliRunner

from cli.main import app


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SysML v2 转换工具集 CLI" in result.output


def test_cli_code_to_graphics_writes_svg(tmp_path) -> None:
    input_file = tmp_path / "example.sysml"
    output_file = tmp_path / "diagram.svg"
    input_file.write_text("package Example {}\npart def A {}", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["code-to-graphics", str(input_file), "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    svg = output_file.read_text(encoding="utf-8")
    assert "<svg" in svg
    assert "Example" in svg


def test_cli_code_to_graphics_raw_text(tmp_path) -> None:
    output_file = tmp_path / "diagram.svg"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "code-to-graphics",
            "package Example {}\npart def A {}",
            "--raw",
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    svg = output_file.read_text(encoding="utf-8")
    assert "Example" in svg


def test_cli_code_to_graphics_reports_missing_input(tmp_path) -> None:
    output_file = tmp_path / "diagram.svg"

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["code-to-graphics", str(tmp_path / "missing.sysml"), "--output", str(output_file)],
    )

    assert result.exit_code != 0
    assert "输入文件不存在" in result.output
    assert not output_file.exists()


def test_cli_code_to_graphics_creates_output_parent(tmp_path) -> None:
    input_file = tmp_path / "example.sysml"
    output_file = tmp_path / "nested" / "diagram.svg"
    input_file.write_text("package Example {}\npart def A {}", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["code-to-graphics", str(input_file), "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert "<svg" in output_file.read_text(encoding="utf-8")
