# Лабораторна робота №3. Нездатні до змін структури даних (immutability) у Python

## Варіант 7. Прокат автомобілів

Предметна модель (автомобіль і оренда з опціями та метаданими) переведена на незмінні структури. Усі зміни стану виконуються як pure updates: функції повертають нові об'єкти й не змінюють вхідні.

## Незмінна модель (`model.py`)

- `Car`, `Rental`, `Order` — `@dataclass(frozen=True, slots=True)`.
- `Option`, `Item` — `NamedTuple`.
- Опції оренди та характеристики авто — `frozenset`; історія статусів і позиції замовлення — `tuple`.
- Метадані — `MappingProxyType` над копією словника (`make_meta`); поле `meta` не бере участі в хешуванні (`hash=False`), тому всі сутності хешовані й підходять як ключі `dict` та елементи `set`.

## Pure-оновлення (`core.py`)

`add_option`, `remove_option`, `extend_rental`, `change_status`, `update_meta`, `add_feature` (через `dataclasses.replace`, операції `frozenset` і конкатенацію `tuple`); розрахунки `rental_total`, `total_with_discount`, `cached_rental_total` (`lru_cache`); глибоке заморожування `freeze`; функції базового домену `add_vip_tag`, `add_item`, `top_expensive_items`, `source`.

## Структура

```
Lab_03/
  README.md
  model.py
  core.py
  mypy.ini
  pyproject.toml
  requirements.txt
  tests/
    __init__.py
    conftest.py
    test_immutability.py
    test_performance.py
  report/
    Lab_03.docx
```

## Запуск

```
pip install -r requirements.txt
pytest -q --durations=5
mypy .
black --check .
ruff check .
```

## Висновок про незмінність

Переваги: немає прихованих змін стану, тести прості (порівняння з еталонним екземпляром), сутності хешовані, а тому працюють як ключі й з `lru_cache`; `frozen`-класи та `MappingProxyType` захищають дані на рівні мови.

Накладні витрати: кожне оновлення створює новий об'єкт. У мікробенчмарку `tests/test_performance.py` (5000 оренд, по три оновлення на кожну) мутабельний варіант виконався за ≈0.008 с, незмінний — за ≈0.115 с, тобто приблизно в 14 разів повільніше. В абсолютних числах це ≈23 мкс на ланцюжок оновлень, що для бізнес-логіки несуттєво. Час усього набору тестів при цьому лишається близько 2–3 с (`pytest --durations=5`).
