"""Directed routing and undirected MST algorithms with construction traces."""
import heapq
import itertools
import math


class NegativeCycleError(ValueError):
    """Reachable negative cycle prevents finite shortest-path answers."""


def _graph(vertices, edges):
    if len(set(vertices)) != len(vertices):
        raise ValueError("Vertex labels must be unique")
    labels = set(vertices)
    if any(u not in labels or v not in labels or not isinstance(w, (int, float))
           or not math.isfinite(w) for u, v, w in edges):
        raise ValueError("Every edge needs known endpoints and a finite weight")


def reconstruct_path(parent, source, target):
    """Return None when unreachable; reject a corrupt predecessor cycle."""
    route, seen, current = [], set(), target
    while current is not None:
        if current in seen:
            raise ValueError("Predecessor chain contains a cycle")
        seen.add(current)
        route.append(current)
        if current == source:
            return list(reversed(route))
        current = parent[current]
    return None


def dijkstra(vertices, edges, source, unsafe_negative_demo=False):
    """Heap Dijkstra. Negative inputs are rejected unless explicitly diagnostic."""
    _graph(vertices, edges)
    if source not in vertices:
        raise ValueError("Unknown source")
    if not unsafe_negative_demo and any(w < 0 for _, _, w in edges):
        raise ValueError("Dijkstra requires nonnegative edge weights")
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        adj[u].append((v, w))
    dist, parent = {v: math.inf for v in vertices}, {v: None for v in vertices}
    dist[source] = 0
    heap, final, order, trace, attempts = [(0, source)], set(), [], [], 0
    while heap:
        value, u = heapq.heappop(heap)
        if u in final or value != dist[u]:
            continue
        final.add(u)
        order.append(u)
        updates = []
        for v, w in adj[u]:
            attempts += 1
            if v not in final and value+w < dist[v]:
                updates.append(dict(vertex=v, old=dist[v], new=value+w, via=u))
                dist[v], parent[v] = value+w, u
                heapq.heappush(heap, (dist[v], v))
        trace.append(dict(finalised=u, distance=value, updates=updates))
    return dict(distances=dist, predecessors=parent, finalised=order,
                paths={v: reconstruct_path(parent, source, v) if dist[v] != math.inf else None
                       for v in vertices},
                trace=trace, stats=dict(edge_attempts=attempts, finalised=len(final)))


def bellman_ford(vertices, edges, source):
    """Repeated in-place relaxation, guarded by source reachability."""
    _graph(vertices, edges)
    if source not in vertices:
        raise ValueError("Unknown source")
    dist, parent = {v: math.inf for v in vertices}, {v: None for v in vertices}
    dist[source] = 0
    passes, attempts = [], 0
    for turn in range(len(vertices)-1):
        updates = []
        for u, v, w in edges:
            attempts += 1
            if dist[u] != math.inf and dist[u]+w < dist[v]:
                updates.append(dict(u=u, v=v, old=dist[v], new=dist[u]+w))
                dist[v], parent[v] = dist[u]+w, u
        passes.append(dict(pass_number=turn+1, updates=updates, distances=dist.copy()))
        if not updates:
            break
    for u, v, w in edges:
        if dist[u] != math.inf and dist[u]+w < dist[v]:
            raise NegativeCycleError(f"Reachable negative cycle: extra relaxation {u}->{v}")
    return dict(distances=dist, predecessors=parent,
                paths={v: reconstruct_path(parent, source, v) if dist[v] != math.inf else None
                       for v in vertices},
                passes=passes, stats=dict(edge_attempts=attempts, passes=len(passes)))


def floyd(vertices, edges):
    """All-pairs costs; do not publish finite results in a negative-cycle graph."""
    _graph(vertices, edges)
    n, ix = len(vertices), {v: i for i, v in enumerate(vertices)}
    d = [[math.inf]*n for _ in range(n)]
    for i in range(n):
        d[i][i] = 0
    for u, v, w in edges:
        i, j = ix[u], ix[v]
        d[i][j] = min(d[i][j], w)
    updates = []
    for k in range(n):
        changed = 0
        for i in range(n):
            for j in range(n):
                if d[i][k] != math.inf and d[k][j] != math.inf:
                    candidate = d[i][k]+d[k][j]
                    if candidate < d[i][j]:
                        d[i][j] = candidate
                        changed += 1
        updates.append(dict(intermediate=vertices[k], improvements=changed))
    if any(d[i][i] < 0 for i in range(n)):
        raise NegativeCycleError("Negative diagonal: finite all-pairs answers are unsafe")
    return dict(matrix=d, trace=updates, states=n**3)


def warshall(vertices, edges):
    """Reflexive directed reachability: the diagonal includes zero-edge paths."""
    _graph(vertices, edges)
    n, ix = len(vertices), {v: i for i, v in enumerate(vertices)}
    reach = [[i == j for j in range(n)] for i in range(n)]
    for u, v, _ in edges:
        reach[ix[u]][ix[v]] = True
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])
    return reach


class DSU:
    """Disjoint sets with path compression and rank."""
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, vertex):
        while self.parent[vertex] != vertex:
            self.parent[vertex] = self.parent[self.parent[vertex]]
            vertex = self.parent[vertex]
        return vertex

    def union(self, u, v):
        u, v = self.find(u), self.find(v)
        if u == v:
            return False
        if self.rank[u] < self.rank[v]:
            u, v = v, u
        self.parent[v] = u
        if self.rank[u] == self.rank[v]:
            self.rank[u] += 1
        return True


def _undirected(vertices, edges):
    _graph(vertices, edges)
    cleaned, seen = [], set()
    for u, v, w in edges:
        if u == v:
            continue
        u, v = sorted((u, v))
        if (u, v) in seen:
            raise ValueError("Use one edge per undirected endpoint pair")
        seen.add((u, v))
        cleaned.append((u, v, w))
    return cleaned


def _mst_result(vertices, selected, trace, **stats):
    if len(selected) != max(0, len(vertices)-1):
        raise ValueError("Disconnected graph has no spanning tree")
    return dict(edges=selected, cost=sum(e[2] for e in selected), trace=trace, stats=stats)


def kruskal(vertices, edges):
    """Grow a forest with the globally cheapest non-cycle edge."""
    edges = _undirected(vertices, edges)
    sets, chosen, trace = DSU(vertices), [], []
    for u, v, w in sorted(edges, key=lambda e: (e[2], e[0], e[1])):
        before = (sets.find(u), sets.find(v))
        accepted = sets.union(u, v)
        trace.append(dict(edge=(u, v, w), components=before, accepted=accepted))
        if accepted:
            chosen.append((u, v, w))
            if len(chosen) == len(vertices)-1:
                break
    return _mst_result(vertices, chosen, trace, edges_tested=len(trace))


def prim(vertices, edges, start=None):
    """Grow one tree; equal-weight frontier entries use insertion order."""
    edges = _undirected(vertices, edges)
    if not vertices:
        return _mst_result(vertices, [], [], heap_pops=0)
    start = vertices[0] if start is None else start
    if start not in vertices:
        raise ValueError("Unknown starting vertex")
    adj = {v: [] for v in vertices}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    visited, heap, serial, chosen, trace, pops = {start}, [], itertools.count(), [], [], 0

    def push(u):
        for v, w in adj[u]:
            if v not in visited:
                heapq.heappush(heap, (w, next(serial), u, v))
    push(start)
    while heap and len(visited) < len(vertices):
        w, _, u, v = heapq.heappop(heap)
        pops += 1
        if v in visited:
            continue
        trace.append(dict(edge=(u, v, w), cut=sorted(visited)))
        chosen.append((min(u, v), max(u, v), w))
        visited.add(v)
        push(v)
    return _mst_result(vertices, chosen, trace, heap_pops=pops)


def boruvka(vertices, edges):
    """Each component proposes a cheapest outgoing edge; union filters cycles."""
    edges = _undirected(vertices, edges)
    sets, selected, rounds = DSU(vertices), [], []
    while len(selected) < max(0, len(vertices)-1):
        cheapest = {}
        for edge in edges:
            u, v, w = edge
            a, b = sets.find(u), sets.find(v)
            if a == b:
                continue
            rank = (w, u, v)
            for root in (a, b):
                if root not in cheapest or rank < cheapest[root][0]:
                    cheapest[root] = (rank, edge)
        proposals = {r: item[1] for r, item in cheapest.items()}
        accepted = []
        for root in sorted(proposals):
            u, v, w = proposals[root]
            if sets.union(u, v):
                selected.append((u, v, w))
                accepted.append((u, v, w))
        rounds.append(dict(proposals=proposals, accepted=accepted))
        if not accepted:
            raise ValueError("Disconnected graph has no spanning tree")
    return _mst_result(vertices, selected, rounds, rounds=len(rounds),
                       edge_scans=len(edges)*len(rounds))

