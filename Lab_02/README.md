# Лабораторна робота №2. Функції вищого порядку, lambda, композиція

## Варіант 7. Аналіз товарів складу

Конвеєр над списком товарів (`id`, `name`, `category`, `price`, `stock`) без мутацій вхідних даних: нормалізація назв, відбір за запасом, обчислення вартості запасу (`value = price × stock`), коефіцієнт вибраної категорії, сортування за `value` спадно та `id` зростаюче, Top-N. Агрегація через `reduce`: `count`, `inventory_value`, `avg_value`.

## Склад

- `core.py` — чисті функції: `compose` (справа наліво), `pipe` (зліва направо), `juxt`, `take`; кроки складу `normalize_item_names`, `only_in_stock`, `with_value`, `boost_category`, `apply_category_factors`, `sort_by_value_desc`, `reduce_inventory_stats`, конвеєри `process_inventory` та `build_inventory_pipeline`; з базового завдання — `only_adults`, `with_total`, `boost_city`, `normalize_names`, `sort_by_total_desc`, `reduce_stats`, `build_pipeline`.
- `app.py` — оболонка вводу-виводу: читання `sample_data.json`, аргументи командного рядка, звіт.
- `main.py` — точка входу.
- `sample_data.json` — приклад вхідних даних.
- `tests/` — `test_core.py`, `test_app.py`, `test_properties.py`, `test_main.py`.

## Структура

```
Lab_02/
  README.md
  core.py
  app.py
  main.py
  sample_data.json
  requirements.txt
  mypy.ini
  pyproject.toml
  .gitignore
  tests/
    __init__.py
    test_core.py
    test_app.py
    test_properties.py
    test_main.py
  report/
    Lab_02.docx
```

## Запуск

```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python main.py --top 3 --boost-category Electronics --factor 1.1 --min-stock 1
mypy .
black --check .
ruff check .
```

Параметри: `--data` (шлях до JSON), `--top` (N), `--boost-category`, `--factor`, `--min-stock`.

## На що звернути увагу

- **Без мутацій.** Кожен крок повертає нові словники (`{**r, ...}`), вхідний список лишається незмінним.
- **Лінивість.** Кроки `filter`/`map` — генераторні вирази; матеріалізація відбувається у `sorted` і `take`.
- **Порядок композиції.** `compose` застосовує функції справа наліво, `pipe` — зліва направо; тести перевіряють, що вони дзеркальні.
- **Чисте ядро.** Увесь ввід-вивід (файл, `argparse`, друк) знаходиться в `app.py` і `main.py`, а `core.py` не має побічних ефектів.
- **Сортування з двома ключами.** `value` спадно, `id` зростаюче: однакова вартість не дає нестабільного порядку.
