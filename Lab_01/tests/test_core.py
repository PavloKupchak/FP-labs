from copy import deepcopy

import pytest

from core import (
    Reading,
    compose,
    consumption_of,
    is_valid_reading,
    make_flat_tariff,
    make_group_benefit,
    make_min_consumption_filter,
    make_multiplier,
    make_reading_processor,
    process_readings_pure,
    stamp_amount,
    with_bill,
)


def test_referential_transparency(
    sample_readings: list[Reading],
    rates: dict[str, float],
    benefit_shares: dict[str, float],
) -> None:
    r1 = process_readings_pure(
        sample_readings,
        rates=rates,
        benefit_shares=benefit_shares,
        min_consumption=1.0,
    )
    r2 = process_readings_pure(
        sample_readings,
        rates=rates,
        benefit_shares=benefit_shares,
        min_consumption=1.0,
    )
    assert r1 == r2


def test_no_mutation(
    sample_readings: list[Reading],
    rates: dict[str, float],
    benefit_shares: dict[str, float],
) -> None:
    original = deepcopy(sample_readings)
    original_rates = deepcopy(rates)
    process_readings_pure(
        sample_readings,
        rates=rates,
        benefit_shares=benefit_shares,
        min_consumption=0.0,
    )
    assert sample_readings == original
    assert rates == original_rates


def test_with_bill_returns_new_object(sample_readings: list[Reading]) -> None:
    original = sample_readings[0]
    updated = with_bill(original, 150.0, 600.0)
    assert updated is not original
    assert "amount" not in original
    assert updated["consumption"] == 150.0
    assert updated["amount"] == 600.0


def test_consumption_and_validity(sample_readings: list[Reading]) -> None:
    assert consumption_of(sample_readings[0]) == 150.0
    assert is_valid_reading(sample_readings[0]) is True
    assert is_valid_reading(sample_readings[2]) is False


def test_process_values(
    sample_readings: list[Reading],
    rates: dict[str, float],
    benefit_shares: dict[str, float],
) -> None:
    result = process_readings_pure(
        sample_readings,
        rates=rates,
        benefit_shares=benefit_shares,
        min_consumption=1.0,
    )
    assert result["count"] == 2
    assert [b["id"] for b in result["bills"]] == [1, 2]
    assert result["consumption"] == pytest.approx(350.0)
    assert result["amount"] == pytest.approx(150 * 4.0 + 200 * 4.0 * 0.5)


def test_callable_policies(sample_readings: list[Reading]) -> None:
    processor = make_reading_processor(
        accept=lambda c: c > 0,
        tariff=lambda group, c: c * 2.0,
        benefit=lambda group, amount: amount - 10.0,
    )
    result = processor(sample_readings)
    assert result["count"] == 2
    assert result["amount"] == pytest.approx((150 * 2 - 10) + (200 * 2 - 10))


def test_processor_is_replaceable(sample_readings: list[Reading]) -> None:
    processor = make_reading_processor(
        accept=lambda c: True,
        tariff=lambda group, c: c,
        benefit=lambda group, amount: amount,
    )
    result = processor(sample_readings)
    assert result["count"] == 3
    assert result["amount"] == pytest.approx(350.0)


def test_policy_factories(rates: dict[str, float]) -> None:
    tariff = make_flat_tariff(rates)
    benefit = make_group_benefit({"pensioner": 0.25})
    assert tariff("commercial", 10.0) == 60.0
    assert benefit("pensioner", 100.0) == 75.0
    assert benefit("household", 100.0) == 100.0
    assert make_min_consumption_filter(5.0)(5.0) is True
    assert make_min_consumption_filter(5.0)(4.9) is False


def test_compose_and_multiplier() -> None:
    double = make_multiplier(2)
    inc_after_double = compose(lambda x: x + 1, double)
    assert inc_after_double(5) == 11


def test_stamp_amount_injected_time() -> None:
    assert stamp_amount(5.0, lambda: 123.0) == (5.0, 123.0)


def test_empty_input() -> None:
    result = process_readings_pure([], rates={}, benefit_shares={}, min_consumption=0.0)
    assert result == {"count": 0, "consumption": 0, "amount": 0, "bills": []}


def test_generator_input(
    sample_readings: list[Reading],
    rates: dict[str, float],
    benefit_shares: dict[str, float],
) -> None:
    result = process_readings_pure(
        (r for r in sample_readings),
        rates=rates,
        benefit_shares=benefit_shares,
        min_consumption=1.0,
    )
    assert result["count"] == 2
