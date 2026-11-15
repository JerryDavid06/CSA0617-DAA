"""Assignment 4B optimisation algorithms, separated from fixtures and output.

Python 3.10+, standard library only. Functions return reconstruction and
instrumentation as ordinary dictionaries; invalid inputs raise ValueError.
"""
from functools import cmp_to_key
from fractions import Fraction
import math


def word_wrap(words, width, power=2):
    """Minimum suffix DP; final line costs zero. Width counts characters."""
    if not isinstance(width, int) or width < 1 or power not in (2, 3):
        raise ValueError("Positive integer width and penalty power 2 or 3 required")
    if any(not isinstance(w, str) or not w or any(c.isspace() for c in w) for w in words):
        raise ValueError("Words must be nonempty tokens without whitespace")
    if any(len(w) > width for w in words):
        raise ValueError("A word exceeds the line width; splitting is not enabled")
    n = len(words)
    cost, end = [math.inf] * n + [0], [-1] * n
    traces, feasible, considered = [], 0, 0
    for i in range(n - 1, -1, -1):
        used = 0
        options = []
        for j in range(i, n):
            considered += 1
            used += len(words[j]) + int(j > i)
            if used > width:
                break
            feasible += 1
            unused = width - used
            penalty = 0 if j == n - 1 else unused ** power
            candidate = penalty + cost[j + 1]
            options.append(dict(end=j, unused=unused, line_penalty=penalty,
                                suffix_cost=cost[j + 1], total=candidate))
            if candidate < cost[i]:
                cost[i], end[i] = candidate, j
        traces.append(dict(start=i, best_end=end[i], optimum=cost[i], candidates=options))
    lines, i = [], 0
    while i < n:
        j = end[i]
        unused = width - sum(map(len, words[i:j + 1])) - (j - i)
        lines.append(dict(words=words[i:j + 1], unused=unused,
                          penalty=0 if j == n - 1 else unused ** power))
        i = j + 1
    return dict(cost=cost[0], lines=lines, dp=cost, trace=traces,
                stats=dict(states=n, candidates=considered, feasible_candidates=feasible,
                           stored_dp_and_choice_slots=2*n+1))


def _items(items, capacity):
    if not isinstance(capacity, int) or capacity < 0:
        raise ValueError("Nonnegative integer capacity required")
    if len({i[0] for i in items}) != len(items):
        raise ValueError("Item IDs must be unique")
    if any(not isinstance(w, int) or isinstance(w, bool) or w <= 0 or
           not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0
           for _, w, v in items):
        raise ValueError("Positive integer weights and finite nonnegative values required")


def _density_order(items, stats):
    def compare(a, b):
        stats["ratio_comparisons"] += 1
        x, y = a[2] * b[1], b[2] * a[1]
        if x != y:
            return -1 if x > y else 1
        return 0  # Python's stable sort retains input order on density ties.
    return sorted(items, key=cmp_to_key(compare))


def fractional_knapsack(items, capacity):
    """Density greedy for divisible items; fractions are reported explicitly."""
    _items(items, capacity)
    stats = dict(ratio_comparisons=0, items_examined=0)
    order = _density_order(items, stats)
    remaining, total, selected, trace = Fraction(capacity), 0, [], []
    for identity, weight, value in order:
        if remaining <= 0:
            break
        stats["items_examined"] += 1
        fraction = min(Fraction(1), remaining / weight)
        remaining -= fraction * weight
        gain = fraction * value
        total += gain
        selected.append(dict(id=identity, fraction=str(fraction),
                             weight=float(fraction*weight), value=float(gain)))
        trace.append(dict(id=identity, density=value/weight, fraction=str(fraction),
                          remaining=float(remaining), value_so_far=float(total)))
    stats["output_items"] = len(selected)
    return dict(value=float(total), selected=selected, trace=trace, stats=stats)


def greedy_01(items, capacity, best_single=False):
    """Fast 0/1 heuristic; skip nonfitting items. Optional singleton safeguard."""
    _items(items, capacity)
    stats = dict(ratio_comparisons=0, items_examined=0)
    order = _density_order(items, stats)
    remaining, value, selected, trace = capacity, 0, [], []
    for identity, weight, benefit in order:
        stats["items_examined"] += 1
        take = weight <= remaining
        if take:
            remaining -= weight
            value += benefit
            selected.append(identity)
        trace.append(dict(id=identity, take=take, remaining=remaining, value=value))
    if best_single:
        feasible = [x for x in items if x[1] <= capacity]
        singleton = max(feasible, key=lambda x: x[2], default=None)
        if singleton and singleton[2] > value:
            selected, value, remaining = [singleton[0]], singleton[2], capacity-singleton[1]
    return dict(value=value, selected=selected, weight=capacity-remaining,
                trace=trace, stats=stats)


def knapsack_01(items, capacity):
    """Exact table DP with traceback; positive integer weights, each item once."""
    _items(items, capacity)
    n = len(items)
    if (n+1)*(capacity+1) > 5_000_000:
        raise ValueError("DP table exceeds the reference implementation's cell budget")
    dp = [[0]*(capacity+1) for _ in range(n+1)]
    transitions = includes = 0
    for i, (_, weight, value) in enumerate(items, 1):
        for c in range(capacity+1):
            transitions += 1
            dp[i][c] = dp[i-1][c]
            if weight <= c:
                includes += 1
                dp[i][c] = max(dp[i][c], value+dp[i-1][c-weight])
    chosen, c, back = [], capacity, []
    for i in range(n, 0, -1):
        take = dp[i][c] > dp[i-1][c]
        back.append(dict(item=items[i-1][0], capacity=c, take=take,
                         optimum=dp[i][c], exclude=dp[i-1][c]))
        if take:
            chosen.append(items[i-1][0])
            c -= items[i-1][1]
    chosen.reverse()
    return dict(value=dp[n][capacity], selected=chosen, weight=capacity-c,
                dp=dp, traceback=back,
                stats=dict(states_evaluated=transitions, include_alternatives=includes,
                           table_cells=(n+1)*(capacity+1)))


def assembly_schedule(processing, transfer, entry, exit_times):
    """Two lines; transfer[l][j] leaves line l after station j (zero-based)."""
    if len(processing) != 2 or not processing[0] or len(processing[0]) != len(processing[1]):
        raise ValueError("Two equally long, nonempty processing rows required")
    n = len(processing[0])
    if len(transfer) != 2 or any(len(r) != n-1 for r in transfer) or len(entry) != 2 or len(exit_times) != 2:
        raise ValueError("Transfer, entry or exit dimensions are inconsistent")
    values = list(entry)+list(exit_times)+[x for row in processing+transfer for x in row]
    if any(not isinstance(x, (int, float)) or not math.isfinite(x) or x < 0 for x in values):
        raise ValueError("All times must be finite and nonnegative")
    f = [[0]*n for _ in range(2)]
    parent = [[None]*n for _ in range(2)]
    f[0][0], f[1][0] = entry[0]+processing[0][0], entry[1]+processing[1][0]
    trace = []
    for j in range(1, n):
        choices = []
        for line in range(2):
            other = 1-line
            stay = f[line][j-1]+processing[line][j]
            switch = f[other][j-1]+transfer[other][j-1]+processing[line][j]
            parent[line][j] = line if stay <= switch else other
            f[line][j] = min(stay, switch)
            choices.append(dict(line=line+1, stay=stay, transfer=switch,
                                selected="stay" if stay <= switch else "transfer",
                                optimum=f[line][j]))
        trace.append(dict(station=j+1, choices=choices))
    totals = [f[l][-1]+exit_times[l] for l in range(2)]
    line = 0 if totals[0] <= totals[1] else 1
    route = [line+1]
    for j in range(n-1, 0, -1):
        line = parent[line][j]
        route.append(line+1)
    route.reverse()
    changes = [dict(after_station=j, from_line=route[j-1], to_line=route[j])
               for j in range(1, n) if route[j-1] != route[j]]
    return dict(time=min(totals), route=route, transfers=changes, dp=f,
                trace=trace, exit_totals=totals,
                stats=dict(states=2*n, predecessor_slots=2*n))


def held_karp(cost):
    """Exact TSP from hub 0; masks contain only deliveries 1..m.

    Count all valid (mask,last) states, excluding the conceptual hub base.
    The conservative guard prevents accidental production-scale exact runs.
    """
    n = len(cost)
    if not n or any(len(row) != n for row in cost):
        raise ValueError("A nonempty square cost matrix is required")
    if any(cost[i][i] != 0 for i in range(n)):
        raise ValueError("The diagonal must be zero")
    if any(not isinstance(x, (int, float)) or math.isnan(x) or x < 0 for row in cost for x in row):
        raise ValueError("Nonnegative costs or positive infinity required")
    m = n-1
    if m > 16:
        raise ValueError("Exact DP is limited to 16 deliveries; do not run it for 200")
    if not m:
        return dict(cost=0, route=[0, 0], stats=dict(states=0, transitions=0), dp={}, parent={})
    dp, parent, transitions = {}, {}, 0
    for mask in range(1, 1 << m):
        for j in range(m):
            if not mask & (1 << j):
                continue
            previous = mask ^ (1 << j)
            if previous == 0:
                dp[mask, j], parent[mask, j] = cost[0][j+1], -1
                continue
            best, predecessor = math.inf, None
            for k in range(m):
                if previous & (1 << k):
                    transitions += 1
                    candidate = dp[previous, k]+cost[k+1][j+1]
                    if candidate < best:
                        best, predecessor = candidate, k
            dp[mask, j], parent[mask, j] = best, predecessor
    full = (1 << m)-1
    last = min(range(m), key=lambda j: (dp[full, j]+cost[j+1][0], j))
    optimum = dp[full, last]+cost[last+1][0]
    if math.isinf(optimum):
        return dict(cost=math.inf, route=None,
                    stats=dict(states=len(dp), transitions=transitions), dp=dp, parent=parent)
    mask, reverse = full, []
    while mask:
        reverse.append(last+1)
        predecessor = parent[mask, last]
        mask ^= 1 << last
        if mask:
            last = predecessor
    return dict(cost=optimum, route=[0]+list(reversed(reverse))+[0],
                stats=dict(states=len(dp), transitions=transitions,
                           dp_and_parent_entries=2*len(dp)), dp=dp, parent=parent)

