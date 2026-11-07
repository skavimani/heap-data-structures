"""
priority_queue.py
-----------------
A max-heap priority queue of Task objects, stored in a Python list.

Design choices
  * Array (Python list) representation: a complete binary tree maps exactly
    onto consecutive list slots, so parent/child positions are found with
    arithmetic instead of pointers, and appending/removing at the end is O(1).
  * Max-heap: the scheduler always runs the task with the HIGHEST priority
    number first.
  * Ties are broken by earlier arrival time, then by task ID, so the order is
    deterministic and fair (first come, first served among equals).
  * A dictionary `_pos` maps task_id -> index in the list. This lets
    increase_key / decrease_key find a task in O(1) instead of O(n).

Operation costs (n = number of tasks in the queue)
    insert            O(log n)   append + sift up
    extract_max       O(log n)   swap root with last, pop, sift down
    peek              O(1)
    increase_key      O(log n)   O(1) lookup + sift up
    decrease_key      O(log n)   O(1) lookup + sift down
    is_empty / len    O(1)
"""
from dataclasses import dataclass, field


@dataclass
class Task:
    """One unit of work to be scheduled."""
    task_id: int
    priority: int            # larger number = more important
    arrival_time: int        # time step at which the task enters the system
    duration: int            # time steps of CPU needed
    deadline: int            # time step by which it should be finished
    start_time: int = field(default=None)
    finish_time: int = field(default=None)

    def key(self):
        """
        Value used to order tasks in the heap. A larger key wins.
        Higher priority first; on a tie the earlier arrival (smaller time),
        then the smaller task_id. Negating makes "smaller is better" fields
        compare as "larger is better".
        """
        return (self.priority, -self.arrival_time, -self.task_id)


class MaxHeapPriorityQueue:
    def __init__(self):
        self._heap = []      # list of Task objects
        self._pos = {}       # task_id -> index in self._heap

    # ---------------------------------------------------------- helpers
    def __len__(self):
        return len(self._heap)

    def is_empty(self):
        """True if there are no tasks waiting. O(1)."""
        return len(self._heap) == 0

    def __contains__(self, task_id):
        return task_id in self._pos

    def _swap(self, i, j):
        h = self._heap
        h[i], h[j] = h[j], h[i]
        self._pos[h[i].task_id] = i      # keep the index map up to date
        self._pos[h[j].task_id] = j

    def _sift_up(self, i):
        """Move heap[i] up while it is larger than its parent. O(log n)."""
        h = self._heap
        while i > 0:
            parent = (i - 1) // 2
            if h[i].key() > h[parent].key():
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        """Move heap[i] down while a child is larger. O(log n)."""
        h, n = self._heap, len(self._heap)
        while True:
            left, right, largest = 2 * i + 1, 2 * i + 2, i
            if left < n and h[left].key() > h[largest].key():
                largest = left
            if right < n and h[right].key() > h[largest].key():
                largest = right
            if largest == i:
                return
            self._swap(i, largest)
            i = largest

    # ---------------------------------------------------- core operations
    def insert(self, task):
        """Add a task at the end of the list, then sift it up. O(log n)."""
        if task.task_id in self._pos:
            raise ValueError(f"task {task.task_id} is already in the queue")
        self._heap.append(task)
        self._pos[task.task_id] = len(self._heap) - 1
        self._sift_up(len(self._heap) - 1)

    def peek(self):
        """Return (without removing) the highest-priority task. O(1)."""
        if self.is_empty():
            raise IndexError("peek from an empty priority queue")
        return self._heap[0]

    def extract_max(self):
        """Remove and return the highest-priority task. O(log n)."""
        if self.is_empty():
            raise IndexError("extract_max from an empty priority queue")
        last = len(self._heap) - 1
        self._swap(0, last)                  # move the max to the end
        top = self._heap.pop()               # O(1) removal from the end
        del self._pos[top.task_id]
        if self._heap:
            self._sift_down(0)               # repair from the root
        return top

    def increase_key(self, task_id, new_priority):
        """Raise a task's priority, then sift it up. O(log n)."""
        i = self._pos[task_id]               # O(1) thanks to the index map
        task = self._heap[i]
        if new_priority < task.priority:
            raise ValueError("new priority is smaller; use decrease_key")
        task.priority = new_priority
        self._sift_up(i)

    def decrease_key(self, task_id, new_priority):
        """Lower a task's priority, then sift it down. O(log n)."""
        i = self._pos[task_id]
        task = self._heap[i]
        if new_priority > task.priority:
            raise ValueError("new priority is larger; use increase_key")
        task.priority = new_priority
        self._sift_down(i)

    def tasks(self):
        """Snapshot of the tasks currently waiting (any order)."""
        return list(self._heap)

    def check_heap(self):
        """True if every parent's key >= its children's keys (used in tests)."""
        h = self._heap
        for i in range(len(h)):
            for c in (2 * i + 1, 2 * i + 2):
                if c < len(h) and h[c].key() > h[i].key():
                    return False
        return all(self._heap[idx].task_id == tid for tid, idx in self._pos.items())


if __name__ == "__main__":
    pq = MaxHeapPriorityQueue()
    for t in [Task(1, 3, 0, 4, 20), Task(2, 9, 1, 2, 10),
              Task(3, 5, 2, 3, 15), Task(4, 1, 3, 1, 30)]:
        pq.insert(t)
    pq.increase_key(4, 10)                  # task 4 becomes the most urgent
    order = []
    while not pq.is_empty():
        order.append(pq.extract_max().task_id)
    print("Extraction order:", order)       # -> [4, 2, 3, 1]
