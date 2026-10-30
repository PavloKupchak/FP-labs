# Лабораторна робота №1. Основи функціонального програмування у Python

## Варіант 7. Облік електроенергії

За попереднім і поточним показниками лічильника та тарифною групою обчислюється спожита енергія (кВт·год) і сума до оплати. Записи з показником, що зменшився, ігноруються. Тариф, пільга та фільтр мінімального споживання передаються як `typing.Callable`. Вхідні дані не змінюються, результат містить нові записи з полями `consumption` та `amount`. Читання даних і друк квитанцій винесено в `app.py`.

## Структура

```
Lab_01/
  README.md
  core.py
  app.py
  main.py
  readings.json
  pyproject.toml
  requirements.txt
  tests/
    __init__.py
    conftest.py
    test_core.py
    test_app.py
    test_orders.py
    test_main.py
    test_properties.py
  report/
    Lab_01.docx
```

- `core.py` — чисте ядро: `consumption_of`, `is_valid_reading`, `with_bill`, `make_flat_tariff`, `make_group_benefit`, `make_min_consumption_filter`, `make_reading_processor` (фабрика обробника), `process_readings_pure`, `compose`, `identity`, `make_multiplier`, `stamp_amount`; а також функції базового завдання `order_subtotal`, `with_total`, `make_processor`, `process_orders_pure`.
- `main.py` — точка входу: запускає `app.main` на `readings.json`.
- `app.py` — оболонка побічних ефектів: читання `readings.json`, формування та друк квитанцій.
- `tests/test_core.py` — референтна прозорість, відсутність мутацій, Callable-політики.
- `tests/test_orders.py` — тести базового завдання (замовлення).
- `tests/test_app.py` — тести оболонки (читання файлу, звіт, друк).
- `tests/test_properties.py` — property-тести на hypothesis.

## Запуск

```
pip install -r requirements.txt
python main.py
pytest
mypy .
black --check .
ruff check .
```
