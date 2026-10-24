import pytest

from filetree import DirNode, FileNode, FsNode


def build_sample_fs() -> DirNode:
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
    node: FsNode = FileNode("leaf.txt", 1)
    for _ in range(depth):
        node = DirNode("d", (node,))
    return node


@pytest.fixture
def sample_fs() -> DirNode:
    return build_sample_fs()
