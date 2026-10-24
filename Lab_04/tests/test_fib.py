import pytest

from algorithms import fact, fact_iter, fib, fib_iter, fib_naive


def test_fib_small() -> None:
    expected = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
    assert [fib(i) for i in range(10)] == expected


def test_fib_iter_matches() -> None:
    for n in range(50):
        assert fib(n) == fib_iter(n)
    for n in range(20):
        assert fib_naive(n) == fib_iter(n)


def test_cache_clear_and_info() -> None:
    fib.cache_clear()
    assert fib.cache_info().currsize == 0
    assert fib(30) == 832040
    info = fib.cache_info()
    assert info.misses == 31
    assert info.hits == 28
    fib.cache_clear()
    assert fib(0) == 0


def test_invalid_input() -> None:
    for func in (fib, fib_iter, fib_naive, fact, fact_iter):
        with pytest.raises(ValueError):
            func(-1)
    with pytest.raises(TypeError):
        fib(1.5)
    with pytest.raises(TypeError):
        fib_iter(True)


def test_recursion_limit_vs_iteration() -> None:
    fib.cache_clear()
    with pytest.raises(RecursionError):
        fib(5000)
    fib.cache_clear()
    assert fib_iter(5000) > 0


def test_factorial() -> None:
    assert fact(0) == 1
    assert fact(1) == 1
    assert fact(10) == 3628800
    assert fact(20) == fact_iter(20)
    with pytest.raises(RecursionError):
        fact(5000)
    assert fact_iter(5000) > 0
