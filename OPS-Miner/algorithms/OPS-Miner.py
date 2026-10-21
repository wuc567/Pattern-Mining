import argparse
import time

import numpy as np


class OPSMiner:


    def __init__(self, window_size, step_size, min_sup):
        self.window_size = int(window_size)
        self.step_size = int(step_size)
        self.min_sup = int(min_sup)
        self.data = np.empty(0, dtype=np.float64)
        self.left = 0
        self.right = -1
        self.length_two_ids = None
        self.length_two_counts = np.zeros(3, dtype=np.int64)
        self.fusion_cache = {}
        self.initial_runtime = 0.0
        self.update_runtimes = []

    # The benchmark runner injects an in-memory float64 array into find2().
    # This standalone text reader is retained here only for reference.
    # def read_file(self, file_path):
    #     values = []
    #     with open(file_path, "r", encoding="utf-8") as stream:
    #         for line in stream:
    #             values.extend(
    #                 float(token)
    #                 for token in line.replace(",", " ").split()
    #             )
    #     return np.asarray(values, dtype=np.float64)

    def find2(self, values=None):
        first_window = self.length_two_ids is None
        start_time = time.perf_counter()

        if first_window:
            self.data = np.ascontiguousarray(values, dtype=np.float64)
            self.length_two_ids = np.zeros(self.data.size, dtype=np.int32)
            self.left = 0
            self.right = self.window_size - 1
            endpoints = np.arange(1, self.right + 1, dtype=np.int64)
            ids = np.where(
                self.data[endpoints - 1] < self.data[endpoints],
                1,
                np.where(
                    self.data[endpoints - 1] > self.data[endpoints],
                    2,
                    0,
                ),
            ).astype(np.int32, copy=False)
            self.length_two_ids[endpoints] = ids
            self.length_two_counts = np.bincount(
                ids, minlength=3
            ).astype(np.int64, copy=False)
            self.length_two_counts[0] = 0
        else:
            if self.right + self.step_size >= self.data.size:
                return None

            old_left = self.left
            old_right = self.right
            self.left += self.step_size
            self.right += self.step_size

            leaving_ids = self.length_two_ids[
                old_left + 1:self.left + 1
            ]
            removed = np.bincount(leaving_ids, minlength=3)
            self.length_two_counts[1:3] -= removed[1:3]

            start = old_right + 1
            stop = self.right + 1
            ids = np.where(
                self.data[start - 1:stop - 1] < self.data[start:stop],
                1,
                np.where(
                    self.data[start - 1:stop - 1] > self.data[start:stop],
                    2,
                    0,
                ),
            ).astype(np.int32, copy=False)
            self.length_two_ids[start:stop] = ids
            added = np.bincount(ids, minlength=3)
            self.length_two_counts[1:3] += added[1:3]

        miner_data = self.data[self.left:self.right + 1]
        position_ids = self.length_two_ids[self.left:self.right + 1]
        boundary_id = int(position_ids[0])
        position_ids[0] = 0

        f2 = {}
        if self.length_two_counts[1] >= self.min_sup:
            f2[(1, 2)] = int(self.length_two_counts[1])
        if self.length_two_counts[2] >= self.min_sup:
            f2[(2, 1)] = int(self.length_two_counts[2])

        if len(f2) != 2:
            active_ids = position_ids.copy()
            keep = np.zeros(3, dtype=bool)
            keep[1] = self.length_two_counts[1] >= self.min_sup
            keep[2] = self.length_two_counts[2] >= self.min_sup
            active_ids[~keep[active_ids]] = 0
        else:
            active_ids = position_ids

        result = self._find_m(
            miner_data,
            f2,
            active_ids,
            [None, (1, 2), (2, 1)],
        )
        position_ids[0] = boundary_id

        if first_window:
            self.initial_runtime = time.perf_counter() - start_time
            self.update_runtimes = []
        else:
            self.update_runtimes.append(time.perf_counter() - start_time)
        return result

    def _find_m(self, miner_data, f2, position_ids, id_to_pattern):
        current_patterns = f2
        current_ids = position_ids
        levels = []
        while current_patterns:
            levels.append(dict(current_patterns))
            pattern_length = len(next(iter(current_patterns)))
            current_patterns, current_ids, id_to_pattern = (
                self._build_next_level(
                    miner_data,
                    pattern_length,
                    current_ids,
                    id_to_pattern,
                )
            )
        return levels

    def _build_next_level(
        self,
        miner_data,
        pattern_length,
        current_ids,
        id_to_pattern,
    ):
        next_ids = np.zeros(miner_data.size, dtype=np.int32)
        prefix_ids = current_ids[:-1]
        suffix_ids = current_ids[1:]
        valid = (prefix_ids != 0) & (suffix_ids != 0)
        aligned_indices = np.flatnonzero(valid)
        if aligned_indices.size == 0:
            return {}, next_ids, [None]

        endpoints = aligned_indices + 1
        starts = endpoints - pattern_length
        relations = np.where(
            miner_data[starts] < miner_data[endpoints],
            1,
            np.where(
                miner_data[starts] > miner_data[endpoints],
                2,
                0,
            ),
        ).astype(np.int64, copy=False)
        active_prefix_ids = prefix_ids[aligned_indices].astype(
            np.int64, copy=False
        )
        active_suffix_ids = suffix_ids[aligned_indices].astype(
            np.int64, copy=False
        )
        id_base = len(id_to_pattern)
        event_keys = (
            (active_prefix_ids * id_base + active_suffix_ids) * 3
            + relations
        )

        max_event_key = int(event_keys.max())
        dense_key_limit = min(4_000_000, int(event_keys.size) * 16)
        use_bincount = max_event_key <= dense_key_limit
        if use_bincount:
            counts_by_key = np.bincount(event_keys)
            unique_keys = np.flatnonzero(counts_by_key)
            counts = counts_by_key[unique_keys]
        else:
            unique_keys, inverse, counts = np.unique(
                event_keys,
                return_inverse=True,
                return_counts=True,
            )

        frequent_groups = np.flatnonzero(counts >= self.min_sup)
        candidate_for_group = [None] * unique_keys.size
        frequent_patterns = {}
        for group_index in frequent_groups:
            event_key = int(unique_keys[group_index])
            relation = event_key % 3
            pair_key = event_key // 3
            prefix_id = pair_key // id_base
            suffix_id = pair_key % id_base
            candidate = self.frequent_pattern_fusion(
                id_to_pattern[prefix_id],
                id_to_pattern[suffix_id],
                relation,
            )
            candidate_for_group[group_index] = candidate
            if candidate is not None:
                frequent_patterns[candidate] = int(counts[group_index])

        next_id_to_pattern = [None, *frequent_patterns]
        pattern_to_next_id = {
            pattern: pattern_id
            for pattern_id, pattern in enumerate(
                next_id_to_pattern[1:], start=1
            )
        }
        group_to_next_id = np.zeros(unique_keys.size, dtype=np.int32)
        for group_index in frequent_groups:
            candidate = candidate_for_group[group_index]
            if candidate is not None:
                group_to_next_id[group_index] = pattern_to_next_id[candidate]

        if use_bincount:
            key_to_next_id = np.zeros(max_event_key + 1, dtype=np.int32)
            key_to_next_id[unique_keys] = group_to_next_id
            next_ids[endpoints] = key_to_next_id[event_keys]
        else:
            next_ids[endpoints] = group_to_next_id[inverse]
        return frequent_patterns, next_ids, next_id_to_pattern

    def frequent_pattern_fusion(self, p, q, relation):
        key = (p, q, int(relation))
        if key not in self.fusion_cache:
            self.fusion_cache[key] = self._pattern_fusion(p, q, relation)
        return self.fusion_cache[key]

    def _pattern_fusion(self, p, q, relation):
        p1 = p[0]
        qm = q[-1]

        if p1 < qm:
            result = [p1]
            result.extend(q)
            for index in range(1, len(result)):
                if result[index] >= result[0]:
                    result[index] += 1
            return tuple(result)

        if p1 > qm:
            result = [p1 + 1]
            result.extend(q)
            for index in range(1, len(result)):
                if result[index] >= result[0]:
                    result[index] += 1
            return tuple(result)

        if relation == 0:
            return None

        middle = [value if value < p1 else value + 1 for value in p[1:]]
        if relation == 1:
            return tuple([p1] + middle + [p1 + 1])
        return tuple([p1 + 1] + middle + [p1])

    def run(self, values, max_updates=None):
        values = np.asarray(values, dtype=np.float64)
        result = self.find2(values)
        updates = 0
        while max_updates is None or updates < max_updates:
            next_result = self.find2()
            if next_result is None:
                break
            result = next_result
            updates += 1
        return result, updates


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OPS-Miner: length-2 scan and pattern-fusion reuse"
    )
    parser.add_argument("dataset", help="Path to a float64 binary time series")
    parser.add_argument("--window", type=int, required=True)
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--minsup", "--min-sup", type=int, required=True)
    parser.add_argument("--updates", type=int, default=None)
    args = parser.parse_args()

    algorithm = OPSMiner(
        args.window,
        args.step,
        args.minsup,
    )
    values = np.memmap(args.dataset, dtype="<f8", mode="r")
    result, updates = algorithm.run(values, args.updates)
    print(f"Data length: {len(algorithm.data)}")
    print(f"Window size: {args.window}")
    print(f"Step size: {args.step}")
    print(f"Minimum support: {args.minsup}")
    print(f"Updates: {updates}")
    print(f"Level counts: {[len(level) for level in result]}")
    print(f"Total frequent patterns: {sum(map(len, result))}")
