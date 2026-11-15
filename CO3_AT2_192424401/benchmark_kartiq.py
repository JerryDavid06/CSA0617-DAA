"""Reproducible small-scale experiments, not production-scale latency claims."""
import json
import math
import platform
import random
import statistics
import time
from pathlib import Path
import kartiq as k


def timed(fn):
    samples = []
    for _ in range(3):
        start = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - start)
    return result, statistics.median(samples)


def main():
    result = dict(python=platform.python_version(), platform=platform.platform(),
                  repeats=3, quicksort=[], matrices=[], calculations={})
    print("QUICK SORT: already descending distinct scores; median of three calls")
    for n in (256, 512, 1024, 2048):
        data = list(range(n, 0, -1))
        baseline, bt = timed(lambda: k.first_pivot_sort(data[:]))
        improved, it = timed(lambda: k.sort_scores(data[:]))
        counts = {}
        k.first_pivot_sort(data[:], counts)
        assert baseline == improved == data
        assert counts["comparisons"] == n * (n - 1) // 2
        result["quicksort"].append(dict(n=n, first_comparisons=counts["comparisons"],
                                        first_seconds=bt, improved_seconds=it))
        print(n, counts["comparisons"], f"first={bt:.6f}s hybrid={it:.6f}s")
    print("MATRIX: fixed integer inputs; cutoff 16; exact equality checked")
    rng = random.Random(606)
    for n in (16, 32, 64, 128):
        a = [[rng.randrange(-5, 6) for _ in range(n)] for _ in range(n)]
        b = [[rng.randrange(-5, 6) for _ in range(n)] for _ in range(n)]
        ref, ct = timed(lambda: k.classical_multiply(a, b))
        got, st = timed(lambda: k.strassen_multiply(a, b, cutoff=16))
        assert got == ref
        counts = {}
        k.strassen_multiply(a, b, cutoff=16, stats=counts)
        result["matrices"].append(dict(n=n, classical_seconds=ct,
                                       hybrid_seconds=st, **counts))
        print(n, counts, f"classical={ct:.6f}s hybrid={st:.6f}s")
    n = 10000000
    h = (n - 1).bit_length()
    calc = result["calculations"]
    calc.update(merge_height=h, merge_nlogn=n*math.log2(n),
                merge_worst=n*h-2**h+1,
                binary_loop_max=h, binary_total_max=h+1,
                quick_worst=100000*99999//2,
                quick_random_expected=2*100001*sum(1/i for i in range(1,100001))-400000,
                strassen_1024_multiplications=7**10,
                conventional_1024_multiplications=1024**3,
                strassen_1024_additions=6*(7**10-1024**2),
                conventional_1024_additions=1024**2*(1024-1),
                hybrid_1024_cutoff64_multiplications=7**4*64**3)
    calc["strassen_multiplication_reduction_percent"] = 100*(1-(7/8)**10)
    print("VERIFIED LARGE-INPUT CALCULATIONS", json.dumps(calc, indent=2))
    Path("measurements.json").write_text(json.dumps(result, indent=2))
    print("All measured outputs match reference results.")


if __name__ == "__main__":
    main()

