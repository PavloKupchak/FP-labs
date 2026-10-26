import operator
from itertools import accumulate

from streams import (
    drop_while,
    naturals,
    prefix_products,
    prefix_sums,
    running_max,
    take,
    take_while,
)


def test_accumulate_sum_prod() -> None:
    assert list(accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(accumulate([1, 2, 3, 4], operator.mul)) == [1, 2, 6, 24]


def test_wrappers() -> None:
    assert list(prefix_sums([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(prefix_products([1, 2, 3, 4])) == [1, 2, 6, 24]
    assert list(running_max([3, 1, 4, 1, 5])) == [3, 3, 4, 4, 5]


def test_empty_input() -> None:
    assert list(prefix_sums([])) == []
    assert list(running_max([])) == []


def test_take_while_and_drop_while() -> None:
    assert list(take_while(lambda x: x < 4, naturals(1))) == [1, 2, 3]
    assert list(drop_while(lambda x: x <= 0, [-1, 0, 2, -3, 5])) == [2, -3, 5]


def test_prefix_sums_on_infinite_stream() -> None:
    assert take(5, prefix_sums(naturals(1))) == [1, 3, 6, 10, 15]
