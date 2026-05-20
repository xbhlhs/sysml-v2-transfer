from typer.testing import CliRunner

from cli.main import app


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SysML v2 转换工具集 CLI" in result.output
