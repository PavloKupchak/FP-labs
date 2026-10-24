import time
from collections.abc import Callable
from typing import Any

from algorithms import fib, fib_iter, fib_naive
from filetree import DirNode, FileNode, FsNode, total_size, total_size_iter


def build_wide(depth: int, width: int) -> FsNode:
    if depth == 0:
        return FileNode("f", 1)
    return DirNode("d", tuple(build_wide(depth - 1, width) for _ in range(width)))


def timed(func: Callable[..., Any], *args: Any) -> float:
    start = time.perf_counter()
    func(*args)
    return time.perf_counter() - start


def test_memoization_speeds_up_fibonacci() -> None:
    n = 25
    naive = timed(fib_naive, n)
    fib.cache_clear()
    cached = timed(fib, n)
    iterative = timed(fib_iter, n)
    print(f"fib({n}): naive={naive:.5f}s cached={cached:.6f}s iter={iterative:.6f}s")
    assert fib_naive(n) == fib(n) == fib_iter(n)
    assert cached < naive


def test_recursive_and_iterative_tree_sizes_match() -> None:
    tree = build_wide(6, 5)
    recursive = timed(total_size, tree)
    iterative = timed(total_size_iter, tree)
    print(f"tree 5^6 files: recursive={recursive:.5f}s iterative={iterative:.5f}s")
    assert total_size(tree) == total_size_iter(tree) == 5**6
