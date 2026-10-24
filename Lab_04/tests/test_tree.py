from algorithms import (
    Node,
    bfs_level_order,
    dfs_preorder_iter,
    inorder,
    postorder,
    preorder,
)


def sample_tree() -> Node:
    return Node(4, left=Node(2, Node(1), Node(3)), right=Node(6, None, Node(7)))


def test_traversals() -> None:
    t = sample_tree()
    assert list(preorder(t)) == [4, 2, 1, 3, 6, 7]
    assert list(inorder(t)) == [1, 2, 3, 4, 6, 7]
    assert list(postorder(t)) == [1, 3, 2, 7, 6, 4]
    assert bfs_level_order(t) == [4, 2, 6, 1, 3, 7]
    assert dfs_preorder_iter(t) == [4, 2, 1, 3, 6, 7]


def test_empty_tree() -> None:
    assert list(preorder(None)) == []
    assert list(inorder(None)) == []
    assert list(postorder(None)) == []
    assert bfs_level_order(None) == []
    assert dfs_preorder_iter(None) == []


def test_single_node() -> None:
    t = Node(1)
    assert list(preorder(t)) == [1]
    assert bfs_level_order(t) == [1]
    assert dfs_preorder_iter(t) == [1]


def test_iterative_dfs_matches_recursive() -> None:
    t = sample_tree()
    assert dfs_preorder_iter(t) == list(preorder(t))


def test_iterative_dfs_handles_deep_tree() -> None:
    root = Node(0)
    current = root
    for key in range(1, 3000):
        current.left = Node(key)
        current = current.left
    assert len(dfs_preorder_iter(root)) == 3000
