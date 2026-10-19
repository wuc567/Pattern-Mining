"""
Python conversion of MemoryUsageMonitor.java

Java's Runtime.totalMemory()/freeMemory() reports JVM heap usage, which has
no direct Python equivalent. The closest analog for "memory this process is
using" is the OS-level RSS (resident set size) via the `psutil` library,
which is what this conversion uses. If you specifically need to track
Python object/heap allocation instead of process RSS, use `tracemalloc`
instead (see the commented alternative at the bottom) — that mirrors the
commented-out MemoryMXBean/heap-based variant in the original Java file.
"""

import threading
import time

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


class MemoryUsageMonitor(threading.Thread):
    """Monitors the memory usage of an algorithm running in this process."""

    def __init__(self, poll_interval: float = 0.01):
        """
        poll_interval: seconds between checks (Java version used 10ms).
        """
        super().__init__(daemon=True)
        self._stopped = threading.Event()
        self._max_memory_mb = 0.0
        self._poll_interval = poll_interval

        if _HAS_PSUTIL:
            self._process = psutil.Process()
        else:
            self._process = None

    def run(self):
        while not self._stopped.is_set():
            used_memory_mb = self._get_used_memory_mb()
            if used_memory_mb > self._max_memory_mb:
                self._max_memory_mb = used_memory_mb
            time.sleep(self._poll_interval)

    def _get_used_memory_mb(self) -> float:
        if self._process is not None:
            # RSS: resident set size, i.e. actual physical memory used by the process
            return self._process.memory_info().rss / 1024 / 1024
        else:
            # Fallback if psutil isn't installed: not accurate, but avoids a hard crash.
            import resource
            # ru_maxrss is KB on Linux, bytes on macOS
            import sys
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            if sys.platform == "darwin":
                return rss / 1024 / 1024
            return rss / 1024

    def get_max_memory_usage(self) -> float:
        return self._max_memory_mb

    def stop_monitoring(self):
        self._stopped.set()


# ---------------------------------------------------------------------------
# Example usage (mirrors how you'd use the Java class):
#
# monitor = MemoryUsageMonitor()
# monitor.start()
# ... run your algorithm ...
# monitor.stop_monitoring()
# monitor.join()
# print(monitor.get_max_memory_usage())
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Alternative: Python-heap-based tracking (analog of the commented-out
# MemoryMXBean/heap version in the original Java file). Use this if you want
# to measure Python object allocations rather than OS-level process memory.
# ---------------------------------------------------------------------------
#
# import tracemalloc
#
# class MemoryUsageMonitorTracemalloc(threading.Thread):
#     def __init__(self, poll_interval: float = 0.01):
#         super().__init__(daemon=True)
#         self._stopped = threading.Event()
#         self._max_memory_mb = 0.0
#         self._poll_interval = poll_interval
#         tracemalloc.start()
#
#     def run(self):
#         while not self._stopped.is_set():
#             current, peak = tracemalloc.get_traced_memory()
#             used_mb = current / 1024 / 1024
#             if used_mb > self._max_memory_mb:
#                 self._max_memory_mb = used_mb
#             time.sleep(self._poll_interval)
#
#     def get_max_memory_usage(self) -> float:
#         return self._max_memory_mb
#
#     def stop_monitoring(self):
#         self._stopped.set()
#         tracemalloc.stop()
