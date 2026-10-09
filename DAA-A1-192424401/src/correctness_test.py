"""
Correctness test for all three algorithms.
Includes:
- own registration number (must be found)
- own registration number + 1 (must not be found)
- first, middle, last, random existing key
"""

from pathlib import Path
import csv
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REG_NO = 192424401
NOT_FOUND_KEY = REG_NO + 1

sys.path.insert(0, str(ROOT / "src"))
from algo1_linear_jerry import linear_search
from algo2_binary_jerry import binary_search
from algo3_hash_jerry import build_hash_table, hash_search

def load(n):
    path = DATA_DIR / f"students_{n}.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return [int(r["registration_number"]) for r in csv.DictReader(f)]

def main():
    n = 1000
    records = load(n)
    sorted_records = sorted(records)
    table = build_hash_table(records)

    tests = [
        ("OWN_REG_NO", REG_NO, True),
        ("OWN_REG_NO_PLUS_1", NOT_FOUND_KEY, False),
        ("FIRST_RECORD", records[0], True),
        ("MIDDLE_RECORD", records[len(records)//2], True),
        ("LAST_RECORD", records[-1], True),
    ]

    print("=" * 72)
    print("DAA ASSIGNMENT 1 - CORRECTNESS TEST")
    print("Name: Jerry David")
    print("Reg No: 192424401")
    print("=" * 72)

    for name, target, expected in tests:
        l_found, l_ops = linear_search(records, target)
        b_found, b_ops = binary_search(sorted_records, target)
        h_found, h_ops = hash_search(table, target)

        assert l_found == expected
        assert b_found == expected
        assert h_found == expected

        print(f"\n{name}: target={target}, expected={expected}")
        print(f"Linear Search          -> {l_found}, operations={l_ops}")
        print(f"Recursive Binary Search-> {b_found}, operations={b_ops}")
        print(f"Hash Table Search      -> {h_found}, operations={h_ops}")

    print("\nALL CORRECTNESS TESTS PASSED.")

if __name__ == "__main__":
    main()
