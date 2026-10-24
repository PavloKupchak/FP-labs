"""Базові рекурсивні алгоритми: quicksort, обходи дерев, Фібоначчі з мемоізацією."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache
from random import choice


def quicksort(xs: list[int]) -> list[int]:
    """Рекурсивне сортування з випадковим pivot; повертає новий список."""
    if len(xs) <= 1:
        return xs[:]
    pivot = choice(xs)
    left = [x for x in xs if x < pivot]
    mid = [x for x in xs if x == pivot]
    right = [x for x in xs if x > pivot]
    return quicksort(left) + mid + quicksort(right)


@dataclass(slots=True)
class Node:
    """Вузол бінарного дерева."""

    key: int
    left: Node | None = None
    right: Node | None = None


def preorder(t: Node | None) -> Iterator[int]:
    """Рекурсивний обхід: корінь, ліве, праве піддерево."""
    if t is None:
        return
    yield t.key
    yield from preorder(t.left)
    yield from preorder(t.right)


def inorder(t: Node | None) -> Iterator[int]:
    """Рекурсивний обхід: ліве піддерево, корінь, праве піддерево."""
    if t is None:
        return
    yield from inorder(t.left)
    yield t.key
    yield from inorder(t.right)


def postorder(t: Node | None) -> Iterator[int]:
    """Рекурсивний обхід: ліве, праве піддерево, корінь."""
    if t is None:
        return
    yield from postorder(t.left)
    yield from postorder(t.right)
    yield t.key


def bfs_level_order(t: Node | None) -> list[int]:
    """Ітеративний обхід у ширину (по рівнях)."""
    if t is None:
        return []
    queue = deque([t])
    out: list[int] = []
    while queue:
        node = queue.popleft()
        out.append(node.key)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return out


def dfs_preorder_iter(t: Node | None) -> list[int]:
    """Ітеративний прямий обхід із власним стеком (без глибокої рекурсії)."""
    if t is None:
        return []
    stack = [t]
    out: list[int] = []
    while stack:
        node = stack.pop()
        out.append(node.key)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return out


def _check_index(n: int) -> None:
    """Перевіряє, що n є невід'ємним цілим числом."""
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")


@lru_cache(maxsize=None)  # noqa: UP033
def fib(n: int) -> int:
    """Фібоначчі: рекурсія з мемоізацією, O(n) часу."""
    _check_index(n)
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_naive(n: int) -> int:
    """Фібоначчі без кешу: експоненційна кількість викликів."""
    _check_index(n)
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


def fib_iter(n: int) -> int:
    """Фібоначчі ітеративно: без стеку викликів."""
    _check_index(n)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def fact(n: int, acc: int = 1) -> int:
    """Факторіал у tail-стилі; CPython не робить TCO, тому стек усе одно росте."""
    _check_index(n)
    if n <= 1:
        return acc
    return fact(n - 1, acc * n)


def fact_iter(n: int) -> int:
    """Факторіал ітеративно."""
    _check_index(n)
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result
