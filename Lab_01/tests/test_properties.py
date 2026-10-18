import math

from hypothesis import given
from hypothesis import strategies as st

from core import (
    Reading,
    Result,
    compose,
    make_multiplier,
    process_readings_pure,
)

RATES = {"household": 4.0, "pensioner": 3.5, "commercial": 6.0}
SHARES = {"pensioner": 0.5}

reading_strategy = st.builds(
    lambda i, prev, delta, group: Reading(
        id=i, prev=prev, curr=prev + delta, group=group
    ),
    st.integers(min_value=0, max_value=10_000),
    st.floats(min_value=0, max_value=1e6, allow_nan=False),
    st.floats(min_value=0, max_value=1e5, allow_nan=False),
    st.sampled_from(sorted(RATES)),
)
readings_strategy = st.lists(reading_strategy, max_size=30)


def calc(readings: list[Reading]) -> Result:
    return process_readings_pure(
        readings, rates=RATES, benefit_shares=SHARES, min_consumption=0.0
    )


@given(readings_strategy)
def test_same_input_same_output(readings: list[Reading]) -> None:
    assert calc(readings) == calc(readings)


@given(readings_strategy)
def test_input_is_not_mutated(readings: list[Reading]) -> None:
    snapshot = [dict(r) for r in readings]
    calc(readings)
    assert [dict(r) for r in readings] == snapshot


@given(readings_strategy)
def test_amounts_are_non_negative_and_bounded(readings: list[Reading]) -> None:
    result = calc(readings)
    assert result["count"] == len(result["bills"]) <= len(readings)
    for bill in result["bills"]:
        assert bill["consumption"] >= 0
        assert 0 <= bill["amount"] <= bill["consumption"] * RATES[bill["group"]] + 1e-6
        assert bill["amount"] >= 0


@given(readings_strategy)
def test_totals_match_bills(readings: list[Reading]) -> None:
    result = calc(readings)
    assert math.isclose(
        result["amount"],
        sum(b["amount"] for b in result["bills"]),
        rel_tol=1e-9,
        abs_tol=1e-6,
    )
    assert math.isclose(
        result["consumption"],
        sum(b["consumption"] for b in result["bills"]),
        rel_tol=1e-9,
        abs_tol=1e-6,
    )


@given(readings_strategy)
def test_order_does_not_change_total(readings: list[Reading]) -> None:
    forward = calc(readings)
    backward = calc(list(reversed(readings)))
    assert forward["count"] == backward["count"]
    assert math.isclose(
        forward["amount"], backward["amount"], rel_tol=1e-9, abs_tol=1e-3
    )


@given(st.integers(-1000, 1000), st.integers(-1000, 1000))
def test_multiplier_and_compose(k: int, x: int) -> None:
    assert make_multiplier(k)(x) == k * x
    assert compose(make_multiplier(2), make_multiplier(k))(x) == 2 * k * x
