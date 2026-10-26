from itertools import islice, starmap

import pytest
from hypothesis import given
from hypothesis import strategies as st

from streams import chunked, moving_average, naturals, sliding_window, take


def test_windows_basic() -> None:
    assert list(sliding_window([1, 2, 3, 4], 3)) == [(1, 2, 3), (2, 3, 4)]


def test_window_sums() -> None:
    sums = list(starmap(lambda *w: sum(w), sliding_window(range(5), 2)))
    assert sums == [1, 3, 5, 7]


def test_window_edge_cases() -> None:
    assert list(sliding_window([1, 2], 3)) == []
    assert list(sliding_window([], 2)) == []
    assert list(sliding_window([1, 2, 3], 1)) == [(1,), (2,), (3,)]


def test_invalid_window_size() -> None:
    with pytest.raises(ValueError):
        sliding_window([1, 2, 3], 0)
    with pytest.raises(ValueError):
        sliding_window([1, 2, 3], -2)


def test_window_over_infinite_stream() -> None:
    sums = islice(starmap(lambda *w: sum(w), sliding_window(naturals(1), 3)), 10)
    assert list(sums) == [6, 9, 12, 15, 18, 21, 24, 27, 30, 33]


def test_moving_average() -> None:
    assert list(moving_average([1, 2, 3, 4], 2)) == [1.5, 2.5, 3.5]
    assert take(3, moving_average(naturals(1), 3)) == [2.0, 3.0, 4.0]
    with pytest.raises(ValueError):
        moving_average([1, 2], 0)


def test_chunked() -> None:
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [(1, 2), (3, 4), (5,)]
    assert list(chunked([], 3)) == []
    with pytest.raises(ValueError):
        chunked([1], 0)


@given(st.lists(st.integers(), max_size=60), st.integers(min_value=1, max_value=10))
def test_window_count_property(xs: list[int], k: int) -> None:
    assert len(list(sliding_window(xs, k))) == max(0, len(xs) - k + 1)


@given(st.lists(st.integers(), max_size=60), st.integers(min_value=1, max_value=10))
def test_chunked_preserves_items(xs: list[int], k: int) -> None:
    batches = list(chunked(xs, k))
    assert [x for batch in batches for x in batch] == xs
    assert all(len(batch) == k for batch in batches[:-1])
