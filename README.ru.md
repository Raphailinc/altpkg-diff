# altpkg-diff

[![CI](https://github.com/Raphailinc/altpkg-diff/actions/workflows/ci.yml/badge.svg)](https://github.com/Raphailinc/altpkg-diff/actions/workflows/ci.yml)

[English](README.md) · [Русский](README.ru.md)

Python CLI и библиотека для сравнения бинарных пакетов ALT Linux между ветками. Два списка загружаются параллельно; результат доступен в JSON, кратком тексте и Markdown для GitHub.

## Возможности

- Сравнение пакетов с учётом архитектуры либо только по имени.
- Фильтры архитектуры и регулярного выражения имени пакета.
- JSON, summary и Markdown; `--limit` ограничивает число строк в человекочитаемом отчёте, `0` снимает ограничение.
- `--fail-on-diff` возвращает код `1`, если найдены различия.
- Ограниченное число HTTP-попыток, тайм-ауты, настраиваемый User-Agent и явные ошибки некорректного ответа API.
- Два совместимых CLI-имени: `altpkg-diff` и `package-comparison`.

## Установка и проверка

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
make ci
```

Для использования без средств разработки:

```bash
python -m pip install git+https://github.com/Raphailinc/altpkg-diff.git
```

## Примеры CLI

```bash
# По умолчанию: sisyphus и p10, JSON в stdout.
package-comparison

altpkg-diff sisyphus p10 --format summary
altpkg-diff sisyphus p10 --format markdown --limit 25 -o report.md
altpkg-diff p10 sisyphus --ignore-arch --filter nginx --fail-on-diff
```

`--format json|summary|markdown|text` выбирает формат. `--arch` и `--filter` можно повторять. `--pretty/--no-pretty` управляет JSON. `--timeout` задаёт тайм-аут запроса, `--user-agent` — заголовок, `--debug` включает traceback вместо короткой ошибки. Неизвестная ветка возвращает код `2`, другие ошибки — `1`.

## Использование библиотеки

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
```

Живое сравнение обращается к внешнему API ALT Linux. Для проверки без сети используйте тесты, в которых ответы API подменены.

## HTTP-контракт и конкурентность

`retries` ограничивает общее число попыток вместе с первой: по умолчанию три. Внутренние адаптеры HTTP не умножают этот бюджет. Тайм-ауты, ошибки соединения и 5xx повторяются с экспоненциальной задержкой. Некорректная структура JSON вызывает `AltApiError` и не превращается в пустое сравнение.

Ответы HTTP закрываются при успехе и ошибке. Созданные внутри сессии закрываются автоматически; переданная вызывающим кодом сессия остаётся открытой. Приоритет заголовков: явные `headers`, затем `user_agent`, затем `session.headers`.

По умолчанию списки веток загружаются параллельно. При переданной общей сессии запросы последовательны; для независимых сессий доступны `session_factory` и `allow_concurrency_with_session=True`.

## Навигация по коду

- [compare.py](package_comparison_tool/compare.py) — загрузка, фильтры и сравнение.
- [api.py](package_comparison_tool/api.py) — HTTP-клиент; [cli.py](package_comparison_tool/cli.py) — Click CLI.
- [HTTP-контракт](tests/test_api_contract.py) — число попыток, ошибки входного API, освобождение ресурсов.
- [examples](examples/) — примеры отчётов и конфигурации. Корневые модули сохраняют совместимые импорты.

## Проверки

```bash
python -m pytest
ruff check .
```

GitHub Actions запускает линтеры, тесты и аудит зависимостей на Python 3.11. Лицензия — [MIT](LICENSE).
