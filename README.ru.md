![CI](https://github.com/Raphailinc/altpkg-diff/actions/workflows/ci.yml/badge.svg)
![Coverage](https://raw.githubusercontent.com/Raphailinc/altpkg-diff/main/badges/coverage.svg)

# altpkg-diff

CLI and library for diffing ALT Linux binary packages between branches. Fetches both branches in parallel with retries and outputs JSON, human-readable summaries, or GitHub-ready Markdown.

## Highlights
- JSON, summary, and Markdown outputs; `--limit` keeps human output compact (set `0` for unlimited).
- Filters: architectures (`--arch`), regex by package name (`--filter`), and name-only comparison (`--ignore-arch`).
- CI-friendly: `--fail-on-diff` exits with code `1` when differences are found.
- Resilient HTTP client with retries, timeouts, and customizable `--user-agent` (honored even with custom sessions).
- New CLI alias `altpkg-diff` (keeps `package-comparison` for compatibility).
- Cleaner CLI errors: short messages by default; `--debug` shows tracebacks. Exit code `2` for missing branches, `1` for other failures.

## Quickstart
```bash
python -m pip install -e .[dev] && make ci
```
Запускает линтеры и тесты. Для простого использования без разработки можно установить пакетом:
```bash
pip install git+https://github.com/Raphailinc/altpkg-diff.git
```

## CLI usage
```bash
# defaults: sisyphus vs p10, JSON to stdout
package-comparison

# same tool via shorter alias
altpkg-diff sisyphus p10 --format summary

# GitHub-ready Markdown report (first 25 rows shown) saved to file
package-comparison sisyphus p10 --format markdown --limit 25 -o report.md

# CI mode: fail on any differences, ignore arch suffixes, filter only nginx packages
package-comparison p10 sisyphus --ignore-arch --filter nginx --fail-on-diff
```

Key options:
- `--format json|summary|markdown|text` – choose output format (JSON honors `--pretty/--no-pretty`).
- `--filter REGEX` – repeatable regex for package names (case-insensitive).
- `--arch ARCH` – repeatable arch filter; `--ignore-arch` compares by name only.
- `--limit N` – limit rows in human-readable formats (Markdown/summary); `0` shows everything.
- `--fail-on-diff` – exit with code `1` when differences exist (useful for CI/pipelines).
- `--timeout`, `--user-agent`, `--debug` – tune HTTP behavior and verbosity on errors.

## Library use
```python
from package_comparison_tool.compare import compare_packages

result = compare_packages(
    "sisyphus",
    "p10",
    ignore_arch=False,
    arches={"x86_64", "noarch"},
    name_patterns=None,
)

print(result["stats"])
# {'only_in_branch1': ..., 'differences': ...}
```

## API samples
```bash
# JSON diff (first 5 rows)
altpkg-diff p10 sisyphus --format json --limit 5 | head

# Markdown report, name-only comparison
altpkg-diff sisyphus p10 --ignore-arch --format markdown -o report.md

# CI pipeline example (GitHub Actions step)
pip install -e .[dev]
pytest --cov=package_comparison_tool
```

## HTTP & concurrency
- Built-in retries for timeouts/connection errors/5xx with exponential backoff; per-request timeouts (`--timeout`) and per-call user agent override (`--user-agent`).
- Sessions created internally are closed automatically; caller-provided sessions are never closed.
- Header precedence (per request): explicit `headers` > `user_agent` value > `session.headers` (so custom UAs are honored even with custom sessions).
- Parallel fetches by default; if you supply a session, calls run sequentially for safety. Provide `session_factory` or `allow_concurrency_with_session=True` to fetch with two cloned/independent sessions.

## Architecture
- `package_comparison_tool/compare.py` — основная логика скачивания/сравнения RPM списков.
- `cli.py` / `api.py` — CLI и FastAPI-lite интерфейс.
- `examples/` — примеры готовых отчётов и конфигов.
- `tests/` — unit-тесты на респонсы/фильтры.

## Quality
- Форматирование/линт: `ruff check .`
- Тесты: `pytest`
- CI: GitHub Actions (`ci.yml`) — линтер + тесты на Python 3.11.

## Development
- Run tests: `pytest`
- Lint: `ruff check .`

## License
MIT – see [LICENSE](LICENSE).
