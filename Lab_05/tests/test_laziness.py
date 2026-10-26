import sys
from collections.abc import Iterator

from streams import chunked, drop, sliding_window, take


def counting_source(counter: list[int]) -> Iterator[int]:
    n = 0
    while True:
        counter.append(n)
        yield n
        n += 1


def test_take_pulls_exactly_requested_items() -> None:
    counter: list[int] = []
    assert take(4, counting_source(counter)) == [0, 1, 2, 3]
    assert len(counter) == 4


def test_drop_then_take_pulls_only_needed_items() -> None:
    counter: list[int] = []
    assert take(2, drop(3, counting_source(counter))) == [3, 4]
    assert len(counter) == 5


def test_sliding_window_is_lazy() -> None:
    counter: list[int] = []
    windows = sliding_window(counting_source(counter), 3)
    assert len(counter) == 0
    next(windows)
    assert len(counter) == 3
    next(windows)
    assert len(counter) == 4


def test_chunked_is_lazy() -> None:
    counter: list[int] = []
    batches = chunked(counting_source(counter), 4)
    assert next(batches) == (0, 1, 2, 3)
    assert len(counter) == 4


def test_generator_is_exhausted_after_use() -> None:
    gen = (x * x for x in range(3))
    assert list(gen) == [0, 1, 4]
    assert list(gen) == []


def test_generator_uses_less_memory_than_list() -> None:
    eager = list(range(100_000))
    lazy = (x for x in range(100_000))
    assert sys.getsizeof(lazy) < sys.getsizeof(eager)
