"""
DAA Assignment 1 - Reproducible Benchmark
Student: Jerry David
Registration No.: 192424401
Seed: 2401

Measures:
- preprocessing time
- search time
- total time
- comparisons/key operations
- correctness

Required sizes:
1,000 / 10,000 / 100,000 / 1,000,000

Task 12:
50,000 searches on 1,000,000 records.
"""

from pathlib import Path
import csv
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
CSV_OUT = RESULTS_DIR / "results.csv"

REG_NO = 192424401
NOT_FOUND_KEY = REG_NO + 1
SIZES = [1_000, 10_000, 100_000, 1_000_000]
TASK12_SEARCHES = 50_000

sys.path.insert(0, str(ROOT / "src"))
from algo1_linear_jerry import linear_search
from algo2_binary_jerry import binary_search
from algo3_hash_jerry import build_hash_table, hash_search

def load_records(n):
    path = DATA_DIR / f"students_{n}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run: python src/dataset_generator.py"
        )
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [int(row["registration_number"]) for row in reader]

def timed_call(fn):
    start = time.perf_counter_ns()
    result = fn()
    elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
    return result, elapsed_ms

def run_single_size(n, target):
    records = load_records(n)

    # Linear: no preprocessing.
    (found_l, ops_l), search_l_ms = timed_call(
        lambda: linear_search(records, target)
    )

    # Binary: preprocessing is sorting.
    (sorted_records, sort_ms) = timed_call(lambda: sorted(records))
    (found_b, ops_b), search_b_ms = timed_call(
        lambda: binary_search(sorted_records, target)
    )

    # Hash: preprocessing is table construction.
    (hash_table, hash_build_ms) = timed_call(lambda: build_hash_table(records))
    (found_h, ops_h), search_h_ms = timed_call(
        lambda: hash_search(hash_table, target)
    )

    expected = target in records
    assert found_l == expected
    assert found_b == expected
    assert found_h == expected

    rows = [
        {
            "experiment": "standard",
            "algorithm": "Linear Search",
            "n": n,
            "target_type": "OWN_REG_NO" if target == REG_NO else "OWN_REG_NO_PLUS_1",
            "target": target,
            "found": found_l,
            "preprocessing_ms": 0.0,
            "search_ms": search_l_ms,
            "total_ms": search_l_ms,
            "key_operations": ops_l,
        },
        {
            "experiment": "standard",
            "algorithm": "Recursive Binary Search",
            "n": n,
            "target_type": "OWN_REG_NO" if target == REG_NO else "OWN_REG_NO_PLUS_1",
            "target": target,
            "found": found_b,
            "preprocessing_ms": sort_ms,
            "search_ms": search_b_ms,
            "total_ms": sort_ms + search_b_ms,
            "key_operations": ops_b,
        },
        {
            "experiment": "standard",
            "algorithm": "Hash Table Search",
            "n": n,
            "target_type": "OWN_REG_NO" if target == REG_NO else "OWN_REG_NO_PLUS_1",
            "target": target,
            "found": found_h,
            "preprocessing_ms": hash_build_ms,
            "search_ms": search_h_ms,
            "total_ms": hash_build_ms + search_h_ms,
            "key_operations": ops_h,
        },
    ]
    return rows

def run_task12(n=1_000_000, number_of_searches=50_000):
    """
    Task 12 benchmark.

    The changed requirement is a high-frequency search workload. Running 50,000
    linear searches over 1M records would require an impractically large number
    of comparisons and would not be a useful way to benchmark the revised design.
    Therefore Task 12 compares the two viable indexed/sorted candidates:
    Recursive Binary Search and Hash Table Search.

    Preprocessing is measured separately below so the report can discuss whether
    the one-time cost is justified by repeated daily searches.
    """
    records = load_records(n)

    # Deterministic query set: 25,000 successful + 25,000 unsuccessful.
    successful_targets = records[:number_of_searches // 2]
    unsuccessful_targets = [NOT_FOUND_KEY] * (
        number_of_searches - len(successful_targets)
    )
    targets = successful_targets + unsuccessful_targets

    # Binary Search preprocessing: sort once.
    (sorted_records, binary_preprocess_ms) = timed_call(lambda: sorted(records))

    start = time.perf_counter_ns()
    binary_ops = 0
    binary_found = 0
    for target in targets:
        found, ops = binary_search(sorted_records, target)
        binary_found += int(found)
        binary_ops += ops
    binary_search_ms = (time.perf_counter_ns() - start) / 1_000_000

    # Hash preprocessing: build dictionary once.
    (hash_table, hash_preprocess_ms) = timed_call(lambda: build_hash_table(records))

    start = time.perf_counter_ns()
    hash_ops = 0
    hash_found = 0
    for target in targets:
        found, ops = hash_search(hash_table, target)
        hash_found += int(found)
        hash_ops += ops
    hash_search_ms = (time.perf_counter_ns() - start) / 1_000_000

    return [
        {
            "experiment": "task12_50000_searches",
            "algorithm": "Recursive Binary Search",
            "n": n,
            "target_type": "MIXED_50K",
            "target": "50,000 deterministic queries",
            "found": f"{binary_found}/{number_of_searches}",
            "preprocessing_ms": binary_preprocess_ms,
            "search_ms": binary_search_ms,
            "total_ms": binary_preprocess_ms + binary_search_ms,
            "key_operations": binary_ops,
        },
        {
            "experiment": "task12_50000_searches",
            "algorithm": "Hash Table Search",
            "n": n,
            "target_type": "MIXED_50K",
            "target": "50,000 deterministic queries",
            "found": f"{hash_found}/{number_of_searches}",
            "preprocessing_ms": hash_preprocess_ms,
            "search_ms": hash_search_ms,
            "total_ms": hash_preprocess_ms + hash_search_ms,
            "key_operations": hash_ops,
        },
    ]

def write_results(rows):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment", "algorithm", "n", "target_type", "target", "found",
        "preprocessing_ms", "search_ms", "total_ms", "key_operations"
    ]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = []

    print("=" * 72)
    print("DAA ASSIGNMENT 1 - BENCHMARK")
    print("Name: Jerry David")
    print("Reg No: 192424401")
    print("Personal Seed: 2401")
    print("Date/Time is supplied by the operating system/terminal.")
    print("=" * 72)

    for n in SIZES:
        print(f"\nDataset Size: {n:,}")
        print("-" * 72)
        for target in (REG_NO, NOT_FOUND_KEY):
            label = "OWN_REG_NO" if target == REG_NO else "OWN_REG_NO_PLUS_1"
            print(f"\nTarget: {target} ({label})")
            rows = run_single_size(n, target)
            all_rows.extend(rows)
            for row in rows:
                print(
                    f"{row['algorithm']:<25} "
                    f"found={row['found']!s:<5} "
                    f"preprocess={row['preprocessing_ms']:.4f} ms  "
                    f"search={row['search_ms']:.4f} ms  "
                    f"total={row['total_ms']:.4f} ms  "
                    f"ops={row['key_operations']}"
                )

    print("\n" + "=" * 72)
    print("TASK 12 - 50,000 SEARCHES ON 1,000,000 RECORDS")
    print("=" * 72)
    task12_rows = run_task12()
    all_rows.extend(task12_rows)
    for row in task12_rows:
        print(
            f"{row['algorithm']:<25} "
            f"search={row['search_ms']:.4f} ms  "
            f"ops={row['key_operations']}  "
            f"found={row['found']}"
        )

    write_results(all_rows)
    print(f"\nResults written to: {CSV_OUT}")

if __name__ == "__main__":
    main()
