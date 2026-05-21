# Repository Guidelines

## Project Structure & Module Organization
- `core/` holds the conversion model and bidirectional transform helpers.
- `cli/` contains the Typer command-line entrypoint in `cli/main.py`.
- `gui/` contains the PySide6 desktop shell in `gui/app.py`.
- `tests/` contains pytest-based smoke and round-trip checks.
- `README.md` is the public developer summary; `BACKLOG.md` is the local roadmap.

## Build, Test, and Development Commands
- `python -m pip install -e .` installs the package in editable mode.
- `python -m pip install -e '.[gui]'` adds the GUI dependency (`PySide6`).
- `python -m pip install -e '.[dev]'` adds the development tools (`pytest`, `ruff`).
- `python -m cli.main --help` shows the available CLI commands.
- `python -m cli.main code-to-graphics <file>` converts SysML v2 text to graphics.
- `python -m cli.main graphics-to-code <file>` converts graphics data back to SysML v2.
- `python -m cli.main gui` launches the desktop UI.
- `python -m pytest -q` runs the test suite.

## Coding Style & Naming Conventions
- Target Python 3.11+, use type hints, and keep files ASCII-only unless existing content already uses Unicode.
- Follow PEP 8 spacing and naming: `snake_case` for functions/modules, `PascalCase` for classes, `UPPER_CASE` for constants.
- Prefer small, explicit functions over implicit control flow.
- Keep comments short and only for non-obvious logic.

## Testing Guidelines
- Use `pytest` for all tests.
- Focus tests on public behavior: CLI help, transform shape, and round-trip expectations.
- Name tests `test_<behavior>.py` or `test_<feature>`.
- Add regression coverage for any bug fix that changes CLI, GUI, or conversion behavior.

## Commit & Pull Request Guidelines
- Commit history is short and imperative, e.g. `Initialize ...` or `Update ...`.
- Keep commit subjects brief and action-oriented.
- PRs should include a short summary, verification steps, linked issue(s), and screenshots for GUI-visible changes.
- Call out limitations explicitly, especially around placeholder conversion logic or partial SysML coverage.

## Contributor Notes
- The repository is still a skeleton; keep changes small and incremental.
- Prefer local roadmap updates in `BACKLOG.md` when planning work.
