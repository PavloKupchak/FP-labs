# Лабораторна робота №5. Ліниві обчислення: генератори та itertools

## Варіант 7. Сенсорні дані IoT

Нескінченний потік значень датчика обробляється лінивим конвеєром: відкидається початковий шум (`dropwhile`), беруться значення до аварійного порога (`takewhile`), результат ділиться на пакети фіксованого розміру (`chunked`). Значення обчислюються лише в міру запиту, нескінченні потоки завжди обмежені.

## Склад

- `streams.py` — `fib_stream`, `naturals`, `take`, `drop`, `sliding_window`, `moving_average`, `chunked`, обгортки `prefix_sums`, `prefix_products`, `running_max`, `take_while`, `drop_while`; для варіанта 7: `sensor_stream` (постачальник значень через `Callable`), `simulated_sensor`, `drop_noise`, `until_alarm`, `process_sensor`, `summarize_batches`.
- `main.py` — демонстрація: перші елементи, віконні суми, рухоме середнє, конвеєр датчика, порівняння пам'яті.
- `tests/` — `test_fib_stream.py`, `test_take_drop.py`, `test_sliding_window.py`, `test_accumulate.py`, `test_laziness.py`, `test_iot.py`, `test_main.py`.
- `ASSIGNMENT.md` — формулювання завдання та критерії.

## Структура

```
Lab_05/
  README.md
  ASSIGNMENT.md
  streams.py
  main.py
  requirements.txt
  mypy.ini
  pyproject.toml
  .gitignore
  tests/
    __init__.py
    test_fib_stream.py
    test_take_drop.py
    test_sliding_window.py
    test_accumulate.py
    test_laziness.py
    test_iot.py
    test_main.py
  report/
    Lab_05.docx
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

- **Лінивість.** Тести `test_laziness.py` і `test_iot.py` лічильником звернень підтверджують, що з джерела витягнуто рівно стільки елементів, скільки запитано (наприклад, `take(4, ...)` читає 4 значення, перший пакет конвеєра датчика читає лише шум і сам пакет).
- **Нескінченні послідовності.** `fib_stream`, `naturals`, `sensor_stream` ніколи не матеріалізуються повністю: їх обмежують `take`/`islice`, `takewhile` або аварійний поріг.
- **Вичерпаність генераторів.** Генератор можна пройти лише один раз, тому конвеєр створюється заново для кожного споживача.
- **Помилки розміру.** `sliding_window`, `moving_average` і `chunked` одразу (до першого елемента) відхиляють розмір ≤ 0.
- **Пам'ять.** Список із 100 000 чисел займає ≈ 800 КБ, а генераторний вираз — ≈ 200 байт.
