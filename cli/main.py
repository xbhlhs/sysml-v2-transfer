"""SPDX-FileCopyrightText: 2026 xbhlhs
SPDX-License-Identifier: MIT"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich import print

from core import code_to_graphics, graphics_to_code, graphics_to_svg
from gui.app import run_gui

app = typer.Typer(help="SysML v2 转换工具集 CLI")


@app.command("code-to-graphics")
def code_to_graphics_cmd(
    input_value: str = typer.Argument(..., help="SysML v2 源文件路径或原始文本"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="输出 SVG 可视化文件路径"),
    raw: bool = typer.Option(False, "--raw", help="将输入视为原始文本而不是文件路径"),
) -> None:
    if raw:
        sysml_text = input_value
    else:
        input_path = Path(input_value)
        if not input_path.exists():
            raise typer.BadParameter(f"输入文件不存在：{input_path}")
        if not input_path.is_file():
            raise typer.BadParameter(f"输入路径不是文件：{input_path}")
        try:
            sysml_text = input_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise typer.BadParameter(f"无法读取输入文件：{input_path}") from exc

    try:
        graphics = code_to_graphics(sysml_text)
        svg = graphics_to_svg(graphics)
    except Exception as exc:
        raise typer.BadParameter(f"转换失败：{exc}") from exc

    result = output or _default_svg_output_path(input_value, raw=raw)
    try:
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(svg, encoding="utf-8")
    except OSError as exc:
        raise typer.BadParameter(f"无法写入输出文件：{result}") from exc
    print(f"[green]已生成 SVG 可视化：{result}")


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


def _default_svg_output_path(input_value: str, *, raw: bool) -> Path:
    if raw:
        return Path("output-graphics.svg")
    input_path = Path(input_value)
    return input_path.with_name(f"{input_path.stem}-def-view.svg")


if __name__ == "__main__":
    app()
