from collections.abc import Callable
from copy import deepcopy
from typing import Any

import pytest

from core import (
    Record,
    StockItem,
    apply_category_factors,
    boost_category,
    boost_city,
    build_inventory_pipeline,
    build_pipeline,
    compose,
    juxt,
    normalize_item_names,
    normalize_names,
    only_adults,
    only_in_stock,
    pipe,
    process_inventory,
    reduce_inventory_stats,
    reduce_stats,
    sort_by_total_desc,
    sort_by_value_desc,
    take,
    with_total,
    with_value,
)


@pytest.fixture
def items() -> list[StockItem]:
    return [
        {
            "id": 1,
            "name": "  laptop ",
            "category": "Electronics",
            "price": 1000.0,
            "stock": 5,
        },
        {
            "id": 2,
            "name": "chair",
            "category": "Furniture",
            "price": 150.0,
            "stock": 20,
        },
        {
            "id": 3,
            "name": "cable",
            "category": "Electronics",
            "price": 5.0,
            "stock": 200,
        },
        {"id": 4, "name": "desk", "category": "Furniture", "price": 400.0, "stock": 0},
        {
            "id": 5,
            "name": "notebook",
            "category": "Stationery",
            "price": 2.5,
            "stock": 1200,
        },
    ]


@pytest.fixture
def clients() -> list[Record]:
    return [
        {
            "id": 1,
            "name": "  alice ",
            "age": 30,
            "city": "Delhi",
            "purchases": [10.0, 20.0],
        },
        {"id": 2, "name": "BOB", "age": 17, "city": "Delhi", "purchases": [100.0]},
        {"id": 3, "name": "carol", "age": 25, "city": "Pune", "purchases": [40.0]},
        {"id": 4, "name": "dave", "age": 40, "city": "Delhi", "purchases": []},
    ]


# ---------- композиція ----------


def test_compose_applies_right_to_left() -> None:
    inc = lambda x: x + 1
    dbl = lambda x: x * 2
    assert compose(inc, dbl)(5) == 11
    assert compose(dbl, inc)(5) == 12


def test_pipe_applies_left_to_right() -> None:
    inc = lambda x: x + 1
    dbl = lambda x: x * 2
    assert pipe(inc, dbl)(5) == 12
    assert pipe(dbl, inc)(5) == 11


def test_compose_and_pipe_are_mirror_images() -> None:
    funcs = [lambda x: x + 3, lambda x: x * 2, lambda x: x - 1]
    assert compose(*funcs)(7) == pipe(*reversed(funcs))(7)


def test_compose_and_pipe_without_functions_are_identity() -> None:
    assert compose()(42) == 42
    assert pipe()("x") == "x"


def smallest(xs: list[int]) -> int:
    return min(xs)


def largest(xs: list[int]) -> int:
    return max(xs)


def total(xs: list[int]) -> int:
    return sum(xs)


def test_juxt_returns_tuple_of_results() -> None:
    stats = juxt(smallest, largest, total)
    assert stats([3, 1, 2]) == (1, 3, 6)
    empty: Callable[[int], tuple[Any, ...]] = juxt()
    assert empty(5) == ()


def test_take() -> None:
    assert take(2)([1, 2, 3]) == [1, 2]
    assert take(0)([1, 2]) == []
    assert take(5)([1, 2]) == [1, 2]
    assert take(2)(iter(range(100))) == [0, 1]
    with pytest.raises(ValueError):
        take(-1)([1])


# ---------- варіант 7: окремі кроки ----------


def test_only_in_stock_filters_by_stock(items: list[StockItem]) -> None:
    assert [i["id"] for i in only_in_stock(1)(items)] == [1, 2, 3, 5]
    assert [i["id"] for i in only_in_stock(20)(items)] == [2, 3, 5]
    assert [i["id"] for i in only_in_stock(0)(items)] == [1, 2, 3, 4, 5]
    assert list(only_in_stock(10_000)(items)) == []


def test_with_value_is_price_times_stock(items: list[StockItem]) -> None:
    values = {i["id"]: i["value"] for i in with_value()(items)}
    assert values == {1: 5000.0, 2: 3000.0, 3: 1000.0, 4: 0.0, 5: 3000.0}


def test_boost_category_only_changes_selected_category(
    items: list[StockItem],
) -> None:
    stage = boost_category("Electronics", 1.1)
    result = list(stage(with_value()(items)))
    assert result[0]["value"] == pytest.approx(5500.0)
    assert result[1]["value"] == pytest.approx(3000.0)
    assert result[2]["value"] == pytest.approx(1100.0)


def test_apply_category_factors(items: list[StockItem]) -> None:
    factors = {"Electronics": 2.0, "Furniture": 0.5}
    result = list(apply_category_factors(factors)(with_value()(items)))
    assert [r["value"] for r in result] == [10000.0, 1500.0, 2000.0, 0.0, 3000.0]


def test_normalize_item_names(items: list[StockItem]) -> None:
    names = [i["name"] for i in normalize_item_names()(items)]
    assert names[0] == "Laptop"
    assert names[4] == "Notebook"


def test_sort_by_value_desc_with_id_tiebreak() -> None:
    rows: list[StockItem] = [
        {"id": 3, "value": 10.0},
        {"id": 1, "value": 10.0},
        {"id": 2, "value": 20.0},
    ]
    assert [r["id"] for r in sort_by_value_desc()(rows)] == [2, 1, 3]


def test_missing_fields_use_defaults() -> None:
    rows: list[StockItem] = [{"id": 1}]
    assert list(only_in_stock(0)(rows)) == rows
    assert next(iter(with_value()(rows)))["value"] == 0.0
    assert next(iter(normalize_item_names()(rows)))["name"] == ""


# ---------- reduce-агрегація ----------


def test_reduce_inventory_stats(items: list[StockItem]) -> None:
    processed = process_inventory("Electronics", 1.0, 1)(items)
    stats = reduce_inventory_stats(processed)
    assert stats["count"] == 4
    assert stats["inventory_value"] == pytest.approx(12000.0)
    assert stats["avg_value"] == pytest.approx(3000.0)


def test_reduce_inventory_stats_on_empty_input() -> None:
    assert reduce_inventory_stats([]) == {
        "count": 0.0,
        "inventory_value": 0.0,
        "avg_value": 0.0,
    }


# ---------- повний конвеєр ----------


def test_pipeline_top_n(items: list[StockItem]) -> None:
    top = build_inventory_pipeline(top_n=2, category="Electronics", factor=1.1)(items)
    assert [i["id"] for i in top] == [1, 2]
    assert top[0]["name"] == "Laptop"
    assert top[0]["value"] == pytest.approx(5500.0)


def test_pipeline_tie_is_resolved_by_id(items: list[StockItem]) -> None:
    top = build_inventory_pipeline(top_n=5, category="None", factor=1.0)(items)
    assert [i["id"] for i in top] == [1, 2, 5, 3]


def test_pipeline_excludes_items_out_of_stock(items: list[StockItem]) -> None:
    top = build_inventory_pipeline(top_n=10, min_stock=1)(items)
    assert 4 not in [i["id"] for i in top]


def test_pipeline_handles_empty_and_large_top_n(items: list[StockItem]) -> None:
    assert build_inventory_pipeline()([]) == []
    assert len(build_inventory_pipeline(top_n=100)(items)) == 4
    assert build_inventory_pipeline(top_n=0)(items) == []


def test_pipeline_does_not_mutate_input(items: list[StockItem]) -> None:
    snapshot = deepcopy(items)
    build_inventory_pipeline(top_n=3)(items)
    process_inventory()(items)
    assert items == snapshot


def test_pipeline_output_is_new_objects(items: list[StockItem]) -> None:
    top = build_inventory_pipeline(top_n=5)(items)
    assert all(row is not original for row in top for original in items)


def test_pipeline_is_composition_of_stages(items: list[StockItem]) -> None:
    manual = take(2)(
        sort_by_value_desc()(
            boost_category("Electronics", 1.1)(
                with_value()(only_in_stock(1)(normalize_item_names()(items)))
            )
        )
    )
    assert build_inventory_pipeline(2, "Electronics", 1.1, 1)(items) == manual


def test_pipeline_accepts_generator_input(items: list[StockItem]) -> None:
    result = build_inventory_pipeline(top_n=1)(i for i in items)
    assert result[0]["id"] == 1


# ---------- базове завдання: клієнти ----------


def test_only_adults(clients: list[Record]) -> None:
    assert [r["id"] for r in only_adults(18)(clients)] == [1, 3, 4]
    assert [r["id"] for r in only_adults(35)(clients)] == [4]


def test_with_total_and_boost_city(clients: list[Record]) -> None:
    totals = list(with_total()(clients))
    assert [r["total"] for r in totals] == [30.0, 100.0, 40.0, 0.0]
    boosted = list(boost_city("Delhi", 1.1)(totals))
    assert boosted[0]["total"] == pytest.approx(33.0)
    assert boosted[2]["total"] == pytest.approx(40.0)


def test_normalize_names(clients: list[Record]) -> None:
    assert [r["name"] for r in normalize_names()(clients)] == [
        "Alice",
        "Bob",
        "Carol",
        "Dave",
    ]


def test_sort_by_total_desc(clients: list[Record]) -> None:
    rows = list(with_total()(clients))
    assert [r["id"] for r in sort_by_total_desc()(rows)] == [2, 3, 1, 4]


def test_build_pipeline_top_two(clients: list[Record]) -> None:
    top = build_pipeline(top_n=2, city="Delhi", factor=1.1)(clients)
    assert [r["id"] for r in top] == [3, 1]
    assert top[1]["total"] == pytest.approx(33.0)
    assert top[0]["name"] == "Carol"


def test_build_pipeline_does_not_mutate_input(clients: list[Record]) -> None:
    snapshot = deepcopy(clients)
    build_pipeline()(clients)
    assert clients == snapshot


def test_reduce_stats(clients: list[Record]) -> None:
    rows = list(with_total()(clients))
    assert reduce_stats(rows) == {
        "count": 4.0,
        "sum_total": 170.0,
        "avg_total": 42.5,
    }
    assert reduce_stats([]) == {"count": 0.0, "sum_total": 0.0, "avg_total": 0.0}
