# Лабораторна робота №4. Рекурсія та мемоізація в Python

## Варіант 7. Файлова ієрархія як дерево

Каталог моделюється як незмінне дерево (`FileNode`, `DirNode`). Реалізовано рекурсивний підрахунок файлів і сумарного розміру, висоти дерева, DFS і BFS. Для кожної рекурсивної операції є ітеративна версія з власним стеком чи чергою. Дерево не змінюється під час обходів.

## Склад

- `algorithms.py` — базові алгоритми: `quicksort` (випадковий pivot, повертає новий список), бінарне дерево `Node` з обходами `preorder`/`inorder`/`postorder`, ітеративні `bfs_level_order` та `dfs_preorder_iter`, `fib` (`@lru_cache`), `fib_naive`, `fib_iter`, `fact` та `fact_iter`.
- `filetree.py` — варіант 7: `count_files`, `total_size`, `tree_height`, `walk_files` (рекурсивний DFS), `iter_files`, `walk_files_bfs`, `count_files_iter`, `total_size_iter`, `tree_height_iter`.
- `main.py` — демонстрація роботи.
- `tests/` — `test_quicksort.py`, `test_tree.py`, `test_fib.py`, `test_filetree.py`, `test_performance.py`, `test_main.py`.

## Структура

```
Lab_04/
  README.md
  algorithms.py
  filetree.py
  main.py
  requirements.txt
  mypy.ini
  pyproject.toml
  .gitignore
  tests/
    __init__.py
    conftest.py
    test_quicksort.py
    test_tree.py
    test_fib.py
    test_filetree.py
    test_performance.py
    test_main.py
  report/
    Lab_04.docx
```

## Запуск

```
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
pytest -q --durations=5
mypy .
black --check .
ruff check .
```

## Ліміт рекурсії та відсутність TCO

У CPython глибина стеку викликів обмежена (`sys.getrecursionlimit()`, зазвичай 1000 кадрів); при перевищенні виникає `RecursionError`. Оптимізації хвостових викликів (TCO) у CPython немає, тому навіть tail-рекурсивна `fact(n, acc)` будує стек такої ж глибини. Підняття ліміту через `sys.setrecursionlimit` ризиковане: надто глибока рекурсія може аварійно завершити інтерпретатор.

У роботі це показано на практиці: рекурсивні `count_files` і `tree_height` на каталозі глибиною 5000 падають із `RecursionError`, а ітеративні `count_files_iter` і `tree_height_iter` працюють. Ітеративну версію безпечніше використовувати, коли глибина вхідних даних невідома або може бути великою (глибокі каталоги, великі `n`).

## Мемоізація і час

`fib` з `@lru_cache(maxsize=None)` перетворює експоненційну рекурсію на лінійну: `cache_info()` показує попадання в кеш, `cache_clear()` очищує його. Приклад вимірювань (`pytest -s tests/test_performance.py`, `fib(25)`):

| Версія | Час |
| --- | --- |
| `fib_naive` (без кешу) | ≈ 0.03–0.06 с |
| `fib` (`lru_cache`) | ≈ 0.00003 с |
| `fib_iter` | ≈ 0.00001 с |

Для дерева з 15625 файлів рекурсивний `total_size` працює ≈ 0.0023 с, ітеративний ≈ 0.0057 с: ітеративна версія тут повільніша через збирання шляхів, але вона не залежить від глибини стека.
