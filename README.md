# SysML v2 Transfer Toolkit

一个用于将 SysML v2 textual notation 转成可视化视图的工具集。

## 概览

本项目的目标是把同一份 SysML v2 模型数据，逐步投影成多种视图，先从 Definition View 开始，再扩展到其他常见视图。

当前重点：

- 从 SysML v2 文本生成 Definition View
- 保持命令行方式可用，便于脚本化和批处理
- 保持桌面 GUI 入口可用，便于交互式查看

后续计划：

- Usage View
- Connection / Interconnection View
- Action Flow View
- Interaction View
- State View
- Requirement View
- 在视图稳定后，再考虑回写链路

## 安装

普通安装：

```bash
python -m pip install -e .
```

GUI 安装：

```bash
python -m pip install -e '.[gui]'
```

开发安装：

```bash
python -m pip install -e '.[dev]'
```

## 使用

```bash
python -m cli.main code-to-graphics "example.sysml"
python -m cli.main graphics-to-code "example.json"
python -m cli.main gui
```

### 命令说明

- `code-to-graphics`：将 SysML v2 文本导出为可视化文件
- `graphics-to-code`：将图形结果回写为 SysML v2 代码
- `gui`：打开桌面 GUI

## 路线图

1. `1.0.0 (Apollo)`：从 texture notation 生成 Definition View
2. `1.1.x`：GUI 复现 Definition View 的可视化流程
3. `1.2.x` / `2.x.x`：补齐更多视图投影
4. 更后续阶段：视图稳定后，再推进回写与更完整的双向转换闭环

## 许可证

仓库根目录默认采用 Apache-2.0；`core/` 和 `cli/` 采用 MIT；`gui/` 继续采用 Apache-2.0。具体以各目录内的 `LICENSE` 文件为准。
