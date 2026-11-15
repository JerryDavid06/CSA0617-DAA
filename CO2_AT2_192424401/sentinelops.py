"""SentinelOps alert triage, with corrected teaching baselines and optimisations.

Coordinates must be finite int/float values within +/- 10**12 kilometres in a
common planar system. This bound prevents overflow in squared distances.
Closest-pair ties use the lexicographically smallest original index pair.
Functions accept indexable sequences; sorting updates and returns its input list.
"""
import math


def insertion_sort_alerts(alerts, stats=None):
    """Stable descending insertion sort; count severity comparisons if requested."""
    comparisons = shifts = 0
    for i in range(1, len(alerts)):
        key = alerts[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if alerts[j][1] >= key[1]:
                break
            alerts[j + 1] = alerts[j]
            shifts += 1
            j -= 1
        alerts[j + 1] = key
    if stats is not None:
        stats.update(comparisons=comparisons, shifts=shifts)
    return alerts


def sort_alerts(alerts):
    """Stable descending severity sort in place; return the same list."""
    alerts.sort(key=lambda alert: alert[1], reverse=True)
    return alerts


def is_blocked_linear(blocklist, ip):
    """Corrected sequential membership search, including an empty blocklist."""
    for address in blocklist:
        if address == ip:
            return True
    return False


def build_blocklist(addresses):
    """Build an immutable lookup snapshot; rebuild when the source list changes."""
    return frozenset(addresses)


def is_blocked(blocklist, ip):
    """Test exact address membership; use a prebuilt set for repeated queries."""
    return ip in blocklist


def find_signature(log, pattern):
    """Return all overlapping starting positions using early-exit brute force.

    The empty pattern occurs at every boundary, including len(log).
    """
    n, m = len(log), len(pattern)
    hits = []
    for i in range(n - m + 1):
        for j in range(m):
            if log[i + j] != pattern[j]:
                break
        else:  # Runs only when the alignment has no mismatching character.
            hits.append(i)
    return hits


def _validate_events(events):
    for point in events:
        if len(point) != 2 or not all(
                isinstance(v, (int, float)) and not isinstance(v, bool)
                and abs(v) <= 10**12 and math.isfinite(v) for v in point):
            raise ValueError('Expected two finite int/float coordinates within +/- 10**12 km')


def closest_logins_bruteforce(events, stats=None):
    """Corrected quadratic reference; one square root for every unordered pair."""
    _validate_events(events)
    best, pair, distances = math.inf, None, 0
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            distance = math.sqrt((events[i][0] - events[j][0]) ** 2 +
                                 (events[i][1] - events[j][1]) ** 2)
            distances += 1
            if distance < best:
                best, pair = distance, (i, j)
    if stats is not None:
        stats.update(distances=distances, square_roots=distances)
    return pair, best


def closest_logins(events, stats=None):
    """X-sorted pruning preserving the baseline's rounded-distance tie semantics.

    Worst-case time is O(n**2); storage is O(n). Equality is retained during
    pruning so the earliest original index pair wins every distance tie.
    """
    _validate_events(events)
    points = sorted((x, y, i) for i, (x, y) in enumerate(events))
    best, limit, pair = math.inf, math.inf, None
    distances = checks = roots = 0
    for a, (x, y, i) in enumerate(points):
        for b in range(a + 1, len(points)):
            xx, yy, j = points[b]
            checks += 1
            dx2 = (xx - x) ** 2
            if dx2 > limit:
                break  # All later x coordinates are at least as far away.
            dy2 = (yy - y) ** 2
            if dy2 > limit:
                continue
            d2 = dx2 + dy2
            distances += 1
            if d2 > limit:
                continue
            # A root is needed only for a possible improvement or rounded tie.
            distance = math.sqrt(d2)
            roots += 1
            candidate = (min(i, j), max(i, j))
            if distance < best or (distance == best and
                                   (pair is None or candidate < pair)):
                best, pair = distance, candidate
                # Keep a conservative bound above every value rounding to best.
                # Padding prevents a rounded-distance tie from being pruned.
                limit = math.nextafter(math.nextafter(best, math.inf) ** 2,
                                       math.inf)
    if stats is not None:
        stats.update(distances=distances, candidate_checks=checks,
                     square_roots=roots)
    return pair, best


if __name__ == '__main__':
    alerts = [('A1', 3), ('A2', 9), ('A3', 5), ('A4', 9), ('A5', 1)]
    blocked = build_blocklist(['10.0.0.5', '10.0.0.9', '172.16.4.2'])
    print('Alerts:', sort_alerts(alerts))
    print('Blocked:', [is_blocked(blocked, q) for q in
                       ['10.0.0.9', '10.0.0.5', '8.8.8.8']])
    print('Signature:', find_signature('FAILFAIXFAIL', 'FAIL'))
    print('Closest:', closest_logins([(2, 3), (12, 30), (40, 50),
                                      (5, 1), (12, 10), (3, 4)]))
