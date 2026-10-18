from copy import deepcopy

import pytest

from core import (
    Order,
    make_processor,
    order_subtotal,
    process_orders_pure,
    with_total,
)


def test_referential_transparency(sample_orders: list[Order]) -> None:
    r1 = process_orders_pure(sample_orders, min_total=100, discount=0.1, tax_rate=0.2)
    r2 = process_orders_pure(sample_orders, min_total=100, discount=0.1, tax_rate=0.2)
    assert r1 == r2


def test_no_mutation(sample_orders: list[Order]) -> None:
    original = deepcopy(sample_orders)
    process_orders_pure(sample_orders, min_total=0, discount=0.0, tax_rate=0.0)
    assert sample_orders == original


def test_callable_policies(sample_orders: list[Order]) -> None:
    processor = make_processor(
        accept=lambda s: s >= 50,
        apply_discount=lambda s: s * 0.9,
        apply_tax=lambda s: s * 1.2,
    )
    result = processor(sample_orders)
    assert result["count"] == 2
    assert result["revenue"] == pytest.approx((150 + 110) * 0.9 * 1.2)


def test_order_subtotal_and_with_total(sample_orders: list[Order]) -> None:
    assert order_subtotal(sample_orders[3]) == 110.0
    updated = with_total(sample_orders[0], 9.0)
    assert updated["total"] == 9.0
    assert "total" not in sample_orders[0]


def test_unpaid_orders_are_excluded(sample_orders: list[Order]) -> None:
    result = process_orders_pure(sample_orders, min_total=0, discount=0.0, tax_rate=0.0)
    assert result["count"] == 3
