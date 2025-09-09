from __future__ import annotations
import time

# === Verbatim from user's original code ===

def measure_execution_time(func, *args, repetitions=10):
    start_time = time.perf_counter()
    for _ in range(repetitions):
        func(*args)
    total_time = time.perf_counter() - start_time
    return total_time / repetitions
