from dataclasses import FrozenInstanceError
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from core import (
    add_feature,
    add_item,
    add_option,
    add_vip_tag,
    cached_rental_total,
    change_status,
    extend_rental,
    freeze,
    long_rental_discount,
    remove_option,
    rental_total,
    source,
    top_expensive_items,
    total_with_discount,
    update_meta,
)
from model import Car, Item, Option, Order, Rental, Status, make_meta
from tests.conftest import build_car, build_order, build_rental


def test_entities_are_frozen(sample_rental: Rental, sample_car: Car) -> None:
    with pytest.raises(FrozenInstanceError):
        sample_rental.days = 10  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        sample_car.daily_rate = 1.0  # type: ignore[misc]


def test_collections_are_immutable(sample_rental: Rental) -> None:
    assert isinstance(sample_rental.options, frozenset)
    assert isinstance(sample_rental.history, tuple)
    assert isinstance(sample_rental.car.features, frozenset)


def test_add_option_returns_new_object_without_mutation(
    sample_rental: Rental,
) -> None:
    updated = add_option(sample_rental, Option("gps_nav", 4.0))
    assert updated is not sample_rental
    assert sample_rental == build_rental()
    assert Option("gps_nav", 4.0) in updated.options
    assert Option("gps_nav", 4.0) not in sample_rental.options


def test_add_option_is_idempotent(sample_rental: Rental) -> None:
    option = Option("gps_nav", 4.0)
    once = add_option(sample_rental, option)
    twice = add_option(once, option)
    assert once == twice


def test_remove_option(sample_rental: Rental) -> None:
    updated = remove_option(sample_rental, "child_seat")
    assert updated.options == frozenset()
    assert sample_rental == build_rental()


def test_extend_rental_pure_and_validated(sample_rental: Rental) -> None:
    extended = extend_rental(sample_rental, 4)
    assert extended.days == 7
    assert sample_rental.days == 3
    with pytest.raises(ValueError):
        extend_rental(sample_rental, 0)
    closed = change_status(sample_rental, Status.RETURNED)
    with pytest.raises(ValueError):
        extend_rental(closed, 1)


def test_change_status_records_history(sample_rental: Rental) -> None:
    active = change_status(sample_rental, Status.ACTIVE)
    assert active.status is Status.ACTIVE
    assert active.history == (Status.BOOKED, Status.ACTIVE)
    assert sample_rental.status is Status.BOOKED
    assert sample_rental.history == (Status.BOOKED,)


def test_update_meta_returns_copy(sample_rental: Rental) -> None:
    updated = update_meta(sample_rental, source="app", note="vip")
    assert updated.meta["source"] == "app"
    assert updated.meta["note"] == "vip"
    assert sample_rental.meta["source"] == "web"
    assert "note" not in sample_rental.meta


def test_add_feature(sample_car: Car) -> None:
    updated = add_feature(sample_car, "bluetooth")
    assert "bluetooth" in updated.features
    assert sample_car == build_car()


def test_mappingproxy_is_read_only(sample_rental: Rental) -> None:
    with pytest.raises(TypeError):
        sample_rental.meta["source"] = "changed"  # type: ignore[index]


def test_meta_is_copied_from_source() -> None:
    source_dict = {"source": "web"}
    meta = make_meta(**source_dict)
    source_dict["source"] = "hacked"
    assert meta["source"] == "web"


def test_hashability(sample_rental: Rental, sample_car: Car) -> None:
    other = add_option(sample_rental, Option("gps_nav", 4.0))
    assert len({sample_rental, other}) == 2
    assert hash(sample_rental) == hash(build_rental())
    assert {sample_car: 1}[build_car()] == 1
    index = {(sample_rental.id, sample_rental.status): sample_rental}
    assert index[(1, Status.BOOKED)] == sample_rental


def test_rental_total_and_discount(sample_rental: Rental) -> None:
    assert rental_total(sample_rental) == pytest.approx((50.0 + 5.0) * 3)
    long_rental = extend_rental(sample_rental, 4)
    assert total_with_discount(long_rental, long_rental_discount) == pytest.approx(
        (50.0 + 5.0) * 7 * 0.9
    )
    assert total_with_discount(sample_rental, long_rental_discount) == pytest.approx(
        rental_total(sample_rental)
    )


def test_lru_cache_works_with_hashable_rental(sample_rental: Rental) -> None:
    cached_rental_total.cache_clear()
    first = cached_rental_total(sample_rental)
    second = cached_rental_total(build_rental())
    assert first == second == rental_total(sample_rental)
    info = cached_rental_total.cache_info()
    assert info.hits == 1
    assert info.misses == 1


def test_freeze_makes_nested_structures_immutable() -> None:
    raw: dict[str, Any] = {"tags": {"a", "b"}, "items": [{"x": 1}, [2, 3]], "name": "n"}
    frozen = freeze(raw)
    assert isinstance(frozen["tags"], frozenset)
    assert isinstance(frozen["items"], tuple)
    assert frozen["name"] == "n"
    with pytest.raises(TypeError):
        frozen["name"] = "other"
    with pytest.raises(TypeError):
        frozen["items"][0]["x"] = 2
    raw["tags"].add("c")
    assert "c" not in frozen["tags"]


def test_order_no_mutation_and_new_object(sample_order: Order) -> None:
    new_order = add_item(sample_order, "X1", 5.0, 1)
    assert new_order is not sample_order
    assert sample_order == build_order()
    assert new_order.subtotal() == sample_order.subtotal() + 5.0


def test_order_tag_and_hashability(sample_order: Order) -> None:
    tagged = add_vip_tag(sample_order)
    assert "vip" in tagged.tags
    assert "vip" not in sample_order.tags
    assert len({sample_order, add_item(sample_order, "C3", 15.0, 2)}) == 2


def test_order_meta_read_only(sample_order: Order) -> None:
    with pytest.raises(TypeError):
        sample_order.meta["source"] = "changed"  # type: ignore[index]
    assert source(sample_order.meta) == "fb_ads"
    assert source(make_meta()) == "unknown"


def test_top_expensive_items(sample_order: Order) -> None:
    top = top_expensive_items(sample_order.items, 1)
    assert top == (Item("A1", 50.0, 2),)
    assert isinstance(top, tuple)


@given(st.integers(min_value=1, max_value=365))
def test_extend_adds_days(extra: int) -> None:
    rental = build_rental()
    assert extend_rental(rental, extra).days == rental.days + extra
    assert rental == build_rental()


@settings(max_examples=30, deadline=None)
@given(st.sets(st.text(min_size=1, max_size=5), max_size=5))
def test_options_set_semantics(names: set[str]) -> None:
    rental = build_rental()
    for name in names:
        rental = add_option(rental, Option(name, 1.0))
    again = rental
    for name in names:
        again = add_option(again, Option(name, 1.0))
    assert rental == again
