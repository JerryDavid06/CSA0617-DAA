"""Reproduce deterministic benchmarks; writes benchmark_results.json.

Run beside sentinelops.py. Timings are median wall time over three executions;
input generation is excluded, validation/instrumentation is included.
"""
import json
import platform
import random
import statistics
import time
from pathlib import Path
import sentinelops as s


def measure(fn, data):
    times = []
    for _ in range(3):
        stats = {}
        started = time.perf_counter()
        result = fn(data, stats)
        times.append(time.perf_counter() - started)
    return result, stats, statistics.median(times)


def main():
    output = {'python': platform.python_version(), 'platform': platform.platform(),
              'seed': 606, 'repeats': 3, 'closest': [], 'insertion': []}
    rng = random.Random(606)
    points = [(rng.randrange(1000000), rng.randrange(1000000)) for _ in range(8000)]
    print('CLOSEST LOGINS | median seconds | full distance evaluations')
    for n in (1000, 2000, 4000, 8000):
        data = points[:n]
        ref, brute, bt = measure(s.closest_logins_bruteforce, data)
        got, opt, ot = measure(s.closest_logins, data)
        assert ref == got
        assert brute['distances'] == n * (n - 1) // 2
        row = dict(n=n, brute=brute, optimised=opt, brute_seconds=bt,
                   optimised_seconds=ot, pair=got[0], distance=got[1])
        output['closest'].append(row)
        print(f"{n:5} | brute {bt:.6f}s {brute['distances']:9} | "
              f"opt {ot:.6f}s {opt['distances']:5} | checks {opt['candidate_checks']}")
    print('INSERTION SORT | median seconds | severity comparisons | shifts')
    for n in (1000, 2000, 4000, 8000):
        ordered = [(str(i), n - i) for i in range(n)]
        nearly = ordered[:]
        for i in range(0, n - 1, 100):
            nearly[i], nearly[i + 1] = nearly[i + 1], nearly[i]
        shuffled = ordered[:]
        random.Random(606 + n).shuffle(shuffled)
        for label, source in [('nearly', nearly), ('random', shuffled)]:
            def run(data, stats):
                return s.insertion_sort_alerts(data[:], stats)
            result, counts, elapsed = measure(run, source)
            assert result == ordered
            output['insertion'].append(dict(n=n, distribution=label,
                                            seconds=elapsed, **counts))
            print(f"{n:5} | {label:6} {elapsed:.6f}s | "
                  f"{counts['comparisons']:9} | {counts['shifts']:9}")
    Path('benchmark_results.json').write_text(json.dumps(output, indent=2))
    print('All benchmark outputs matched corrected reference outputs.')


if __name__ == '__main__':
    main()
