import heapq
from collections import deque
from typing import Any


class Queue:
    def __init__(self, maxsize: int = 0):
        self._queue: deque = deque()
        self._maxsize = maxsize

    def enqueue(self, item: Any) -> bool:
        if self._maxsize and len(self._queue) >= self._maxsize:
            return False
        self._queue.append(item)
        return True

    def dequeue(self) -> Any:
        if not self._queue:
            raise IndexError("dequeue from empty queue")
        return self._queue.popleft()

    def peek(self) -> Any:
        if not self._queue:
            raise IndexError("peek from empty queue")
        return self._queue[0]

    def is_empty(self) -> bool:
        return len(self._queue) == 0

    def is_full(self) -> bool:
        return bool(self._maxsize and len(self._queue) >= self._maxsize)

    def size(self) -> int:
        return len(self._queue)

    def clear(self) -> None:
        self._queue.clear()

    def __repr__(self) -> str:
        return f"Queue(size={self.size()}, maxsize={self._maxsize})"


class PriorityQueue:
    def __init__(self):
        self._heap: list = []
        self._counter = 0

    def push(self, item: Any, priority: int = 0) -> None:
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self) -> Any:
        if not self._heap:
            raise IndexError("pop from empty priority queue")
        return heapq.heappop(self._heap)[2]

    def peek(self) -> Any:
        if not self._heap:
            raise IndexError("peek from empty priority queue")
        return self._heap[0][2]

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        return f"PriorityQueue(size={self.size()})"


if __name__ == "__main__":
    print("--- Queue ---")
    q = Queue(maxsize=3)
    print(q.enqueue("a"))
    print(q.enqueue("b"))
    print(q.enqueue("c"))
    print("full:", q.is_full())
    print("rejected:", not q.enqueue("d"))
    print("peek:", q.peek())
    print("dequeue:", q.dequeue())
    print("size:", q.size())
    print(q)

    print("\n--- PriorityQueue ---")
    pq = PriorityQueue()
    pq.push("low priority task", priority=10)
    pq.push("high priority task", priority=1)
    pq.push("medium priority task", priority=5)
    print("peek:", pq.peek())
    print("pop:", pq.pop())
    print("pop:", pq.pop())
    print("pop:", pq.pop())
    print(pq)
