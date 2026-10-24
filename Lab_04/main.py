"""Демонстрація рекурсивних та ітеративних алгоритмів лабораторної роботи."""

import sys

from algorithms import fib, fib_iter, quicksort
from filetree import (
    DirNode,
    FileNode,
    FsNode,
    count_files,
    count_files_iter,
    total_size,
    tree_height,
    walk_files,
    walk_files_bfs,
)


def build_sample_tree() -> DirNode:
    """Будує невеликий каталог для демонстрації."""
    return DirNode(
        "root",
        (
            FileNode("README.md", 100),
            DirNode(
                "src",
                (
                    FileNode("main.py", 300),
                    DirNode("utils", (FileNode("helpers.py", 150),)),
                ),
            ),
            DirNode("docs", (FileNode("guide.md", 200), DirNode("empty"))),
        ),
    )


def build_chain(depth: int) -> FsNode:
    """Будує глибокий ланцюжок каталогів ітеративно."""
    node: FsNode = FileNode("leaf.txt", 1)
    for _ in range(depth):
        node = DirNode("d", (node,))
    return node


def main() -> None:
    """Показує обходи, мемоізацію та обмеження стеку CPython."""
    tree = build_sample_tree()
    print(
        f"files={count_files(tree)} size={total_size(tree)} height={tree_height(tree)}"
    )
    print(f"dfs: {list(walk_files(tree))}")
    print(f"bfs: {walk_files_bfs(tree)}")
    print(f"quicksort: {quicksort([5, 3, 8, 1, 3, 9, 2])}")
    print(f"fib(80)={fib(80)} fib_iter(80)={fib_iter(80)}")
    print(f"cache: {fib.cache_info()}")
    print(f"recursion limit: {sys.getrecursionlimit()}")
    chain = build_chain(5000)
    try:
        count_files(chain)
    except RecursionError:
        print("recursive count_files: RecursionError")
    print(f"iterative count_files_iter: {count_files_iter(chain)}")


if __name__ == "__main__":
    main()
