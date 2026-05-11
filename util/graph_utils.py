from collections import defaultdict, deque
import heapq
from typing import Any


class Graph:
    def __init__(self, directed: bool = False):
        self.directed = directed
        self._adj: dict[Any, dict[Any, float]] = defaultdict(dict)

    def add_node(self, node: Any) -> None:
        if node not in self._adj:
            self._adj[node] = {}

    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        self.add_node(v)
        self._adj[u][v] = weight
        if not self.directed:
            self._adj[v][u] = weight

    def remove_edge(self, u: Any, v: Any) -> None:
        self._adj[u].pop(v, None)
        if not self.directed:
            self._adj[v].pop(u, None)

    def neighbors(self, node: Any) -> list[Any]:
        return list(self._adj[node].keys())

    def nodes(self) -> list[Any]:
        return list(self._adj.keys())

    def edges(self) -> list[tuple]:
        seen = set()
        result = []
        for u, nbrs in self._adj.items():
            for v, w in nbrs.items():
                key = (u, v) if self.directed else tuple(sorted([str(u), str(v)]))
                if key not in seen:
                    seen.add(key)
                    result.append((u, v, w))
        return result

    def has_node(self, node: Any) -> bool:
        return node in self._adj

    def has_edge(self, u: Any, v: Any) -> bool:
        return v in self._adj.get(u, {})

    def degree(self, node: Any) -> int:
        return len(self._adj[node])

    def __len__(self) -> int:
        return len(self._adj)


def bfs(graph: Graph, start: Any) -> list[Any]:
    visited, queue, order = {start}, deque([start]), []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nbr in graph.neighbors(node):
            if nbr not in visited:
                visited.add(nbr)
                queue.append(nbr)
    return order


def dfs(graph: Graph, start: Any) -> list[Any]:
    visited, stack, order = set(), [start], []
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            order.append(node)
            for nbr in reversed(graph.neighbors(node)):
                if nbr not in visited:
                    stack.append(nbr)
    return order


def shortest_path(graph: Graph, start: Any, end: Any) -> list[Any] | None:
    prev = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == end:
            path = []
            while node is not None:
                path.append(node)
                node = prev[node]
            return list(reversed(path))
        for nbr in graph.neighbors(node):
            if nbr not in prev:
                prev[nbr] = node
                queue.append(nbr)
    return None


def dijkstra(graph: Graph, start: Any) -> dict[Any, float]:
    dist = {node: float("inf") for node in graph.nodes()}
    dist[start] = 0.0
    heap = [(0.0, start)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue
        for nbr, w in graph._adj[node].items():
            nd = d + w
            if nd < dist[nbr]:
                dist[nbr] = nd
                heapq.heappush(heap, (nd, nbr))
    return dist


def has_cycle(graph: Graph) -> bool:
    visited = set()

    def dfs_cycle(node, parent):
        visited.add(node)
        for nbr in graph.neighbors(node):
            if nbr not in visited:
                if dfs_cycle(nbr, node):
                    return True
            elif nbr != parent:
                return True
        return False

    for node in graph.nodes():
        if node not in visited:
            if dfs_cycle(node, None):
                return True
    return False


def is_connected(graph: Graph) -> bool:
    nodes = graph.nodes()
    if not nodes:
        return True
    return len(bfs(graph, nodes[0])) == len(nodes)


def topological_sort(graph: Graph) -> list[Any]:
    in_degree = {n: 0 for n in graph.nodes()}
    for u, v, _ in graph.edges():
        in_degree[v] += 1
    queue = deque(n for n, d in in_degree.items() if d == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nbr in graph.neighbors(node):
            in_degree[nbr] -= 1
            if in_degree[nbr] == 0:
                queue.append(nbr)
    if len(order) != len(graph.nodes()):
        raise ValueError("Graph has a cycle — topological sort not possible")
    return order


if __name__ == "__main__":
    g = Graph()
    for edge in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E")]:
        g.add_edge(*edge)

    print("nodes:           ", g.nodes())
    print("edges:           ", [(u, v) for u, v, _ in g.edges()])
    print("degree(D):       ", g.degree("D"))
    print("has_edge(A,B):   ", g.has_edge("A", "B"))
    print("has_edge(A,E):   ", g.has_edge("A", "E"))

    print("\nbfs from A:      ", bfs(g, "A"))
    print("dfs from A:      ", dfs(g, "A"))
    print("shortest A->E:   ", shortest_path(g, "A", "E"))
    print("shortest A->D:   ", shortest_path(g, "A", "D"))

    wg = Graph()
    wg.add_edge("A", "B", 1)
    wg.add_edge("A", "C", 4)
    wg.add_edge("B", "C", 2)
    wg.add_edge("B", "D", 5)
    wg.add_edge("C", "D", 1)
    print("\ndijkstra from A: ", dijkstra(wg, "A"))

    print("\nhas_cycle(g):    ", has_cycle(g))
    cyclic = Graph()
    cyclic.add_edge("X", "Y")
    cyclic.add_edge("Y", "Z")
    cyclic.add_edge("Z", "X")
    print("has_cycle(cyclic):", has_cycle(cyclic))

    print("\nis_connected(g): ", is_connected(g))

    dag = Graph(directed=True)
    for edge in [("A", "C"), ("B", "C"), ("C", "D"), ("C", "E"), ("D", "F")]:
        dag.add_edge(*edge)
    print("\ntopological_sort:", topological_sort(dag))
