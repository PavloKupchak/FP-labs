# Лабораторна робота №8. Алгебраїчні типи даних «по-Python'івськи»

## Варіант 7. Результат операції

`Result[T] = Success[T] | Failure` моделює результат обчислення без використання `None` як сигналу помилки. Вузли — незмінні `@dataclass(frozen=True)`, тип результату — `TypeAlias`, код помилки — `Literal`, структурний контракт помилки — `Protocol`, усі операції — чисті функції з `match/case`. Базова модель виразів `Expr = Num | Add | Mul` реалізована за методичкою.

## Склад

- `model.py` — `Success[T]`, `Failure` (з `ErrorCode = Literal[...]`), `Result` і `Protocol` `HasError`.
- `evaluator.py` — операції над `Result`: `map_result`, `flat_map`, `unwrap_or`, `flatten`, `sequence`, `is_success`/`is_failure`, `attempt` (виняток → `Failure`), `statistics`, `count_codes`; безпечні обчислення `parse_int`, `safe_div`, `get_item`, `compute_ratio`, `eval_safe` (вираз повертає `Failure` замість винятку).
- `expr.py` — `Expr = Num | Add | Mul`, альтернативна форма `Bin` з `Literal["+", "*"]` і `Protocol` `SupportsBin`.
- `eval_.py` — `eval_expr` та `eval_expr2` через `match/case`, `EvalOverflow`.
- `pretty.py` — `render` (вирази), `render_result` (результати), `Protocol` `Renders`.
- `main.py` — демонстрація.
- `tests/` — `test_expr.py`, `test_result.py` (включно з property-тестами законів функтора й монади), `test_evaluator.py`, `test_main.py`.

## Структура

```
Lab_08/
  README.md
  model.py
  expr.py
  eval_.py
  evaluator.py
  pretty.py
  main.py
  requirements.txt
  mypy.ini
  pyproject.toml
  .gitignore
  tests/
    __init__.py
    test_expr.py
    test_result.py
    test_evaluator.py
    test_main.py
  report/
    Lab_08.docx
```

## Запуск

```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
pytest -q
mypy --strict .
black --check .
ruff check .
```

## На що звернути увагу

- **`None` не є помилкою.** `Success(None)` — валідний успішний результат; помилку позначає лише `Failure` із кодом із `ErrorCode`.
- **Вичерпність `match`.** `mypy --strict` перевіряє, що всі варіанти `Union` розібрано (для `Bin` оператор розбирається вкладеним `match` по `Literal`), а додавання нового вузла без оновлення функцій видно статично.
- **Чисті функції.** Усі операції повертають нові значення; вузли незмінні й хешовані.
- **Винятки лише на межі.** `attempt` та `code_for` перетворюють виняток обчислення на `Failure`, а решта коду працює з `Result`.
- **Закони.** Property-тести перевіряють закони функтора (тотожність, композиція) та монади (ліва/права тотожність, асоціативність).
