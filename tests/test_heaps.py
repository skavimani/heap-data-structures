"""
Unit tests. Run from the project folder:   python -m unittest discover -s tests -v
"""
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from heapsort import build_max_heap, heapsort, is_max_heap      # noqa: E402
from other_sorts import merge_sort, quicksort, quicksort_first  # noqa: E402
from priority_queue import MaxHeapPriorityQueue, Task           # noqa: E402


class TestSorting(unittest.TestCase):
    def test_edge_cases(self):
        for data in [[], [1], [2, 1], [3, 3, 3], [5, -1, 0, -1, 5]]:
            for fn in (heapsort, quicksort, quicksort_first, merge_sort):
                self.assertEqual(fn(data[:]), sorted(data))

    def test_random_lists(self):
        rng = random.Random(0)
        for _ in range(200):
            data = [rng.randint(-50, 50) for _ in range(rng.randint(0, 60))]
            for fn in (heapsort, quicksort, merge_sort):
                self.assertEqual(fn(data[:]), sorted(data))

    def test_build_max_heap(self):
        data = list(range(100))
        build_max_heap(data)
        self.assertTrue(is_max_heap(data))
        self.assertEqual(data[0], 99)


class TestPriorityQueue(unittest.TestCase):
    def make(self, i, p, arrival=0):
        return Task(i, p, arrival, 1, 100)

    def test_extract_order(self):
        pq = MaxHeapPriorityQueue()
        for i, p in enumerate([4, 9, 1, 7, 3, 9]):
            pq.insert(self.make(i, p, arrival=i))
        self.assertTrue(pq.check_heap())
        order = [pq.extract_max().task_id for _ in range(6)]
        self.assertEqual(order, [1, 5, 3, 0, 4, 2])   # ties -> earlier arrival
        self.assertTrue(pq.is_empty())

    def test_increase_and_decrease_key(self):
        pq = MaxHeapPriorityQueue()
        for i in range(10):
            pq.insert(self.make(i, i))
        pq.increase_key(0, 50)
        self.assertEqual(pq.peek().task_id, 0)
        pq.decrease_key(0, -1)
        self.assertEqual(pq.peek().task_id, 9)
        self.assertTrue(pq.check_heap())

    def test_random_operations_keep_heap_valid(self):
        rng, pq, live = random.Random(3), MaxHeapPriorityQueue(), {}
        for step in range(2_000):
            op = rng.random()
            if op < 0.5 or not live:
                t = self.make(step, rng.randint(0, 100))
                pq.insert(t); live[t.task_id] = t
            elif op < 0.7:
                top = pq.extract_max()
                self.assertEqual(top.priority, max(t.priority for t in live.values()))
                del live[top.task_id]
            elif op < 0.85:
                tid = rng.choice(list(live))
                pq.increase_key(tid, live[tid].priority + rng.randint(0, 20))
            else:
                tid = rng.choice(list(live))
                pq.decrease_key(tid, live[tid].priority - rng.randint(0, 20))
            self.assertTrue(pq.check_heap())

    def test_errors(self):
        pq = MaxHeapPriorityQueue()
        with self.assertRaises(IndexError):
            pq.extract_max()
        pq.insert(self.make(1, 5))
        with self.assertRaises(ValueError):
            pq.insert(self.make(1, 6))
        with self.assertRaises(ValueError):
            pq.increase_key(1, 2)


if __name__ == "__main__":
    unittest.main()
