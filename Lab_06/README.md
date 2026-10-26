# Лабораторна робота №6. Замикання та декоратори як HOF

## Варіант 7. Кешування результатів пошуку

Пошук документів кешується з нормалізацією запиту. Запити `"Python"`, `"  python  "` і `"the PYTHON"` дають один запис кешу, бо ключ будується із замикання-нормалізатора. Записи можна інвалідувати за предикатом, є TTL, а час вимірюється лише для справжніх (не кешованих) пошуків.

## Склад

- `closures.py` — замикання: `make_counter` (стан через `nonlocal`), `make_logger`, `make_normalizer` (регістр, пробіли, стоп-слова), `make_query_key` (ключ кешу).
- `decorators.py` — параметризовані декоратори з `functools.wraps`, `ParamSpec` і `TypeVar`: `timed` (clock/logger), `retries` (sleep/rand/logger, backoff, jitter), `cached` (TTL, `key_fn`, `cache_clear`, `cache_invalidate`, `cache_info`).
- `search.py` — `Document`, `search_documents` і `make_search_service`, що збирає `cached(timed(search))`.
- `main.py` — демонстрація.
- `tests/` — `test_closures.py`, `test_timed.py`, `test_retries.py`, `test_cached.py`, `test_search.py`, `test_composition.py`, `test_main.py`.

## Структура

```
Lab_06/
  README.md
  closures.py
  decorators.py
  search.py
  main.py
  requirements.txt
  mypy.ini
  pyproject.toml
  .gitignore
  tests/
    __init__.py
    test_closures.py
    test_timed.py
    test_retries.py
    test_cached.py
    test_search.py
    test_composition.py
    test_main.py
  report/
    Lab_06.docx
```

## Запуск

```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
pytest -q
mypy .
black --check .
ruff check .
```

## На що звернути увагу

- **Залежності передаються ззовні.** `clock`, `sleep`, `rand`, `logger`, `time_fn` і `key_fn` ін'єктуються як `Callable`, тому в тестах немає реальних затримок і часу.
- **Порядок декораторів.** Декоратори застосовуються знизу вгору. У `make_search_service` `timed` стоїть під `cached`, тож лог часу з'являється лише при промаху кешу; у `test_composition.py` показано різницю з протилежним порядком.
- **Ключ кешу.** Аргументи мають бути хешованими; для нормалізованих запитів використовується власний `key_fn`. Список як аргумент дає `TypeError`.
- **Метадані.** `__name__`, `__doc__` і `__wrapped__` зберігаються після декорування в усіх декораторах.
- **Потокобезпека.** Доступ до кешу захищений `threading.Lock`; значення обчислюється поза блокуванням.
