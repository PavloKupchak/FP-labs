import functools
from collections.abc import Callable
from typing import ParamSpec, TypeVar

from decorators import cached, timed

P = ParamSpec("P")
R = TypeVar("R")


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        self.now += 0.001
        return self.now


def test_timed_inside_cached_logs_only_misses() -> None:
    logs: list[str] = []
    calls = {"n": 0}

    @cached()
    @timed("inner", logger=logs.append, clock=Clock())
    def f(x: int) -> int:
        calls["n"] += 1
        return x

    f(1)
    f(1)
    f(1)
    assert calls["n"] == 1
    assert len(logs) == 1


def test_timed_outside_cached_logs_every_call() -> None:
    logs: list[str] = []
    calls = {"n": 0}

    @timed("outer", logger=logs.append, clock=Clock())
    @cached()
    def f(x: int) -> int:
        calls["n"] += 1
        return x

    f(1)
    f(1)
    f(1)
    assert calls["n"] == 1
    assert len(logs) == 3


def test_decorators_apply_bottom_up() -> None:
    order: list[str] = []

    def tag(name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            @functools.wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                order.append(name)
                return func(*args, **kwargs)

            return wrapper

        return decorator

    @tag("outer")
    @tag("inner")
    def f() -> None:
        order.append("body")

    f()
    assert order == ["outer", "inner", "body"]
