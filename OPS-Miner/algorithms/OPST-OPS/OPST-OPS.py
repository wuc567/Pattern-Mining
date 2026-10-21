#!/usr/bin/env python3
"""Standalone sliding-window wrapper for the C++ OPST implementation.

Python is responsible only for loading the source sequence, selecting complete
windows, and converting each window to integer ranks.  The compiled
``OPSTFrequent`` executable constructs the OPST and mines all frequent
order-preserving patterns of length at least two.

Two time scopes are reported:

``aligned_runtime_seconds``
    window extraction + rank conversion + C++ OPST construction + C++ mining
    and counting.  Temporary text transport, process startup, and input parsing
    are excluded.  This is the scope used for algorithm comparisons.

``pipeline_runtime_seconds``
    the complete per-window Python-to-C++ pipeline after the source sequence is
    loaded, including temporary text transport and C++ process startup/input.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np

try:
    import psutil
except ImportError:  # Peak RSS remains optional for minimal installations.
    psutil = None


CONSTRUCTION_RE = re.compile(
    r"Runtime only for OPST construction\s*=\s*([0-9.eE+-]+)\s*s"
)
MINING_RE = re.compile(
    r"Runtime only used for mining all frequent OPPs:\s*([0-9.eE+-]+)\s*s"
)
COUNT_RE = re.compile(r"The number of found frequent patterns is\s+(\d+)")


class SlidingOPSTMiner:
    """Mine all complete windows by invoking the C++ OPST executable."""

    def __init__(
        self,
        window_size: int,
        step_size: int,
        min_sup: int,
        binary: str | Path,
        rank_mode: str = "strict",
    ) -> None:
        self.window_size = int(window_size)
        self.step_size = int(step_size)
        self.min_sup = int(min_sup)
        self.binary = Path(binary).expanduser().resolve()
        self.rank_mode = rank_mode

        if self.window_size < 2:
            raise ValueError("window_size must be at least 2")
        if self.step_size < 1:
            raise ValueError("step_size must be positive")
        if self.min_sup < 1:
            raise ValueError("min_sup must be positive")
        if self.rank_mode not in {"strict", "dense"}:
            raise ValueError("rank_mode must be 'strict' or 'dense'")
        if not self.binary.is_file():
            raise FileNotFoundError(
                f"C++ OPST executable not found: {self.binary}\n"
                "Compile OPSTFrequent first or pass --opst-binary PATH."
            )
        if not os.access(self.binary, os.X_OK):
            raise PermissionError(f"C++ OPST executable is not executable: {self.binary}")

    def _rank_window(self, values: np.ndarray) -> np.ndarray:
        values = np.asarray(values)
        if not np.isfinite(values).all():
            raise ValueError("OPST input contains NaN or infinity")

        if self.rank_mode == "dense":
            # Equal observations retain equal ranks.
            return (
                np.unique(values, return_inverse=True)[1]
                .astype(np.int32, copy=False)
                + 1
            )

        # Break ties deterministically by original position, producing a
        # permutation 1..w.  This is the mode used in the fair WOPP comparison.
        positions = np.arange(values.size, dtype=np.int64)
        order = np.lexsort((positions, values))
        ranks = np.empty(values.size, dtype=np.int32)
        ranks[order] = np.arange(1, values.size + 1, dtype=np.int32)
        return ranks

    @staticmethod
    def _parse(regex: re.Pattern[str], output: str, cast=float):
        match = regex.search(output)
        if not match:
            raise RuntimeError(f"Unable to parse C++ OPST output:\n{output}")
        return cast(match.group(1))

    @staticmethod
    def _rss_bytes(*processes) -> int:
        if psutil is None:
            return 0
        total = 0
        for process in processes:
            try:
                total += process.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied, PermissionError):
                pass
        return total

    def _run_cpp(self, input_path: Path) -> tuple[str, int]:
        """Run one OPST child and sample parent+child RSS concurrently."""
        process = subprocess.Popen(
            [
                str(self.binary),
                "-f",
                str(input_path),
                "-t",
                str(self.min_sup),
            ],
            cwd=self.binary.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        peak_rss = 0
        if psutil is not None:
            parent = psutil.Process(os.getpid())
            child = psutil.Process(process.pid)
            while process.poll() is None:
                peak_rss = max(peak_rss, self._rss_bytes(parent, child))
                time.sleep(0.0005)

        stdout, stderr = process.communicate()
        if process.returncode:
            raise RuntimeError(
                f"C++ OPST failed with exit code {process.returncode}:\n"
                f"{stdout}\n{stderr}"
            )
        if psutil is not None:
            peak_rss = max(
                peak_rss,
                self._rss_bytes(psutil.Process(os.getpid())),
            )
        return stdout, peak_rss

    def run(
        self,
        values: np.ndarray,
        max_windows: int | None = None,
        repeats: int = 1,
        verbose: bool = False,
    ) -> dict:
        values = np.asarray(values)
        if values.size < self.window_size:
            raise ValueError("data length is smaller than window_size")
        if repeats < 1:
            raise ValueError("repeats must be positive")

        starts = list(range(0, values.size - self.window_size + 1, self.step_size))
        if max_windows is not None:
            starts = starts[: int(max_windows)]
        if not starts:
            raise ValueError("no complete windows")

        runs = []
        with tempfile.TemporaryDirectory(prefix="sliding-opst-") as temporary:
            input_path = Path(temporary) / "window.txt"
            for repeat_index in range(repeats):
                pipeline_started = time.perf_counter()
                rank_seconds = 0.0
                construction_seconds = 0.0
                mining_seconds = 0.0
                patterns_total = 0
                peak_rss_bytes = 0
                per_window = []

                for window_index, start in enumerate(starts, 1):
                    rank_started = time.perf_counter()
                    window_values = values[start : start + self.window_size]
                    ranks = self._rank_window(window_values)
                    window_rank_seconds = time.perf_counter() - rank_started
                    rank_seconds += window_rank_seconds

                    # Text transport is required by the unmodified executable,
                    # but is deliberately outside the aligned algorithm time.
                    np.savetxt(input_path, ranks, fmt="%d")
                    output, sampled_rss = self._run_cpp(input_path)
                    peak_rss_bytes = max(peak_rss_bytes, sampled_rss)

                    window_construction = self._parse(CONSTRUCTION_RE, output)
                    window_mining = self._parse(MINING_RE, output)
                    window_patterns = self._parse(COUNT_RE, output, int)
                    construction_seconds += window_construction
                    mining_seconds += window_mining
                    patterns_total += window_patterns

                    if verbose:
                        per_window.append(
                            {
                                "window": window_index,
                                "start": start,
                                "rank_seconds": window_rank_seconds,
                                "construction_seconds": window_construction,
                                "mining_seconds": window_mining,
                                "frequent_patterns": window_patterns,
                            }
                        )

                pipeline_seconds = time.perf_counter() - pipeline_started
                aligned_seconds = rank_seconds + construction_seconds + mining_seconds
                runs.append(
                    {
                        "repeat": repeat_index + 1,
                        "rank_seconds": rank_seconds,
                        "construction_seconds": construction_seconds,
                        "mining_seconds": mining_seconds,
                        "aligned_runtime_seconds": aligned_seconds,
                        "pipeline_runtime_seconds": pipeline_seconds,
                        "peak_rss_bytes": peak_rss_bytes or None,
                        "peak_rss_mib": (
                            peak_rss_bytes / 1048576 if peak_rss_bytes else None
                        ),
                        "patterns_total": patterns_total,
                        "patterns_mean_per_window": patterns_total / len(starts),
                        "per_window": per_window if verbose else None,
                    }
                )

        pattern_totals = {run["patterns_total"] for run in runs}
        if len(pattern_totals) != 1:
            raise RuntimeError(f"non-deterministic pattern totals: {pattern_totals}")

        def median(field: str):
            numbers = [run[field] for run in runs if run[field] is not None]
            return statistics.median(numbers) if numbers else None

        return {
            "algorithm": "OPST-Frequent (C++ core, Python sliding wrapper)",
            "binary": str(self.binary),
            "data_length": int(values.size),
            "window_size": self.window_size,
            "step_size": self.step_size,
            "overlap": 1.0 - self.step_size / self.window_size,
            "minsup": self.min_sup,
            "rank_mode": self.rank_mode,
            "windows": len(starts),
            "repeats": repeats,
            "patterns_total": runs[0]["patterns_total"],
            "patterns_mean_per_window": runs[0]["patterns_mean_per_window"],
            "rank_seconds_median": median("rank_seconds"),
            "construction_seconds_median": median("construction_seconds"),
            "mining_seconds_median": median("mining_seconds"),
            "aligned_runtime_seconds_median": median("aligned_runtime_seconds"),
            "pipeline_runtime_seconds_median": median("pipeline_runtime_seconds"),
            "peak_rss_mib_median": median("peak_rss_mib"),
            "runs": runs,
            "timing_scope": {
                "aligned": (
                    "window extraction + rank conversion + C++ OPST construction + "
                    "all-frequent mining/counting"
                ),
                "pipeline": (
                    "aligned work + temporary text transport + C++ process startup "
                    "+ C++ text input + Python output parsing"
                ),
                "excluded_from_both": "source dataset loading and final JSON output",
            },
        }


def load_values(path: Path, data_format: str) -> np.ndarray:
    if data_format == "auto":
        data_format = (
            "binary" if path.suffix.lower() in {".f64", ".bin", ".raw"} else "text"
        )
    if data_format == "binary":
        return np.memmap(path, dtype="<f8", mode="r")

    values = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            values.extend(
                float(token) for token in line.replace(",", " ").split()
            )
    return np.asarray(values, dtype=np.float64)


def main() -> None:
    default_binary = Path(__file__).resolve().parent / "OPSTFrequent"
    parser = argparse.ArgumentParser(
        description="Run the C++ OPST frequent-pattern miner over sliding windows."
    )
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--window", "-w", type=int, required=True)
    parser.add_argument("--step", "-s", type=int, required=True)
    parser.add_argument("--minsup", "-m", type=int, required=True)
    parser.add_argument(
        "--data-format", choices=["auto", "binary", "text"], default="auto"
    )
    parser.add_argument(
        "--rank-mode",
        choices=["strict", "dense"],
        default="strict",
        help="strict breaks ties by position; dense preserves equal values",
    )
    parser.add_argument("--opst-binary", type=Path, default=default_binary)
    parser.add_argument("--max-windows", type=int)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    values = load_values(args.dataset.expanduser().resolve(), args.data_format)
    miner = SlidingOPSTMiner(
        args.window,
        args.step,
        args.minsup,
        args.opst_binary,
        args.rank_mode,
    )
    result = miner.run(
        values,
        max_windows=args.max_windows,
        repeats=args.repeats,
        verbose=args.verbose,
    )

    if args.output:
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
