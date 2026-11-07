"""
benchmark_sorts.py
------------------
Empirically compares Heapsort, Quicksort (random pivot) and Merge Sort on
three input distributions (random, sorted, reverse-sorted) and several sizes.

For every (algorithm, distribution, size) it records:
  * the median wall-clock time over REPEATS runs (time.perf_counter)
  * the number of key comparisons (from one extra counted run)

A second, smaller experiment shows Quicksort's O(n^2) worst case when the
pivot is always the first element and the input is already sorted.

Results are written to results/sort_times.csv, results/naive_quicksort.csv
and charts to results/*.png.

Run from the project folder:   python src/benchmark_sorts.py
"""
import csv
import math
import os
import random
import statistics
import time

from heapsort import heapsort
from other_sorts import merge_sort, quicksort, quicksort_first

SIZES = [1_000, 5_000, 10_000, 25_000, 50_000, 100_000]
REPEATS = 5
ALGORITHMS = {"Heapsort": heapsort, "Quicksort": quicksort, "Merge Sort": merge_sort}
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results")


def make_input(kind, n, seed=0):
    """Build one of the three test distributions."""
    data = list(range(n))
    if kind == "random":
        random.Random(seed).shuffle(data)
    elif kind == "reverse":
        data.reverse()
    return data                     # "sorted" -> already ascending


def time_one(fn, data):
    copy = data[:]                  # never sort the shared input itself
    start = time.perf_counter()
    fn(copy)
    elapsed = time.perf_counter() - start
    assert copy == sorted(data), f"{fn.__name__} produced a wrong result"
    return elapsed


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for kind in ["random", "sorted", "reverse"]:
        for n in SIZES:
            data = make_input(kind, n)
            for name, fn in ALGORITHMS.items():
                times = [time_one(fn, data) for _ in range(REPEATS)]
                counter = [0]
                fn(data[:], counter=counter)
                rows.append({
                    "distribution": kind, "n": n, "algorithm": name,
                    "median_s": statistics.median(times),
                    "comparisons": counter[0],
                    "comparisons_per_nlog2n": counter[0] / (n * math.log2(n)),
                })
                print(f"{kind:8s} n={n:>7,} {name:10s} "
                      f"{rows[-1]['median_s']*1000:9.1f} ms  "
                      f"{counter[0]:>12,} comparisons")

    with open(os.path.join(OUT, "sort_times.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    # --- Worst case demo: first-element-pivot Quicksort on sorted input ---
    naive = []
    for n in [500, 1_000, 2_000, 4_000, 8_000]:
        data = make_input("sorted", n)
        for name, fn in [("Quicksort (first pivot)", quicksort_first),
                         ("Heapsort", heapsort)]:
            t = statistics.median(time_one(fn, data) for _ in range(3))
            naive.append({"n": n, "algorithm": name, "median_s": t})
            print(f"sorted   n={n:>7,} {name:24s} {t*1000:9.1f} ms")
    with open(os.path.join(OUT, "naive_quicksort.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=naive[0].keys())
        w.writeheader()
        w.writerows(naive)

    make_charts(rows, naive)


def make_charts(rows, naive):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping charts (CSV files still saved).")
        return

    colors = {"Heapsort": "#2a6fdb", "Quicksort": "#e07b00", "Merge Sort": "#2e9e5b"}
    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=True)
    for ax, kind in zip(axes, ["random", "sorted", "reverse"]):
        for name in ALGORITHMS:
            pts = [r for r in rows if r["distribution"] == kind and r["algorithm"] == name]
            ax.plot([p["n"] for p in pts], [p["median_s"] for p in pts],
                    marker="o", label=name, color=colors[name])
        ax.set_title(f"{kind.capitalize()} input")
        ax.set_xlabel("Input size n")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("Median time (seconds)")
    axes[0].legend()
    fig.suptitle("Running time of Heapsort vs. Quicksort vs. Merge Sort")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "sort_times.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4))
    for name, color in [("Quicksort (first pivot)", "#c0392b"), ("Heapsort", "#2a6fdb")]:
        pts = [r for r in naive if r["algorithm"] == name]
        ax.plot([p["n"] for p in pts], [p["median_s"] for p in pts],
                marker="o", label=name, color=color)
    ax.set_title("Already-sorted input: Quicksort worst case vs. Heapsort")
    ax.set_xlabel("Input size n")
    ax.set_ylabel("Median time (seconds)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "quicksort_worst_case.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
