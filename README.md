# Heap Data Structures: Implementation, Analysis, and Applications

MSCS-532 Assignment 4 — Soundarya Kavimani

This repository contains:

* an in-place **Heapsort** built on an array-based max-heap,
* an **empirical comparison** of Heapsort with Quicksort and Merge Sort,
* a **max-heap priority queue** of `Task` objects (`insert`, `extract_max`,
  `increase_key`, `decrease_key`, `is_empty`), and
* a **task scheduler simulation** that uses the priority queue.

The full write-up is in [`Report_Heap_Data_Structures.docx`](Report_Heap_Data_Structures.docx).

## Project layout

```
heap-data-structures/
├── README.md
├── Report_Heap_Data_Structures.docx   report (design, analysis, results)
├── requirements.txt                   matplotlib (only needed for charts)
├── src/
│   ├── heapsort.py                    Heapsort + build_max_heap
│   ├── other_sorts.py                 Quicksort (random + first pivot), Merge Sort
│   ├── benchmark_sorts.py             sorting experiment -> results/
│   ├── priority_queue.py              Task class + MaxHeapPriorityQueue
│   └── scheduler_simulation.py        scheduler experiment -> results/
├── tests/
│   └── test_heaps.py                  7 unit tests
└── results/                           CSV files and PNG charts
```

## How to run

Requires Python 3.8 or newer. From the project folder:

```bash
pip3 install -r requirements.txt               # only for the charts
python3 src/heapsort.py                        # small Heapsort demo
python3 src/priority_queue.py                  # small priority-queue demo
python3 -m unittest discover -s tests -v       # run the tests
python3 src/benchmark_sorts.py                 # sorting experiment (~1 minute)
python3 src/scheduler_simulation.py            # scheduler experiment (~15 seconds)
```

Each experiment prints its results and writes CSV files and PNG charts into
`results/`. Exact times will differ from machine to machine, but the trends
should be the same.

## Summary of findings

**Heapsort is O(n log n) on every input.** On 100,000 integers it took about
0.26–0.30 s whether the input was random, sorted, or reverse-sorted, and it made
about 1.8 · n log₂ n comparisons in every case. Its running time does not depend
on the input order.

**But it was the slowest of the three in practice.** At n = 100,000 (random
input) Quicksort took 0.21 s, Merge Sort 0.25 s and Heapsort 0.30 s. Heapsort
makes more comparisons per element and jumps around the array (parent ↔ child
at index 2i + 1), which is less cache friendly than the sequential scans of
Quicksort and Merge Sort. Merge Sort sped up the most on already-sorted data
(about 16% faster than on random data) because its merges finish early.

**Heapsort's guarantee matters when Quicksort's pivot is bad.** A Quicksort that
always picks the first element became quadratic on sorted input: 1.33 s for
only 8,000 elements versus 0.019 s for Heapsort.

Measured on a Mac with Python 3.12.3 (median of 5 runs):

| n = 100,000 | Random | Sorted | Reverse |
|---|---|---|---|
| Heapsort | 295 ms | 294 ms | 262 ms |
| Quicksort (random pivot) | 207 ms | 200 ms | 198 ms |
| Merge Sort | 253 ms | 212 ms | 216 ms |

**Priority queue.** `insert`, `extract_max`, `increase_key` and `decrease_key`
are all O(log n); `is_empty` and `peek` are O(1). A dictionary from task ID to
heap index lets `increase_key`/`decrease_key` find a task in O(1).

**Scheduler (1,000 tasks, one CPU, ~87% busy).**

| Policy | Avg wait, priority 8–10 | Longest wait | Missed deadlines |
|---|---|---|---|
| FIFO | 21.6 | 95 | 288 |
| Priority (max-heap) | 2.7 | 567 | 123 |
| Priority + aging | 2.8 | 204 | 202 |

Heap-based priority scheduling cut the waiting time of urgent tasks by about
8× and missed deadlines by more than half, but low-priority tasks could wait a
very long time. Aging (raising a waiting task's priority with `increase_key`)
reduced the longest wait from 567 to 204 time steps.
