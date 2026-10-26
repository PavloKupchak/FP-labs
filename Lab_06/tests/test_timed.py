from collections.abc import Callable
from typing import Literal

import pytest

from decorators import timed


def make_clock(*ticks: float) -> Callable[[], float]:
    values = list(ticks)
    return lambda: values.pop(0)


def test_timed_uses_clock_and_logger() -> None:
    logs: list[str] = []

    @timed("work", unit="ms", logger=logs.append, clock=make_clock(0.0, 0.012345))
    def work(x: int) -> int:
        return x * x

    assert work(5) == 25
    assert logs == ["[timed] work took 12.345 ms"]


@pytest.mark.parametrize(
    ("unit", "expected"),
    [("s", "2.000 s"), ("ms", "2000.000 ms"), ("us", "2000000.000 us")],
)
def test_timed_units(unit: Literal["s", "ms", "us"], expected: str) -> None:
    logs: list[str] = []

    @timed(unit=unit, logger=logs.append, clock=make_clock(0.0, 2.0))
    def task() -> None:
        return None

    task()
    assert logs == [f"[timed] task took {expected}"]


def test_timed_default_label_is_function_name() -> None:
    logs: list[str] = []

    @timed(logger=logs.append, clock=make_clock(1.0, 1.5))
    def compute() -> int:
        return 1

    compute()
    assert "compute" in logs[0]


def test_timed_logs_even_when_function_raises() -> None:
    logs: list[str] = []

    @timed("boom", logger=logs.append, clock=make_clock(0.0, 0.001))
    def boom() -> None:
        raise RuntimeError("fail")

    with pytest.raises(RuntimeError):
        boom()
    assert logs == ["[timed] boom took 1.000 ms"]


def test_timed_preserves_metadata() -> None:
    @timed(logger=lambda _: None)
    def documented(a: int, b: int) -> int:
        """Додає числа."""
        return a + b

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "Додає числа."
    assert getattr(documented, "__wrapped__", None) is not None
    assert documented(1, 2) == 3


def test_timed_rejects_unknown_unit() -> None:
    with pytest.raises(ValueError):
        timed(unit="h")  # type: ignore[arg-type]
