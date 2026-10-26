import threading

import pytest

from decorators import cached


class Clock:
    def __init__(self, now: float = 1000.0) -> None:
        self.now = now

    def __call__(self) -> float:
        return self.now


def test_cached_ttl_and_invalidate() -> None:
    clock = Clock()
    hit = {"n": 0}

    @cached(ttl=1.0, time_fn=clock)
    def f(x: int) -> int:
        hit["n"] += 1
        return x * 2

    assert f(10) == 20
    assert f(10) == 20
    assert hit["n"] == 1

    clock.now += 2.0
    assert f(10) == 20
    assert hit["n"] == 2

    removed = f.cache_invalidate(lambda args, kwargs: args == (10,))
    assert removed == 1
    assert f(10) == 20
    assert hit["n"] == 3


def test_ttl_boundary_is_exclusive() -> None:
    clock = Clock()
    calls = {"n": 0}

    @cached(ttl=5.0, time_fn=clock)
    def f() -> int:
        calls["n"] += 1
        return calls["n"]

    assert f() == 1
    clock.now += 4.999
    assert f() == 1
    clock.now += 0.001
    assert f() == 2


def test_no_ttl_never_expires() -> None:
    clock = Clock()
    calls = {"n": 0}

    @cached(time_fn=clock)
    def f(x: int) -> int:
        calls["n"] += 1
        return x

    f(1)
    clock.now += 10**9
    f(1)
    assert calls["n"] == 1


def test_cache_info_and_clear() -> None:
    @cached()
    def f(x: int) -> int:
        return x + 1

    f(1)
    f(1)
    f(2)
    info = f.cache_info()
    assert (info.hits, info.misses, info.size) == (1, 2, 2)
    f.cache_clear()
    assert f.cache_info() == (0, 0, 0)


def test_selective_invalidation_by_predicate() -> None:
    @cached()
    def f(x: int, scale: int = 1) -> int:
        return x * scale

    for n in range(5):
        f(n)
    f(1, scale=3)
    removed = f.cache_invalidate(lambda args, kwargs: args[0] % 2 == 1)
    assert removed == 3
    assert f.cache_info().size == 3
    assert f.cache_invalidate(lambda args, kwargs: False) == 0


def test_args_and_kwargs_are_part_of_key() -> None:
    calls = {"n": 0}

    @cached()
    def f(a: int, b: int = 0) -> int:
        calls["n"] += 1
        return a + b

    assert f(1, b=2) == 3
    assert f(1, b=2) == 3
    assert f(1, b=3) == 4
    assert f(a=1, b=2) == 3
    assert calls["n"] == 3


def test_exceptions_are_not_cached() -> None:
    calls = {"n": 0}

    @cached()
    def f() -> int:
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("first")
        return 42

    with pytest.raises(RuntimeError):
        f()
    assert f() == 42
    assert f() == 42
    assert calls["n"] == 2


def test_unhashable_arguments_raise_type_error() -> None:
    @cached()
    def f(xs: list[int]) -> int:
        return len(xs)

    with pytest.raises(TypeError):
        f([1, 2, 3])


def test_custom_key_function() -> None:
    calls = {"n": 0}

    @cached(key_fn=lambda args, kwargs: args[0].lower())
    def f(name: str) -> str:
        calls["n"] += 1
        return name

    f("Alice")
    f("ALICE")
    assert calls["n"] == 1


def test_cached_preserves_metadata() -> None:
    @cached()
    def price(item: int) -> float:
        """Ціна товару."""
        return item * 1.5

    assert price.__name__ == "price"
    assert price.__doc__ == "Ціна товару."
    assert price.__wrapped__(2) == 3.0


def test_cached_is_thread_safe() -> None:
    @cached()
    def square(x: int) -> int:
        return x * x

    results: list[int] = []

    def worker() -> None:
        for i in range(50):
            results.append(square(i % 5))

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(set(results)) == [0, 1, 4, 9, 16]
    assert square.cache_info().size == 5
