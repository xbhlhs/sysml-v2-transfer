# SysML v2 Transfer Toolkit

一个用于 SysML v2 代码与图形表示之间双向转换的工具集工作区。

## 目标

- `core`：实现 SysML v2 语法、元模型、图形模型和转换逻辑。
- `cli`：提供命令行接口，支持代码转图形、图形转代码、集成 GUI 启动等。
- `gui`：基于桌面 GUI 的交互式视图，与 CLI 集成以实现统一工具体验。

## 初始结构

- `core/`
- `cli/`
- `gui/`
- `tests/`

## 安装

```bash
python -m pip install -e .
python -m pip install -e .[gui]
```

## 运行

```bash
python -m cli.main code-to-graphics "example.sysml"
python -m cli.main graphics-to-code "example.json"
python -m cli.main gui
```

## 开发建议

- 先从 `core` 的 SysML v2 文本解析和图形模型序列化开始。
- 以 `cli` 命令和 `gui` 视图为入口，逐步实现双向转换流程。
