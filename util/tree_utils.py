from collections import deque
from typing import Any


class TreeNode:
    def __init__(self, value: Any):
        self.value = value
        self.left: "TreeNode | None" = None
        self.right: "TreeNode | None" = None

    def __repr__(self) -> str:
        return f"TreeNode({self.value!r})"


def insert(root: TreeNode | None, value: Any) -> TreeNode:
    if root is None:
        return TreeNode(value)
    if value < root.value:
        root.left = insert(root.left, value)
    elif value > root.value:
        root.right = insert(root.right, value)
    return root


def search(root: TreeNode | None, value: Any) -> TreeNode | None:
    if root is None or root.value == value:
        return root
    if value < root.value:
        return search(root.left, value)
    return search(root.right, value)


def delete(root: TreeNode | None, value: Any) -> TreeNode | None:
    if root is None:
        return None
    if value < root.value:
        root.left = delete(root.left, value)
    elif value > root.value:
        root.right = delete(root.right, value)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        successor = min_node(root.right)
        root.value = successor.value
        root.right = delete(root.right, successor.value)
    return root


def inorder(root: TreeNode | None) -> list[Any]:
    if root is None:
        return []
    return inorder(root.left) + [root.value] + inorder(root.right)


def preorder(root: TreeNode | None) -> list[Any]:
    if root is None:
        return []
    return [root.value] + preorder(root.left) + preorder(root.right)


def postorder(root: TreeNode | None) -> list[Any]:
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.value]


def level_order(root: TreeNode | None) -> list[list[Any]]:
    if root is None:
        return []
    result, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.value)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


def height(root: TreeNode | None) -> int:
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))


def size(root: TreeNode | None) -> int:
    if root is None:
        return 0
    return 1 + size(root.left) + size(root.right)


def min_node(root: TreeNode) -> TreeNode:
    while root.left:
        root = root.left
    return root


def max_node(root: TreeNode) -> TreeNode:
    while root.right:
        root = root.right
    return root


def is_bst(root: TreeNode | None, lo: Any = None, hi: Any = None) -> bool:
    if root is None:
        return True
    if lo is not None and root.value <= lo:
        return False
    if hi is not None and root.value >= hi:
        return False
    return is_bst(root.left, lo, root.value) and is_bst(root.right, root.value, hi)


def is_balanced(root: TreeNode | None) -> bool:
    def check(node):
        if node is None:
            return 0
        left = check(node.left)
        if left == -1:
            return -1
        right = check(node.right)
        if right == -1:
            return -1
        if abs(left - right) > 1:
            return -1
        return 1 + max(left, right)
    return check(root) != -1


def from_list(values: list[Any]) -> TreeNode | None:
    root = None
    for v in values:
        root = insert(root, v)
    return root


def to_list(root: TreeNode | None) -> list[Any]:
    return inorder(root)


def pretty_print(root: TreeNode | None, prefix: str = "", is_left: bool = True) -> None:
    if root is None:
        return
    if root.right:
        pretty_print(root.right, prefix + ("    " if is_left else "|   "), False)
    print(prefix + ("`-- " if is_left else "/-- ") + str(root.value))
    if root.left:
        pretty_print(root.left, prefix + ("|   " if is_left else "    "), True)


if __name__ == "__main__":
    values = [5, 3, 7, 1, 4, 6, 8, 2]
    root = from_list(values)

    print("inorder:     ", inorder(root))
    print("preorder:    ", preorder(root))
    print("postorder:   ", postorder(root))
    print("level_order: ", level_order(root))
    print("height:      ", height(root))
    print("size:        ", size(root))
    print("min:         ", min_node(root).value)
    print("max:         ", max_node(root).value)
    print("is_bst:      ", is_bst(root))
    print("is_balanced: ", is_balanced(root))
    print("search(4):   ", search(root, 4))
    print("search(9):   ", search(root, 9))

    print("\ntree structure:")
    pretty_print(root)

    print("\nafter delete(5):")
    root = delete(root, 5)
    print("inorder:     ", inorder(root))
    pretty_print(root)
