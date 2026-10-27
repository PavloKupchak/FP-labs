# Лабораторна робота №7. functools та operator

## Варіант 7. Готельні бронювання

Записи бронювань (`guest`, `nights`, `room_type`, `price`, `status`) завантажуються з JSON чи CSV, нормалізуються, для них обчислюється `total_price` за тарифом, відбираються підтверджені та формується Top-N за вартістю. Конвеєр побудований на `functools.partial` і `functools.reduce` без явних циклів; поліморфний завантажувач реалізовано через `functools.singledispatch`, порядок бронювань задано через `functools.total_ordering`.

## Склад

- `core.py` — `pipeline` (через `reduce`), `mapf`/`filt` (через `partial`), `multisort` (стабільні проходи по критеріях), `take_n`, тарифи `high_season`/`low_season` (`partial(apply_tariff, ...)`), фільтри `confirmed` та `at_least`, `top_bookings`; з базового завдання — `clean_and_rank` і `sort_products`.
- `loaders.py` — `load_bookings` та `load_users` на `@singledispatch` для `str` (JSON, CSV або шлях), `pathlib.Path`, відкритого текстового файлу (`io.TextIOBase`) та готового `list`.
- `models.py` — `Booking` (порядок за `total_price`, `nights`, `guest`) і `Box` (об'єм, площа фронтальної грані, `w`) з `@total_ordering`; для чужих типів повертається `NotImplemented`.
- `main.py` — демонстрація, `sample_data.json`, `sample_data.csv` — зразки даних.
- `tests/test_lab07.py` — тести `pipeline`, `partial`, `operator`, `singledispatch`, сортування та всіх операторів порівняння.

## Структура

```
Lab_07/
  README.md
  core.py
  loaders.py
  models.py
  main.py
  sample_data.json
  sample_data.csv
  requirements.txt
  mypy.ini
  pyproject.toml
  .gitignore
  tests/
    __init__.py
    test_lab07.py
  report/
    Lab_07.docx
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

- **Однаковий результат для всіх джерел.** JSON-рядок, CSV-рядок, шлях (`str` і `Path`), відкритий файл і список словників дають однакові записи; список копіюється, вхідні дані не змінюються.
- **Диспетчеризація лише за першим аргументом.** Невідомий тип (наприклад, `int`) дає `TypeError`, некоректний вміст списку або JSON — `ValueError`.
- **`reduce` і початкове значення.** `pipeline` і `multisort` коректно працюють на порожніх вхідних даних.
- **Сортування «за зростанням і за спаданням».** `multisort` застосовує стабільні проходи з `itemgetter` від останнього критерію до першого, тому змішані напрямки (`total_price` ↓, `guest` ↑) працюють без хитрощів із ключем.
- **`total_ordering`.** Достатньо `__eq__` і `__lt__`; решта операторів (`<=`, `>`, `>=`) добудовує декоратор. `__hash__` узгоджений з `__eq__`.
