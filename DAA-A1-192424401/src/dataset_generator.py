"""
DAA Assignment 1 - Personal Dataset Generator
Student: Jerry David
Registration No.: 192424401
Personal seed: 2401 (last four digits of registration number)

Generates deterministic, unique registration-number datasets for:
1,000 / 10,000 / 100,000 / 1,000,000 records.

Large datasets are intentionally NOT committed to GitHub.
Run this script to regenerate them.
"""

from pathlib import Path
import csv
import random
import sys

REG_NO = 192424401
SEED = 2401
SIZES = [1_000, 10_000, 100_000, 1_000_000]
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def generate_registration_numbers(n: int):
    if n < 2:
        raise ValueError("n must be at least 2")

    rng = random.Random(SEED + n)
    required = REG_NO
    forbidden = REG_NO + 1

    values = {required}
    while len(values) < n:
        value = rng.randint(100_000_000, 999_999_999)
        if value not in (required, forbidden):
            values.add(value)

    # Shuffle deterministically so the original data is not sorted.
    values = list(values)
    rng.shuffle(values)
    return values

def write_csv(values, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["registration_number"])
        writer.writerows((v,) for v in values)

def generate(n: int):
    values = generate_registration_numbers(n)
    path = DATA_DIR / f"students_{n}.csv"
    write_csv(values, path)
    print(f"Generated {n:,} records -> {path}")
    print(f"Contains own Reg No. {REG_NO}: {REG_NO in values}")
    print(f"Excludes Reg No.+1 {REG_NO + 1}: {REG_NO + 1 not in values}")
    return path

if __name__ == "__main__":
    requested = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else SIZES
    for n in requested:
        if n not in SIZES:
            raise SystemExit(f"Allowed sizes: {SIZES}")
        generate(n)
