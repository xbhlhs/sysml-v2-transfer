# SysML v2 Transfer Toolkit

一个用于 SysML v2 代码与图形表示之间双向转换的工具集工作区。

## 功能说明

本项目旨在提供一个简洁的体验，用于在 SysML v2 文本描述与图形模型之间互相转换：

- 从 SysML v2 代码生成图形化模型视图
- 从图形模型数据导出为 SysML v2 代码
- 提供命令行调用接口，支持自动化和脚本化使用
- 提供桌面 GUI 启动入口，便于交互式查看与调试

## 项目结构

- `core/`
  - SysML v2 语法解析
  - 元模型与图形模型实现
  - 转换逻辑与序列化支持
- `cli/`
  - 命令行入口
  - 代码到图形、图形到代码、GUI 启动等命令
- `gui/`
  - 桌面 GUI 应用
  - 与 CLI 集成的交互式视图
- `tests/`
  - 单元测试与功能测试

## 开发说明

### 安装

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

### 运行示例

```bash
python -m cli.main code-to-graphics "example.sysml"
python -m cli.main graphics-to-code "example.json"
python -m cli.main gui
```

### 开发建议

- 先从 `core` 的 SysML v2 文本解析和图形模型序列化开始。
- 以 `cli` 命令和 `gui` 视图为入口，逐步实现双向转换流程。
- 维护 `tests/` 中的测试用例，确保转换逻辑稳定。

## 版本规划

本项目当前处于早期演进阶段，优先级大致如下：

1. 先让 CLI 输出可直接打开的可视化结果
2. 再让 GUI 复现同样的可视化流程
3. 然后补齐最小 SysML v2 语义、视图与导航
4. 再做可视化结果回写为 SysML v2 代码，形成 `1.0.0` 级别的最小闭环
