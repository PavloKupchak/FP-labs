"""Функціональний конвеєр: map/filter/reduce, compose, pipe, juxt (варіант 7: склад)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from functools import reduce
from itertools import islice
from typing import Any, TypedDict, TypeVar, cast

T = TypeVar("T")


class Record(TypedDict, total=False):
    """Клієнт інтернет-магазину (базове завдання)."""

    id: int
    name: str
    age: int
    city: str
    purchases: list[float]
    total: float


class StockItem(TypedDict, total=False):
    """Товар складу; value з'являється в результаті."""

    id: int
    name: str
    category: str
    price: float
    stock: int
    value: float


Stage = Callable[[Iterable[T]], Iterator[T]]


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Композиція справа наліво: compose(f, g)(x) == f(g(x))."""
    return lambda x: reduce(lambda acc, f: f(acc), reversed(funcs), x)


def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Композиція зліва направо: pipe(f, g)(x) == g(f(x))."""
    return lambda x: reduce(lambda acc, f: f(acc), funcs, x)


def juxt(*funcs: Callable[[T], Any]) -> Callable[[T], tuple[Any, ...]]:
    """Застосовує кожну функцію до одного значення й повертає кортеж результатів."""
    return lambda x: tuple(f(x) for f in funcs)


def take(n: int) -> Callable[[Iterable[T]], list[T]]:
    """Перші n елементів (Top-N після сортування)."""
    return lambda items: list(islice(items, n))


# ---------- базове завдання: клієнти ----------


def only_adults(min_age: int = 18) -> Stage[Record]:
    """Фільтр: повнолітні."""
    return lambda recs: (r for r in recs if int(r.get("age", 0)) >= min_age)


def with_total() -> Stage[Record]:
    """Map: додає total = сума покупок."""
    return lambda recs: (
        {**r, "total": float(sum(r.get("purchases", []) or []))} for r in recs
    )


def boost_city(city: str, factor: float) -> Stage[Record]:
    """Map: підсилює total для вибраного міста."""

    def apply(recs: Iterable[Record]) -> Iterator[Record]:
        for r in recs:
            total = float(r.get("total", 0.0))
            yield {**r, "total": total * factor if r.get("city") == city else total}

    return apply


def normalize_names() -> Stage[Record]:
    """Map: ім'я у Title Case без зайвих пробілів."""
    return lambda recs: (
        {**r, "name": str(r.get("name", "")).strip().title()} for r in recs
    )


def sort_by_total_desc() -> Callable[[Iterable[Record]], list[Record]]:
    """Сортування: total спадно, id зростаючи."""
    return lambda recs: sorted(
        recs, key=lambda r: (-float(r.get("total", 0.0)), r.get("id", 0))
    )


def reduce_stats(recs: Iterable[Record]) -> dict[str, float]:
    """Агрегація reduce: count, sum_total, avg_total."""
    init = {"count": 0.0, "sum_total": 0.0}
    acc = reduce(
        lambda a, r: {
            "count": a["count"] + 1,
            "sum_total": a["sum_total"] + float(r.get("total", 0.0)),
        },
        recs,
        init,
    )
    avg = acc["sum_total"] / acc["count"] if acc["count"] else 0.0
    return {"count": acc["count"], "sum_total": acc["sum_total"], "avg_total": avg}


def build_pipeline(
    top_n: int = 2, city: str = "Delhi", factor: float = 1.1
) -> Callable[[Iterable[Record]], list[Record]]:
    """Конвеєр клієнтів; compose застосовує функції справа наліво."""
    return cast(
        Callable[[Iterable[Record]], list[Record]],
        compose(
            take(top_n),
            sort_by_total_desc(),
            boost_city(city, factor),
            with_total(),
            only_adults(18),
            normalize_names(),
        ),
    )


# ---------- варіант 7: аналіз товарів складу ----------


def normalize_item_names() -> Stage[StockItem]:
    """Map: назва товару у Title Case без зайвих пробілів."""
    return lambda items: (
        {**i, "name": str(i.get("name", "")).strip().title()} for i in items
    )


def only_in_stock(min_stock: int = 1) -> Stage[StockItem]:
    """Фільтр: товари із запасом не менше min_stock."""
    return lambda items: (i for i in items if int(i.get("stock", 0)) >= min_stock)


def with_value() -> Stage[StockItem]:
    """Map: вартість запасу value = price × stock."""
    return lambda items: (
        {**i, "value": float(i.get("price", 0.0)) * int(i.get("stock", 0))}
        for i in items
    )


def boost_category(category: str, factor: float) -> Stage[StockItem]:
    """Map: коефіцієнт для вибраної категорії."""

    def apply(items: Iterable[StockItem]) -> Iterator[StockItem]:
        for i in items:
            value = float(i.get("value", 0.0))
            yield {
                **i,
                "value": value * factor if i.get("category") == category else value,
            }

    return apply


def apply_category_factors(factors: Mapping[str, float]) -> Stage[StockItem]:
    """Map: окремий коефіцієнт для кожної категорії (за замовчуванням 1.0)."""
    frozen = dict(factors)
    return lambda items: (
        {
            **i,
            "value": float(i.get("value", 0.0))
            * frozen.get(str(i.get("category")), 1.0),
        }
        for i in items
    )


def sort_by_value_desc() -> Callable[[Iterable[StockItem]], list[StockItem]]:
    """Сортування: value спадно, id зростаючи."""
    return lambda items: sorted(
        items, key=lambda i: (-float(i.get("value", 0.0)), i.get("id", 0))
    )


def reduce_inventory_stats(items: Iterable[StockItem]) -> dict[str, float]:
    """Агрегація reduce: count, inventory_value, avg_value."""
    init = {"count": 0.0, "inventory_value": 0.0}
    acc = reduce(
        lambda a, i: {
            "count": a["count"] + 1,
            "inventory_value": a["inventory_value"] + float(i.get("value", 0.0)),
        },
        items,
        init,
    )
    avg = acc["inventory_value"] / acc["count"] if acc["count"] else 0.0
    return {
        "count": acc["count"],
        "inventory_value": acc["inventory_value"],
        "avg_value": avg,
    }


def process_inventory(
    category: str = "Electronics", factor: float = 1.1, min_stock: int = 1
) -> Callable[[Iterable[StockItem]], list[StockItem]]:
    """Усі кроки конвеєра складу, крім Top-N."""
    return cast(
        Callable[[Iterable[StockItem]], list[StockItem]],
        compose(
            sort_by_value_desc(),
            boost_category(category, factor),
            with_value(),
            only_in_stock(min_stock),
            normalize_item_names(),
        ),
    )


def build_inventory_pipeline(
    top_n: int = 3,
    category: str = "Electronics",
    factor: float = 1.1,
    min_stock: int = 1,
) -> Callable[[Iterable[StockItem]], list[StockItem]]:
    """Повний конвеєр складу з Top-N."""
    return cast(
        Callable[[Iterable[StockItem]], list[StockItem]],
        pipe(process_inventory(category, factor, min_stock), take(top_n)),
    )
