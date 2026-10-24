import pytest

from filetree import (
    DirNode,
    FileNode,
    count_files,
    count_files_iter,
    iter_files,
    total_size,
    total_size_iter,
    tree_height,
    tree_height_iter,
    walk_files,
    walk_files_bfs,
)
from tests.conftest import build_chain, build_sample_fs


def test_count_and_size(sample_fs: DirNode) -> None:
    assert count_files(sample_fs) == 4
    assert total_size(sample_fs) == 750


def test_tree_height(sample_fs: DirNode) -> None:
    assert tree_height(sample_fs) == 3
    assert tree_height_iter(sample_fs) == 3


def test_empty_directory() -> None:
    empty = DirNode("empty")
    assert count_files(empty) == 0
    assert total_size(empty) == 0
    assert tree_height(empty) == 0
    assert list(walk_files(empty)) == []
    assert walk_files_bfs(empty) == []


def test_single_file() -> None:
    file = FileNode("a.txt", 5)
    assert count_files(file) == 1
    assert total_size(file) == 5
    assert list(walk_files(file)) == ["a.txt"]
    assert walk_files_bfs(file) == ["a.txt"]


def test_dfs_order(sample_fs: DirNode) -> None:
    assert list(walk_files(sample_fs)) == [
        "root/README.md",
        "root/src/main.py",
        "root/src/utils/helpers.py",
        "root/docs/guide.md",
    ]


def test_bfs_order(sample_fs: DirNode) -> None:
    assert walk_files_bfs(sample_fs) == [
        "root/README.md",
        "root/src/main.py",
        "root/docs/guide.md",
        "root/src/utils/helpers.py",
    ]


def test_iterative_matches_recursive(sample_fs: DirNode) -> None:
    assert [p for p, _ in iter_files(sample_fs)] == list(walk_files(sample_fs))
    assert count_files_iter(sample_fs) == count_files(sample_fs)
    assert total_size_iter(sample_fs) == total_size(sample_fs)


def test_deep_directory_recursion_vs_iteration() -> None:
    chain = build_chain(5000)
    with pytest.raises(RecursionError):
        count_files(chain)
    with pytest.raises(RecursionError):
        tree_height(chain)
    assert count_files_iter(chain) == 1
    assert total_size_iter(chain) == 1
    assert tree_height_iter(chain) == 5000


def test_moderately_deep_directory_works_recursively() -> None:
    chain = build_chain(200)
    assert count_files(chain) == 1
    assert tree_height(chain) == 200


def test_tree_is_immutable_and_not_mutated(sample_fs: DirNode) -> None:
    count_files(sample_fs)
    list(walk_files(sample_fs))
    walk_files_bfs(sample_fs)
    assert sample_fs == build_sample_fs()
    with pytest.raises(AttributeError):
        sample_fs.name = "other"  # type: ignore[misc]


def test_negative_size_rejected() -> None:
    with pytest.raises(ValueError):
        FileNode("bad.bin", -1)


def test_tree_is_hashable(sample_fs: DirNode) -> None:
    assert len({sample_fs, build_sample_fs()}) == 1
