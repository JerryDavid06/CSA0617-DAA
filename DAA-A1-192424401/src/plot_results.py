"""
Generate graphs from results/results.csv.

Important: graphs are based ONLY on the student's measured CSV.
"""

from pathlib import Path
import csv
from collections import defaultdict
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "results" / "results.csv"
OUT = ROOT / "results" / "graphs"
OUT.mkdir(parents=True, exist_ok=True)

def read_rows():
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def standard_rows(rows):
    return [r for r in rows if r["experiment"] == "standard" and r["target_type"] == "OWN_REG_NO"]

def make_runtime_graph(rows):
    algos = sorted(set(r["algorithm"] for r in rows))
    plt.figure(figsize=(10, 6))
    for algo in algos:
        subset = [r for r in rows if r["algorithm"] == algo]
        subset.sort(key=lambda r: int(r["n"]))
        x = [int(r["n"]) for r in subset]
        y = [float(r["search_ms"]) for r in subset]
        plt.plot(x, y, marker="o", label=algo)
    plt.xlabel("Input Size (n)")
    plt.ylabel("Search Time (ms)")
    plt.title("Search Time vs Input Size")
    plt.xscale("log")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "runtime_comparison.png", dpi=200)
    plt.close()

def make_ops_graph(rows):
    algos = sorted(set(r["algorithm"] for r in rows))
    plt.figure(figsize=(10, 6))
    for algo in algos:
        subset = [r for r in rows if r["algorithm"] == algo]
        subset.sort(key=lambda r: int(r["n"]))
        x = [int(r["n"]) for r in subset]
        y = [int(r["key_operations"]) for r in subset]
        plt.plot(x, y, marker="o", label=algo)
    plt.xlabel("Input Size (n)")
    plt.ylabel("Key Operations / Comparisons")
    plt.title("Key Operations vs Input Size")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "operations_comparison.png", dpi=200)
    plt.close()

def make_total_cost_graph(rows):
    algos = sorted(set(r["algorithm"] for r in rows))
    plt.figure(figsize=(10, 6))
    for algo in algos:
        subset = [r for r in rows if r["algorithm"] == algo]
        subset.sort(key=lambda r: int(r["n"]))
        x = [int(r["n"]) for r in subset]
        y = [float(r["total_ms"]) for r in subset]
        plt.plot(x, y, marker="o", label=algo)
    plt.xlabel("Input Size (n)")
    plt.ylabel("Total Time Including Preprocessing (ms)")
    plt.title("Total Cost vs Input Size")
    plt.xscale("log")
    plt.yscale("log")
    plt.legend()
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(OUT / "total_cost_comparison.png", dpi=200)
    plt.close()

def make_task12_graph(rows):
    subset = [r for r in rows if r["experiment"] == "task12_50000_searches"]
    labels = [r["algorithm"] for r in subset]
    values = [float(r["search_ms"]) for r in subset]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)
    plt.xlabel("Algorithm")
    plt.ylabel("Total Time for 50,000 Searches (ms)")
    plt.title("Task 12: 50,000 Searches on 1,000,000 Records")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(OUT / "task12_50000_searches.png", dpi=200)
    plt.close()

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError("Run benchmark.py first.")
    rows = read_rows()
    std = standard_rows(rows)
    make_runtime_graph(std)
    make_ops_graph(std)
    make_total_cost_graph(std)
    make_task12_graph(rows)
    print(f"Graphs written to {OUT}")

if __name__ == "__main__":
    main()
