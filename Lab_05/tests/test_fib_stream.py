from itertools import islice

from streams import drop, fib_stream, take


def test_first_10() -> None:
    assert list(islice(fib_stream(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_first_zero_values() -> None:
    assert take(0, fib_stream()) == []


def test_skip_five_take_eight() -> None:
    assert take(8, drop(5, fib_stream())) == [5, 8, 13, 21, 34, 55, 89, 144]


def test_streams_are_independent() -> None:
    first = fib_stream()
    second = fib_stream()
    assert take(3, first) == [0, 1, 1]
    assert take(3, second) == [0, 1, 1]


def test_large_index_is_correct() -> None:
    assert take(1, drop(90, fib_stream())) == [2880067194370816120]
