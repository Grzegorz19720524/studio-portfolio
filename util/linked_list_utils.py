from typing import Any


class Node:
    def __init__(self, value: Any):
        self.value = value
        self.next: "Node | None" = None

    def __repr__(self) -> str:
        return f"Node({self.value!r})"


class LinkedList:
    def __init__(self):
        self.head: Node | None = None
        self._length: int = 0

    def append(self, value: Any) -> None:
        node = Node(value)
        if self.head is None:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._length += 1

    def prepend(self, value: Any) -> None:
        node = Node(value)
        node.next = self.head
        self.head = node
        self._length += 1

    def insert(self, index: int, value: Any) -> None:
        if index <= 0:
            self.prepend(value)
            return
        cur = self.head
        for _ in range(index - 1):
            if cur is None:
                break
            cur = cur.next
        if cur is None:
            self.append(value)
            return
        node = Node(value)
        node.next = cur.next
        cur.next = node
        self._length += 1

    def remove(self, value: Any) -> bool:
        if self.head is None:
            return False
        if self.head.value == value:
            self.head = self.head.next
            self._length -= 1
            return True
        cur = self.head
        while cur.next:
            if cur.next.value == value:
                cur.next = cur.next.next
                self._length -= 1
                return True
            cur = cur.next
        return False

    def pop(self) -> Any:
        if self.head is None:
            raise IndexError("pop from empty list")
        if self.head.next is None:
            val = self.head.value
            self.head = None
            self._length -= 1
            return val
        cur = self.head
        while cur.next and cur.next.next:
            cur = cur.next
        val = cur.next.value
        cur.next = None
        self._length -= 1
        return val

    def popleft(self) -> Any:
        if self.head is None:
            raise IndexError("pop from empty list")
        val = self.head.value
        self.head = self.head.next
        self._length -= 1
        return val

    def find(self, value: Any) -> Node | None:
        cur = self.head
        while cur:
            if cur.value == value:
                return cur
            cur = cur.next
        return None

    def reverse(self) -> None:
        prev, cur = None, self.head
        while cur:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        self.head = prev

    def to_list(self) -> list[Any]:
        result, cur = [], self.head
        while cur:
            result.append(cur.value)
            cur = cur.next
        return result

    def __len__(self) -> int:
        return self._length

    def __iter__(self):
        cur = self.head
        while cur:
            yield cur.value
            cur = cur.next

    def __repr__(self) -> str:
        return " -> ".join(str(v) for v in self) + " -> None"


def from_list(values: list[Any]) -> LinkedList:
    ll = LinkedList()
    for v in values:
        ll.append(v)
    return ll


def has_cycle(ll: LinkedList) -> bool:
    slow = fast = ll.head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False


def middle(ll: LinkedList) -> Any | None:
    slow = fast = ll.head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow.value if slow else None


def merge_sorted(a: LinkedList, b: LinkedList) -> LinkedList:
    dummy = Node(0)
    cur = dummy
    ca, cb = a.head, b.head
    while ca and cb:
        if ca.value <= cb.value:
            cur.next = Node(ca.value)
            ca = ca.next
        else:
            cur.next = Node(cb.value)
            cb = cb.next
        cur = cur.next
    while ca:
        cur.next = Node(ca.value)
        ca = ca.next
        cur = cur.next
    while cb:
        cur.next = Node(cb.value)
        cb = cb.next
        cur = cur.next
    result = LinkedList()
    result.head = dummy.next
    result._length = len(a) + len(b)
    return result


def remove_duplicates(ll: LinkedList) -> None:
    seen = set()
    cur = ll.head
    prev = None
    while cur:
        if cur.value in seen:
            prev.next = cur.next
            ll._length -= 1
        else:
            seen.add(cur.value)
            prev = cur
        cur = cur.next


if __name__ == "__main__":
    ll = from_list([1, 2, 3, 4, 5])
    print("list:        ", ll)
    print("len:         ", len(ll))
    print("to_list:     ", ll.to_list())

    ll.prepend(0)
    print("\nafter prepend(0):", ll)

    ll.insert(3, 99)
    print("after insert(3, 99):", ll)

    ll.remove(99)
    print("after remove(99):", ll)

    print("\npop:         ", ll.pop())
    print("popleft:     ", ll.popleft())
    print("after pops:  ", ll)

    print("\nfind(3):     ", ll.find(3))
    print("find(99):    ", ll.find(99))

    ll.reverse()
    print("reversed:    ", ll)

    print("\nmiddle:      ", middle(ll))

    print("\nhas_cycle:   ", has_cycle(ll))

    a = from_list([1, 3, 5, 7])
    b = from_list([2, 4, 6, 8])
    merged = merge_sorted(a, b)
    print("\nmerge_sorted:", merged)

    dup = from_list([1, 2, 2, 3, 3, 3, 4])
    remove_duplicates(dup)
    print("remove_duplicates:", dup)
