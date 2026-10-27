from collections.abc import Iterator
from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given
from hypothesis import strategies as st

from evaluator import (
    flat_map,
    flatten,
    is_failure,
    is_success,
    map_result,
    sequence,
    unwrap_or,
)
from model import Failure, Result, Success
from pretty import render_result


def test_map_result() -> None:
    assert map_result(lambda n: n + 1, Success(1)) == Success(2)
    failure = Failure("boom", "invalid")
    assert map_result(lambda n: n + 1, failure) is failure


def test_map_result_changes_type() -> None:
    assert map_result(str, Success(5)) == Success("5")


def test_flat_map_chains_and_short_circuits() -> None:
    def half(n: int) -> Result[int]:
        return Success(n // 2) if n % 2 == 0 else Failure(f"odd: {n}")

    assert flat_map(half, Success(8)) == Success(4)
    assert flat_map(half, flat_map(half, Success(8))) == Success(2)
    assert flat_map(half, Success(3)) == Failure("odd: 3")
    assert flat_map(half, Failure("first")) == Failure("first")


def test_unwrap_or() -> None:
    assert unwrap_or(Success(5), 0) == 5
    assert unwrap_or(Failure("x"), 0) == 0
    assert unwrap_or(Success(None), 1) is None


def test_success_may_hold_none_without_being_a_failure() -> None:
    result: Result[None] = Success(None)
    assert is_success(result)
    assert not is_failure(result)


def test_flatten_nested_results() -> None:
    assert flatten(Success(Success(1))) == Success(1)
    assert flatten(Success(Failure("inner", "not_found"))) == Failure(
        "inner", "not_found"
    )
    assert flatten(Failure("outer")) == Failure("outer")


def test_sequence() -> None:
    ok: list[Result[int]] = [Success(1), Success(2)]
    assert sequence(ok) == Success((1, 2))
    assert sequence([]) == Success(())
    first_failure = Failure("first")
    mixed: list[Result[int]] = [Success(1), first_failure, Failure("second")]
    assert sequence(mixed) is first_failure


def test_sequence_stops_at_first_failure() -> None:
    consumed: list[int] = []

    def source() -> Iterator[Result[int]]:
        for i in range(5):
            consumed.append(i)
            yield Failure("stop") if i == 2 else Success(i)

    assert sequence(source()) == Failure("stop")
    assert consumed == [0, 1, 2]


def test_failure_defaults_and_equality() -> None:
    assert Failure("x").code == "invalid"
    assert Failure("x", "overflow") != Failure("x")
    assert Success(1) == Success(1)
    assert Success(1) != Success(2)
    other: object = Failure("1")
    assert Success(1) != other


def test_nodes_are_frozen_and_hashable() -> None:
    ok = Success(1)
    with pytest.raises(FrozenInstanceError):
        ok.value = 2  # type: ignore[misc]
    bad = Failure("x")
    with pytest.raises(FrozenInstanceError):
        bad.error = "y"  # type: ignore[misc]
    assert len({Success(1), Success(1), Failure("x"), Failure("x")}) == 2


def test_inputs_are_not_mutated() -> None:
    items: list[Result[int]] = [Success(1), Failure("x")]
    snapshot = list(items)
    sequence(items)
    assert items == snapshot


def test_render_result() -> None:
    assert render_result(Success(5)) == "Success(5)"
    assert render_result(Success("a")) == "Success('a')"
    assert render_result(Failure("boom", "overflow")) == "Failure[overflow]: boom"
    assert render_result(Success(Success(1))) == "Success(Success(value=1))"


@given(st.integers())
def test_functor_identity(n: int) -> None:
    assert map_result(lambda x: x, Success(n)) == Success(n)


@given(st.integers(-1000, 1000))
def test_functor_composition(n: int) -> None:
    def inc(x: int) -> int:
        return x + 1

    def dbl(x: int) -> int:
        return x * 2

    left = map_result(lambda x: dbl(inc(x)), Success(n))
    right = map_result(dbl, map_result(inc, Success(n)))
    assert left == right


@given(st.integers(-1000, 1000))
def test_monad_laws(n: int) -> None:
    def f(x: int) -> Result[int]:
        return Success(x + 1) if x >= 0 else Failure("negative")

    def g(x: int) -> Result[int]:
        return Success(x * 2) if x < 500 else Failure("big", "overflow")

    assert flat_map(f, Success(n)) == f(n)
    assert flat_map(Success, Success(n)) == Success(n)
    left = flat_map(g, flat_map(f, Success(n)))
    right = flat_map(lambda x: flat_map(g, f(x)), Success(n))
    assert left == right
