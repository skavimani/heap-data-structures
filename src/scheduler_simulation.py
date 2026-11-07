"""
scheduler_simulation.py
-----------------------
Simulates a single-CPU, non-preemptive task scheduler and compares three
policies on the same randomly generated workload:

  1. FIFO           - first come, first served (a plain queue, no heap)
  2. Priority       - always run the waiting task with the highest priority
                      (uses MaxHeapPriorityQueue.extract_max)
  3. Priority+Aging - like Priority, but every AGING_INTERVAL time steps a
                      waiting task's priority is raised by 1 with
                      increase_key (capped at 10), so low-priority tasks
                      cannot starve

It also times insert / extract_max / increase_key at growing heap sizes to
check the O(log n) analysis.

Run from the project folder:   python src/scheduler_simulation.py
"""
import csv
import os
import random
import statistics
import time
from collections import deque

from priority_queue import MaxHeapPriorityQueue, Task

NUM_TASKS = 1_000
AGING_INTERVAL = 30       # time steps of waiting per +1 priority
MAX_PRIORITY = 10
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results")


def generate_workload(n=NUM_TASKS, seed=7):
    """
    Random tasks:
      * priority 1..10 (uniform)
      * duration 1..9 time steps (mean 5)
      * arrivals: on average one task every 5.6 steps -> CPU busy ~90% of
        the time, so a queue builds up and the policy actually matters
      * deadline = arrival + duration + slack; urgent (high-priority) tasks
        get tighter slack
    """
    rng = random.Random(seed)
    tasks, t = [], 0
    for i in range(n):
        t += round(rng.expovariate(1 / 5.6))
        priority = rng.randint(1, MAX_PRIORITY)
        duration = rng.randint(1, 9)
        slack = (MAX_PRIORITY + 1 - priority) * 6 + rng.randint(0, 10)
        tasks.append(Task(i, priority, t, duration, t + duration + slack))
    return tasks


def fresh_copy(tasks):
    return [Task(t.task_id, t.priority, t.arrival_time, t.duration, t.deadline)
            for t in tasks]


def simulate(tasks, policy):
    """Run one policy; return the list of finished tasks (with times filled)."""
    pending = deque(sorted(tasks, key=lambda t: t.arrival_time))
    original_priority = {t.task_id: t.priority for t in tasks}
    fifo = deque()
    pq = MaxHeapPriorityQueue()
    done, clock, last_aging = [], 0, 0

    def waiting_empty():
        return not fifo if policy == "FIFO" else pq.is_empty()

    while pending or not waiting_empty():
        # 1. admit every task that has arrived by now
        while pending and pending[0].arrival_time <= clock:
            task = pending.popleft()
            if policy == "FIFO":
                fifo.append(task)
            else:
                pq.insert(task)                          # O(log n)

        # 2. aging: bump everyone who has waited another AGING_INTERVAL steps
        if policy == "Priority+Aging":
            while last_aging + AGING_INTERVAL <= clock:
                last_aging += AGING_INTERVAL
                for task in pq.tasks():
                    if task.arrival_time <= last_aging - AGING_INTERVAL \
                            and task.priority < MAX_PRIORITY:
                        pq.increase_key(task.task_id, task.priority + 1)  # O(log n)

        # 3. CPU idle and nothing waiting -> jump to the next arrival
        if waiting_empty():
            clock = pending[0].arrival_time
            continue

        # 4. pick the next task and run it to completion (non-preemptive)
        task = fifo.popleft() if policy == "FIFO" else pq.extract_max()  # O(log n)
        task.start_time = clock
        clock += task.duration
        task.finish_time = clock
        task.priority = original_priority[task.task_id]   # report the real one
        done.append(task)
    return done


def summarize(done, policy):
    wait = [t.start_time - t.arrival_time for t in done]
    high = [t.start_time - t.arrival_time for t in done if t.priority >= 8]
    low = [t.start_time - t.arrival_time for t in done if t.priority <= 3]
    return {
        "policy": policy,
        "avg_wait": statistics.mean(wait),
        "avg_wait_high_prio_8_10": statistics.mean(high),
        "avg_wait_low_prio_1_3": statistics.mean(low),
        "max_wait": max(wait),
        "missed_deadlines": sum(t.finish_time > t.deadline for t in done),
        "missed_high_prio": sum(t.finish_time > t.deadline for t in done if t.priority >= 8),
        "makespan": max(t.finish_time for t in done),
    }


def benchmark_operations():
    """Average time per operation as the heap grows (should grow like log n)."""
    rows, rng = [], random.Random(1)
    for n in [1_000, 10_000, 100_000, 1_000_000]:
        pq = MaxHeapPriorityQueue()
        tasks = [Task(i, rng.randint(1, 10**6), i, 1, 0) for i in range(n)]
        t0 = time.perf_counter()
        for task in tasks:
            pq.insert(task)
        ins = (time.perf_counter() - t0) / n

        ids = rng.sample(range(n), min(n, 2_000))
        t0 = time.perf_counter()
        for tid in ids:
            pq.increase_key(tid, pq._heap[pq._pos[tid]].priority + 10**6)
        inc = (time.perf_counter() - t0) / len(ids)

        k = min(n, 2_000)
        t0 = time.perf_counter()
        for _ in range(k):
            pq.extract_max()
        ext = (time.perf_counter() - t0) / k
        rows.append({"n": n, "insert_us": ins * 1e6,
                     "increase_key_us": inc * 1e6, "extract_max_us": ext * 1e6})
        print(f"n={n:>9,}  insert {ins*1e6:6.2f} us  increase_key {inc*1e6:6.2f} us"
              f"  extract_max {ext*1e6:6.2f} us")
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


def main():
    os.makedirs(OUT, exist_ok=True)
    workload = generate_workload()
    results = []
    for policy in ["FIFO", "Priority", "Priority+Aging"]:
        s = summarize(simulate(fresh_copy(workload), policy), policy)
        results.append(s)
        print(f"{policy:15s} avg wait {s['avg_wait']:6.1f} | high-prio {s['avg_wait_high_prio_8_10']:6.1f}"
              f" | low-prio {s['avg_wait_low_prio_1_3']:6.1f} | max {s['max_wait']:4d}"
              f" | missed {s['missed_deadlines']:3d} (high {s['missed_high_prio']})")
    write_csv(os.path.join(OUT, "scheduler_results.csv"), results)
    ops = benchmark_operations()
    write_csv(os.path.join(OUT, "pq_operation_times.csv"), ops)
    make_charts(results, ops)


def make_charts(results, ops):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping charts (CSV files still saved).")
        return

    names = [r["policy"] for r in results]
    colors = ["#8a8f98", "#2a6fdb", "#2e9e5b"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    panels = [("avg_wait_high_prio_8_10", "Avg wait, priority 8-10"),
              ("max_wait", "Longest wait (starvation)"),
              ("missed_deadlines", "Missed deadlines (of 1,000)")]
    for ax, (col, title) in zip(axes, panels):
        vals = [r[col] for r in results]
        bars = ax.bar(names, vals, color=colors)
        ax.bar_label(bars, fmt="%.0f" if col != "avg_wait_high_prio_8_10" else "%.1f")
        ax.set_title(title)
        ax.margins(y=0.12)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Time steps / count")
    fig.suptitle("Scheduler simulation: FIFO vs. heap-based priority scheduling")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "scheduler_results.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ns = [r["n"] for r in ops]
    for col, label, color in [("insert_us", "insert", "#2e9e5b"),
                              ("increase_key_us", "increase_key", "#e07b00"),
                              ("extract_max_us", "extract_max", "#2a6fdb")]:
        ax.plot(ns, [r[col] for r in ops], marker="o", label=label, color=color)
    ax.set_xscale("log")
    ax.set_xlabel("Number of tasks in the heap (log scale)")
    ax.set_ylabel("Average time per operation (microseconds)")
    ax.set_title("Priority queue operation cost vs. heap size")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "pq_operation_times.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
