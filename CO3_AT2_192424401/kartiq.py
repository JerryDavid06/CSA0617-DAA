"""KartIQ divide-and-conquer reference implementations (standard library only).

Orders are (timestamp, order_id) records in global arrival order. Scores are
finite comparable numbers. Matrices are nonempty equal-size square lists.
These transparent Python examples are not tuned native production kernels.
"""
import math
import random


def merge_sort_orders(orders, stats=None):
    """Return a stable ascending timestamp copy with one reusable merge buffer."""
    a = list(orders)
    auxiliary = [None] * len(a)
    comparisons = 0

    def sort(lo, hi):
        nonlocal comparisons
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        sort(lo, mid)
        sort(mid, hi)
        i, j, k = lo, mid, lo
        while i < mid and j < hi:
            comparisons += 1
            # Left-first equality is the essential stability rule.
            if a[i][0] <= a[j][0]:
                auxiliary[k] = a[i]
                i += 1
            else:
                auxiliary[k] = a[j]
                j += 1
            k += 1
        while i < mid:
            auxiliary[k] = a[i]
            i += 1
            k += 1
        while j < hi:
            auxiliary[k] = a[j]
            j += 1
            k += 1
        for k in range(lo, hi):
            a[k] = auxiliary[k]
    sort(0, len(a))
    if stats is not None:
        stats.update(comparisons=comparisons)
    return a


def partition_first_desc(scores, lo=0, hi=None):
    """First-pivot two-way partition for the sample; descending scores."""
    hi = len(scores) - 1 if hi is None else hi
    if lo < 0 or hi >= len(scores) or lo > hi:
        raise ValueError("Expected a valid nonempty inclusive range")
    pivot, boundary = scores[lo], lo + 1
    for scan in range(lo + 1, hi + 1):
        if scores[scan] > pivot:
            scores[boundary], scores[scan] = scores[scan], scores[boundary]
            boundary += 1
    scores[lo], scores[boundary - 1] = scores[boundary - 1], scores[lo]
    return boundary - 1


def first_pivot_sort(scores, stats=None):
    """Fault-prone pivot policy, executed iteratively to avoid recursion failure."""
    comparisons, stack = 0, [(0, len(scores) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo < hi:
            comparisons += hi - lo
            pivot = partition_first_desc(scores, lo, hi)
            stack.extend([(lo, pivot - 1), (pivot + 1, hi)])
    if stats is not None:
        stats.update(comparisons=comparisons)
    return scores


def _heap_sort_desc(a, lo, hi):
    """Min-heap extraction gives a descending inclusive subrange in place."""
    size = hi - lo + 1

    def sift(root, end):
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end and a[lo + child + 1] < a[lo + child]:
                child += 1
            if a[lo + root] <= a[lo + child]:
                return
            a[lo + root], a[lo + child] = a[lo + child], a[lo + root]
            root = child
    for root in range(size // 2 - 1, -1, -1):
        sift(root, size)
    for end in range(size - 1, 0, -1):
        a[lo], a[lo + end] = a[lo + end], a[lo]
        sift(0, end)


def sort_scores(scores, seed=606, cutoff=16, depth_limit=None, stats=None):
    """Descending random-pivot three-way introspective Quick Sort, in place.

    Small ranges use insertion sort; exhausted depth uses heap sort. Worst time
    O(n log n), pending-stack space O(log n). Equal-score order is unspecified.
    """
    if cutoff < 1:
        raise ValueError("cutoff must be positive")
    if depth_limit is None:
        depth_limit = 2 * (len(scores).bit_length() - 1) if scores else 0
    if depth_limit < 0:
        raise ValueError("depth_limit must be nonnegative")
    rng, stack = random.Random(seed), [(0, len(scores) - 1, depth_limit)]
    counts = dict(partitions=0, fallbacks=0, small_ranges=0)
    while stack:
        lo, hi, depth = stack.pop()
        if hi <= lo:
            continue
        if hi - lo + 1 <= cutoff:
            counts["small_ranges"] += 1
            for i in range(lo + 1, hi + 1):
                value, j = scores[i], i - 1
                while j >= lo and scores[j] < value:
                    scores[j + 1] = scores[j]
                    j -= 1
                scores[j + 1] = value
            continue
        if depth == 0:
            counts["fallbacks"] += 1
            _heap_sort_desc(scores, lo, hi)
            continue
        counts["partitions"] += 1
        pivot = scores[rng.randrange(lo, hi + 1)]
        left, scan, right = lo, lo, hi
        while scan <= right:
            if scores[scan] > pivot:
                scores[left], scores[scan] = scores[scan], scores[left]
                left += 1
                scan += 1
            elif scores[scan] < pivot:
                scores[scan], scores[right] = scores[right], scores[scan]
                right -= 1
            else:
                scan += 1
        ranges = [(lo, left - 1, depth - 1), (right + 1, hi, depth - 1)]
        # Process the smaller side next, bounding pending stack storage.
        ranges.sort(key=lambda item: item[1] - item[0], reverse=True)
        stack.extend(ranges)
    if stats is not None:
        stats.update(counts)
    return scores


def first_order_at_timestamp(orders, timestamp, stats=None):
    """First matching index or None; ascending timestamp order is required."""
    lo, hi, comparisons = 0, len(orders), 0
    while lo < hi:
        mid = (lo + hi) // 2
        comparisons += 1
        if orders[mid][0] < timestamp:
            lo = mid + 1
        else:
            hi = mid
    found = lo < len(orders)
    if found:
        comparisons += 1
        found = orders[lo][0] == timestamp
    if stats is not None:
        stats.update(timestamp_comparisons=comparisons)
    return lo if found else None


def _validate(a, b):
    n = len(a)
    if not n or len(b) != n or any(len(row) != n for row in list(a) + list(b)):
        raise ValueError("Expected nonempty square matrices of equal size")
    for matrix in (a, b):
        for row in matrix:
            for x in row:
                if not isinstance(x, (int, float)) or not math.isfinite(x):
                    raise ValueError("Expected finite numeric entries")
    return n


def _classical(a, b, counts):
    n = len(a)
    c = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            value = a[i][0] * b[0][j]
            counts["multiplications"] += 1
            for k in range(1, n):
                value += a[i][k] * b[k][j]
                counts["multiplications"] += 1
                counts["additions_subtractions"] += 1
            c[i][j] = value
    return c


def classical_multiply(a, b, stats=None):
    """n^3 scalar multiplies and n^2(n-1) adds for square matrices."""
    _validate(a, b)
    counts = dict(multiplications=0, additions_subtractions=0)
    c = _classical(a, b, counts)
    if stats is not None:
        stats.update(counts)
    return c


def strassen_multiply(a, b, cutoff=32, stats=None):
    """Seven-product Strassen with conventional leaves; zero-pad if necessary.

    cutoff=1 gives pure Strassen. Integer sample results are exact. Floating
    results need tolerance checks because summation order changes.
    """
    n = _validate(a, b)
    if cutoff < 1:
        raise ValueError("cutoff must be positive")
    size = 1 << (n - 1).bit_length()
    aa = [list(row) + [0] * (size - n) for row in a]
    bb = [list(row) + [0] * (size - n) for row in b]
    aa += [[0] * size for _ in range(size - n)]
    bb += [[0] * size for _ in range(size - n)]
    counts = dict(multiplications=0, additions_subtractions=0)

    def add(x, y, sign=1):
        counts["additions_subtractions"] += len(x) ** 2
        if sign == 1:
            return [[v + w for v, w in zip(rx, ry)] for rx, ry in zip(x, y)]
        return [[v - w for v, w in zip(rx, ry)] for rx, ry in zip(x, y)]

    def blocks(x):
        h = len(x) // 2
        return ([r[:h] for r in x[:h]], [r[h:] for r in x[:h]],
                [r[:h] for r in x[h:]], [r[h:] for r in x[h:]])

    def multiply(x, y):
        if len(x) <= cutoff:
            return _classical(x, y, counts)
        a11, a12, a21, a22 = blocks(x)
        b11, b12, b21, b22 = blocks(y)
        m1 = multiply(add(a11, a22), add(b11, b22))
        m2 = multiply(add(a21, a22), b11)
        m3 = multiply(a11, add(b12, b22, -1))
        m4 = multiply(a22, add(b21, b11, -1))
        m5 = multiply(add(a11, a12), b22)
        m6 = multiply(add(a21, a11, -1), add(b11, b12))
        m7 = multiply(add(a12, a22, -1), add(b21, b22))
        c11 = add(add(add(m1, m4), m5, -1), m7)
        c12, c21 = add(m3, m5), add(m2, m4)
        c22 = add(add(add(m1, m2, -1), m3), m6)
        return [l + r for l, r in zip(c11, c12)] + [
            l + r for l, r in zip(c21, c22)]
    c = multiply(aa, bb)
    if stats is not None:
        stats.update(counts, padded_size=size)
    return [row[:n] for row in c[:n]]


if __name__ == "__main__":
    orders = [(105, "O1"), (102, "O2"), (105, "O3"),
              (101, "O4"), (102, "O5"), (103, "O6")]
    ordered = merge_sort_orders(orders)
    print("Stable orders:", ordered)
    scores = [42, 17, 63, 8, 55, 29]
    partitioned = scores[:]
    print("First-pivot partition index:", partition_first_desc(partitioned))
    print("Partitioned descending:", partitioned)
    print("Final descending scores:", sort_scores(scores))
    print("First timestamp 102 index:", first_order_at_timestamp(ordered, 102))
    a, b, counts = [[1, 7], [3, 5]], [[1, 3], [7, 5]], {}
    print("Strassen sample:", strassen_multiply(a, b, 1, counts))
    print("Strassen scalar counts:", counts)
    print("Conventional sample:", classical_multiply(a, b))

