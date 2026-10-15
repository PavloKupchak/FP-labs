# Лабораторна робота №1. Основи функціонального програмування у Python

## Варіант 7. Облік електроенергії

За попереднім і поточним показниками лічильника та тарифною групою обчислюється спожита енергія (кВт·год) і сума до оплати. Записи з показником, що зменшився, ігноруються. Тариф, пільга та фільтр мінімального споживання передаються як `typing.Callable`. Вхідні дані не змінюються, результат містить нові записи з полями `consumption` та `amount`. Друк квитанцій винесено в `app.py`.

## Структура

```
lab01/
  README.md
  core.py
  app.py
  tests/
    conftest.py
    test_core.py
  requirements.txt
  pytest.ini
  mypy.ini
```

- `core.py` — чисте ядро: `consumption_of`, `is_valid_reading`, `with_bill`, `make_flat_tariff`, `make_group_benefit`, `make_min_consumption_filter`, `make_processor` (фабрика обробника), `process_readings_pure`, `compose`, `make_multiplier`, `stamp_amount`.
- `app.py` — оболонка побічних ефектів (`render_receipt`, `render_report`, `print`).
- `tests/test_core.py` — тести референтної прозорості, відсутності мутацій і Callable-політик.

## Запуск

```
pip install -r requirements.txt
python app.py
pytest
mypy core.py app.py tests
black --check .
ruff check .
```
