from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from core import code_to_graphics, graphics_to_code
from gui.app import run_gui

app = typer.Typer(help="SysML v2 转换工具集 CLI")


@app.command("code-to-graphics")
def code_to_graphics_cmd(
    input_path: Path = typer.Argument(..., help="SysML v2 源文件或文本路径"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="输出图形模型文件路径"),
    raw: bool = typer.Option(False, "--raw", help="将输入视为原始文本而不是文件路径"),
) -> None:
    if raw:
        sysml_text = input_path.read_text()
    else:
        sysml_text = input_path.read_text(encoding="utf-8")

    graphics = code_to_graphics(sysml_text)
    result = output or Path("output-graphics.json")
    result.write_text(str(graphics), encoding="utf-8")
    print(f"[green]已生成图形模型：{result}")


@app.command("graphics-to-code")
def graphics_to_code_cmd(
    input_path: Path = typer.Argument(..., help="图形模型文件路径"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="输出 SysML v2 代码文件路径"),
) -> None:
    graphics_text = input_path.read_text(encoding="utf-8")
    graphics_model = {"content": graphics_text}
    sysml_code = graphics_to_code(graphics_model)
    result = output or Path("output.sysml")
    result.write_text(sysml_code, encoding="utf-8")
    print(f"[green]已生成 SysML v2 代码：{result}")


@app.command("gui")
def gui_cmd() -> None:
    """启动集成 GUI。"""
    print("[blue]正在启动 GUI...")
    run_gui()


if __name__ == "__main__":
    app()
