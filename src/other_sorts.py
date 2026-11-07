"""
other_sorts.py
--------------
The two algorithms Heapsort is compared against.

* quicksort        - randomized pivot (Hoare, 1962). Expected O(n log n).
* quicksort_first  - first-element pivot. Kept only to show Quicksort's
                     O(n^2) worst case on already-sorted input.
* merge_sort       - top-down Merge Sort. O(n log n) always, O(n) extra memory.

All three sort in ascending order and return the sorted list. The optional
`counter` (a one-item list) counts key comparisons for the experiments.
"""
import random


# ----------------------------------------------------------------- Quicksort
def _partition(arr, lo, hi, pivot_index, counter):
    """Lomuto partition around arr[pivot_index]; returns the pivot's final spot."""
    arr[pivot_index], arr[hi] = arr[hi], arr[pivot_index]
    pivot = arr[hi]
    store = lo
    for i in range(lo, hi):
        if counter is not None:
            counter[0] += 1
        if arr[i] < pivot:
            arr[i], arr[store] = arr[store], arr[i]
            store += 1
    arr[store], arr[hi] = arr[hi], arr[store]
    return store


def _quicksort(arr, choose_pivot, counter):
    """
    Iterative quicksort with an explicit stack so very unbalanced splits
    (the worst case) cannot overflow Python's recursion limit.
    """
    stack = [(0, len(arr) - 1)]
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        p = _partition(arr, lo, hi, choose_pivot(lo, hi), counter)
        stack.append((lo, p - 1))
        stack.append((p + 1, hi))
    return arr


def quicksort(arr, counter=None, rng=random.Random(42)):
    """Quicksort with a uniformly random pivot (expected O(n log n))."""
    return _quicksort(arr, lambda lo, hi: rng.randint(lo, hi), counter)


def quicksort_first(arr, counter=None):
    """Quicksort that always picks the first element - O(n^2) on sorted input."""
    return _quicksort(arr, lambda lo, hi: lo, counter)


# ---------------------------------------------------------------- Merge Sort
def merge_sort(arr, counter=None):
    """Top-down Merge Sort. Uses a temporary list of size n (O(n) memory)."""
    n = len(arr)
    if n < 2:
        return arr
    tmp = [None] * n

    def sort(lo, hi):                       # sorts arr[lo:hi]
        if hi - lo < 2:
            return
        mid = (lo + hi) // 2
        sort(lo, mid)
        sort(mid, hi)
        i, j, k = lo, mid, lo
        while i < mid and j < hi:           # merge the two sorted halves
            if counter is not None:
                counter[0] += 1
            if arr[j] < arr[i]:
                tmp[k] = arr[j]; j += 1
            else:
                tmp[k] = arr[i]; i += 1     # "<=" keeps the sort stable
            k += 1
        while i < mid:
            tmp[k] = arr[i]; i += 1; k += 1
        while j < hi:
            tmp[k] = arr[j]; j += 1; k += 1
        arr[lo:hi] = tmp[lo:hi]

    sort(0, n)
    return arr
