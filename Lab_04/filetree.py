"""Файлова ієрархія як незмінне дерево (варіант 7) та рекурсивні/ітеративні обходи."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FileNode:
    """Файл із розміром у байтах."""

    name: str
    size: int

    def __post_init__(self) -> None:
        """Розмір файлу не може бути від'ємним."""
        if self.size < 0:
            raise ValueError("size must be non-negative")


@dataclass(frozen=True, slots=True)
class DirNode:
    """Каталог із кортежем дочірніх вузлів."""

    name: str
    children: tuple[FileNode | DirNode, ...] = ()


FsNode = FileNode | DirNode


def count_files(node: FsNode) -> int:
    """Рекурсивно рахує файли; база: файл дає 1, порожній каталог дає 0."""
    if isinstance(node, FileNode):
        return 1
    return sum(count_files(child) for child in node.children)


def total_size(node: FsNode) -> int:
    """Рекурсивно рахує сумарний розмір файлів."""
    if isinstance(node, FileNode):
        return node.size
    return sum(total_size(child) for child in node.children)


def tree_height(node: FsNode) -> int:
    """Висота: кількість ребер до найглибшого нащадка (файл і порожній каталог — 0)."""
    if isinstance(node, FileNode) or not node.children:
        return 0
    return 1 + max(tree_height(child) for child in node.children)


def join_path(prefix: str, name: str) -> str:
    """З'єднує шлях батька з іменем вузла."""
    return f"{prefix}/{name}" if prefix else name


def walk_files(node: FsNode, prefix: str = "") -> Iterator[str]:
    """Рекурсивний DFS: шляхи файлів у прямому порядку."""
    path = join_path(prefix, node.name)
    if isinstance(node, FileNode):
        yield path
        return
    for child in node.children:
        yield from walk_files(child, path)


def iter_files(node: FsNode) -> Iterator[tuple[str, FileNode]]:
    """Ітеративний DFS із власним стеком: пари (шлях, файл) у прямому порядку."""
    stack = [(node.name, node)]
    while stack:
        path, current = stack.pop()
        if isinstance(current, FileNode):
            yield path, current
        else:
            for child in reversed(current.children):
                stack.append((join_path(path, child.name), child))


def walk_files_bfs(node: FsNode) -> list[str]:
    """Ітеративний BFS: шляхи файлів у порядку обходу по рівнях."""
    queue = deque([(node.name, node)])
    out: list[str] = []
    while queue:
        path, current = queue.popleft()
        if isinstance(current, FileNode):
            out.append(path)
        else:
            for child in current.children:
                queue.append((join_path(path, child.name), child))
    return out


def count_files_iter(node: FsNode) -> int:
    """Ітеративний підрахунок файлів (безпечний для дуже глибоких каталогів)."""
    return sum(1 for _ in iter_files(node))


def total_size_iter(node: FsNode) -> int:
    """Ітеративний підрахунок сумарного розміру."""
    return sum(file.size for _, file in iter_files(node))


def tree_height_iter(node: FsNode) -> int:
    """Ітеративна висота дерева з явним стеком пар (вузол, глибина)."""
    stack = [(node, 0)]
    best = 0
    while stack:
        current, depth = stack.pop()
        best = max(best, depth)
        if isinstance(current, DirNode):
            for child in current.children:
                stack.append((child, depth + 1))
    return best
