"""
heapsort.py
-----------
In-place Heapsort built on an array-based binary max-heap.

How the array represents the heap (0-based indexing):
    parent(i) = (i - 1) // 2
    left(i)   = 2 * i + 1
    right(i)  = 2 * i + 2

Algorithm (Williams, 1964; Floyd, 1964):
    1. BUILD-MAX-HEAP: turn the unsorted list into a max-heap by calling
       sift_down on every internal node, from the last one up to the root.
       This bottom-up construction costs O(n) in total.
    2. Repeat n - 1 times:
         a. The largest element is at index 0. Swap it with the last
            element of the heap region, so it lands in its final sorted spot.
         b. Shrink the heap region by one.
         c. Call sift_down(0) to restore the max-heap property. O(log n).

Total: O(n) + (n - 1) * O(log n) = O(n log n) in every case.
Extra memory: O(1) - the sort happens inside the input list.
"""


def _sift_down(arr, start, end, counter=None):
    """
    Move arr[start] down the tree until the max-heap property holds for the
    subtree rooted at `start`. Only indexes < `end` are part of the heap.

    Written as a loop (not recursion) so it uses O(1) extra memory.
    `counter` is an optional one-item list used to count key comparisons
    for the experiments; it does not change the algorithm.
    """
    root = start
    while True:
        left = 2 * root + 1
        if left >= end:              # root is a leaf -> nothing to do
            return
        largest = root
        right = left + 1

        if counter is not None:
            counter[0] += 1
        if arr[left] > arr[largest]:
            largest = left

        if right < end:
            if counter is not None:
                counter[0] += 1
            if arr[right] > arr[largest]:
                largest = right

        if largest == root:          # heap property already satisfied
            return
        arr[root], arr[largest] = arr[largest], arr[root]
        root = largest               # keep sifting the moved element down


def build_max_heap(arr, counter=None):
    """Rearrange `arr` into a max-heap in O(n) time (Floyd's method)."""
    n = len(arr)
    # The last internal (non-leaf) node is at index n//2 - 1.
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(arr, i, n, counter)


def heapsort(arr, counter=None):
    """
    Sort `arr` in ascending order, in place, and also return it.

    >>> heapsort([5, 2, 9, 1, 5, 6])
    [1, 2, 5, 5, 6, 9]
    """
    n = len(arr)
    build_max_heap(arr, counter)
    # `end` marks where the heap region stops; everything after it is sorted.
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]   # move current max to the back
        _sift_down(arr, 0, end, counter)      # repair the smaller heap
    return arr


def is_max_heap(arr):
    """Return True if `arr` satisfies the max-heap property (used in tests)."""
    n = len(arr)
    for i in range(n):
        left, right = 2 * i + 1, 2 * i + 2
        if left < n and arr[i] < arr[left]:
            return False
        if right < n and arr[i] < arr[right]:
            return False
    return True


if __name__ == "__main__":
    sample = [12, 3, 17, 8, 34, 25, 1, 9, 17]
    print("Before:", sample)
    print("After: ", heapsort(sample[:]))
