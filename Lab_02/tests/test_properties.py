from copy import deepcopy

from hypothesis import given
from hypothesis import strategies as st

from core import StockItem, build_inventory_pipeline, compose, pipe, process_inventory

item_strategy = st.fixed_dictionaries(
    {
        "id": st.integers(0, 50),
        "name": st.text(max_size=8),
        "category": st.sampled_from(["A", "B", "C"]),
        "price": st.floats(0, 1000, allow_nan=False),
        "stock": st.integers(0, 500),
    }
)
items_strategy = st.lists(item_strategy, max_size=30)


@given(items_strategy, st.integers(0, 10), st.integers(0, 5))
def test_top_n_is_sorted_and_bounded(
    items: list[StockItem], top_n: int, min_stock: int
) -> None:
    top = build_inventory_pipeline(top_n, "A", 1.5, min_stock)(items)
    assert len(top) <= top_n
    assert all(i["stock"] >= min_stock for i in top)
    keys = [(-i["value"], i["id"]) for i in top]
    assert keys == sorted(keys)


@given(items_strategy)
def test_pipeline_never_mutates_input(items: list[StockItem]) -> None:
    snapshot = deepcopy(items)
    build_inventory_pipeline(3)(items)
    process_inventory()(items)
    assert items == snapshot


@given(items_strategy)
def test_top_n_is_prefix_of_full_ranking(items: list[StockItem]) -> None:
    full = process_inventory("A", 2.0, 1)(items)
    top = build_inventory_pipeline(4, "A", 2.0, 1)(items)
    assert top == full[:4]


@given(st.integers(-100, 100))
def test_compose_and_pipe_are_inverse_orders(x: int) -> None:
    f = lambda n: n + 1
    g = lambda n: n * 3
    assert compose(f, g)(x) == pipe(g, f)(x)
