import random

from hypothesis import given
from hypothesis import strategies as st

from algorithms import quicksort


def test_quicksort_basic() -> None:
    assert quicksort([]) == []
    assert quicksort([1]) == [1]
    assert quicksort([3, 2, 1]) == [1, 2, 3]
    assert quicksort([2, 2, 1, 3, 2]) == [1, 2, 2, 2, 3]


def test_quicksort_random() -> None:
    rng = random.Random(0)
    xs = [rng.randint(-1000, 1000) for _ in range(1000)]
    assert quicksort(xs) == sorted(xs)


def test_quicksort_does_not_mutate_input() -> None:
    xs = [5, 3, 8, 1]
    original = xs[:]
    result = quicksort(xs)
    assert xs == original
    assert result is not xs


def test_quicksort_sorted_and_reversed_input() -> None:
    ascending = list(range(500))
    assert quicksort(ascending) == ascending
    assert quicksort(ascending[::-1]) == ascending


def test_quicksort_many_duplicates() -> None:
    xs = [7] * 300 + [1] * 200 + [9] * 100
    assert quicksort(xs) == sorted(xs)


@given(st.lists(st.integers(min_value=-10_000, max_value=10_000), max_size=200))
def test_quicksort_matches_sorted(xs: list[int]) -> None:
    assert quicksort(xs) == sorted(xs)
