"""OPS-Enum: SOPP extension enumeration before PPC."""

import argparse
import time

import numpy as np


def sort(src):
    src = np.array(src)
    src = src.argsort()
    src = src.argsort() + 1
    return src.tolist()


class OPSEnumMiner:
    def __init__(self, window_size, step_size, min_sup):
        self.window_size = int(window_size)
        self.step_size = int(step_size)
        self.min_sup = int(min_sup)
        self.data = np.empty(0, dtype=np.float64)
        self.initial_runtime = 0.0
        self.update_runtimes = []
        # Enumeration has a natural stable key: a frequent prefix pattern and
        # its appended rank.  Cache the resulting candidate, suffix and
        # endpoint relation so later windows do not rebuild them.
        self.enumeration_cache = {}
        self.fusion_cache = {}
        self.fusion_cache_hits = 0
        self.fusion_cache_misses = 0

    # Not used by the benchmark runner; retained for reference only.
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
        first_window = (
            not hasattr(self, "length_two_ids")
            or self.length_two_ids.size == 0
        )

        if first_window:
            start = time.perf_counter()
            self.data = np.ascontiguousarray(values, dtype=np.float64)
            self.length_two_ids = np.zeros(
                self.data.size, dtype=np.int32
            )
            self.left = 0
            self.right = self.window_size - 1
            endpoints = np.arange(1, self.right + 1, dtype=np.int64)
            left_values = self.data[endpoints - 1]
            right_values = self.data[endpoints]
        else:
            if self.right + self.step_size >= self.data.size:
                return None

            start = time.perf_counter()
            old_left = self.left
            old_right = self.right
            new_left = old_left + self.step_size
            new_right = old_right + self.step_size

            leaving_ids = self.length_two_ids[old_left + 1:new_left + 1]
            removed = np.bincount(leaving_ids, minlength=3)
            removed[0] = 0
            self.length_two_counts -= removed[:3]

            endpoints = np.arange(
                old_right + 1,
                new_right + 1,
                dtype=np.int64,
            )
            left_values = self.data[endpoints - 1]
            right_values = self.data[endpoints]

        ids = np.where(
            left_values < right_values,
            1,
            np.where(left_values > right_values, 2, 0),
        ).astype(np.int32, copy=False)
        self.length_two_ids[endpoints] = ids

        if first_window:
            self.length_two_counts = np.bincount(
                ids, minlength=3
            ).astype(np.int64, copy=False)
            self.length_two_counts[0] = 0
        else:
            added = np.bincount(ids, minlength=3)
            added[0] = 0
            self.length_two_counts += added[:3]
            self.left = new_left
            self.right = new_right

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

        old_data = self.data
        self.data = miner_data
        result = self._find_m(f2, active_ids, [None, (1, 2), (2, 1)])
        self.data = old_data
        position_ids[0] = boundary_id

        if first_window:
            self.initial_runtime = time.perf_counter() - start
            self.update_runtimes = []
        else:
            self.update_runtimes.append(time.perf_counter() - start)
        return result

    def _find_m(self, f2, position_ids, id_to_pattern):
        current_patterns = f2
        current_ids = position_ids
        current_id_to_pattern = id_to_pattern
        levels = []
        while current_patterns:
            levels.append(dict(current_patterns))
            pattern_length = len(next(iter(current_patterns)))
            next_patterns, next_ids, next_id_to_pattern = (
                self._build_next_level(
                    pattern_length,
                    current_patterns,
                    current_ids,
                    current_id_to_pattern,
                )
            )
            if not next_patterns:
                break
            current_patterns = next_patterns
            current_ids = next_ids
            current_id_to_pattern = next_id_to_pattern
        return levels

    def _build_fusion_table(self, current_patterns, id_to_pattern):
        transition = {}
        pattern_to_id = {
            pattern: pattern_id
            for pattern_id, pattern in enumerate(id_to_pattern)
            if pattern is not None
        }
        for prefix_id in range(1, len(id_to_pattern)):
            pattern = id_to_pattern[prefix_id]
            if pattern not in current_patterns:
                continue
            if current_patterns[pattern] < self.min_sup:
                continue

            pattern_length = len(pattern)
            for extension_value in range(1, pattern_length + 2):
                cache_key = (tuple(pattern), int(extension_value))
                cached = self.enumeration_cache.get(cache_key)
                if cached is None:
                    super_pattern = list(pattern)
                    super_pattern.append(extension_value)
                    for i in range(pattern_length):
                        if super_pattern[i] >= super_pattern[-1]:
                            super_pattern[i] += 1

                    suffix = super_pattern[1:]
                    for i in range(pattern_length):
                        if suffix[i] > super_pattern[0]:
                            suffix[i] -= 1
                    candidate = tuple(super_pattern)
                    suffix_pattern = tuple(suffix)
                    if pattern[0] == suffix_pattern[-1]:
                        relation = 1 if candidate[0] < candidate[-1] else 2
                    else:
                        relation = 0
                    cached = (candidate, suffix_pattern, relation)
                    self.enumeration_cache[cache_key] = cached
                candidate, suffix_pattern, relation = cached

                suffix_id = pattern_to_id.get(suffix_pattern)
                if suffix_id is None:
                    continue
                if suffix_pattern not in current_patterns:
                    continue
                if current_patterns[suffix_pattern] < self.min_sup:
                    continue

                # Count and reuse only candidates that survive the enum
                # suffix/parent checks, matching OPS-PF's candidate semantics.
                fusion_key = (tuple(pattern), suffix_pattern, int(relation))
                if fusion_key in self.fusion_cache:
                    candidate = self.fusion_cache[fusion_key]
                    self.fusion_cache_hits += 1
                else:
                    self.fusion_cache[fusion_key] = candidate
                    self.fusion_cache_misses += 1

                if pattern[0] == suffix_pattern[-1]:
                    if relation == 1:
                        transition[(prefix_id, suffix_id, 1)] = candidate
                    elif relation == 2:
                        transition[(prefix_id, suffix_id, 2)] = candidate
                else:
                    transition[(prefix_id, suffix_id, 0)] = candidate
                    transition[(prefix_id, suffix_id, 1)] = candidate
                    transition[(prefix_id, suffix_id, 2)] = candidate
        return transition

    def _build_next_level(
        self,
        pattern_length,
        current_patterns,
        current_ids,
        id_to_pattern,
    ):
        data_size = self.data.size
        next_ids = np.zeros(data_size, dtype=np.int32)

        # EFO prefix/suffix pairing and parent-support pruning are applied
        # before PPC. All possible super-patterns are generated here.
        transition = self._build_fusion_table(
            current_patterns,
            id_to_pattern,
        )

        prefix_ids = current_ids[:-1]
        suffix_ids = current_ids[1:]
        valid = (prefix_ids != 0) & (suffix_ids != 0)
        aligned_indices = np.flatnonzero(valid)
        if aligned_indices.size == 0:
            return {}, next_ids, [None]

        endpoints = aligned_indices + 1
        starts = endpoints - pattern_length
        tbegin = self.data[starts]
        tend = self.data[endpoints]
        relations = np.where(
            tbegin < tend,
            1,
            np.where(tbegin > tend, 2, 0),
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
            inverse = None
        else:
            unique_keys, inverse, counts = np.unique(
                event_keys,
                return_inverse=True,
                return_counts=True,
            )

        frequent_group = counts >= self.min_sup
        frequent_group_indices = np.flatnonzero(frequent_group)

        candidate_for_group = [None] * unique_keys.size
        frequent_patterns = {}
        for group_index in frequent_group_indices.tolist():
            event_key = int(unique_keys[group_index])
            relation = event_key % 3
            pair_key = event_key // 3
            prefix_id = pair_key // id_base
            suffix_id = pair_key % id_base
            candidate = transition.get(
                (prefix_id, suffix_id, relation)
            )
            candidate_for_group[group_index] = candidate
            if candidate is not None:
                frequent_patterns[candidate] = int(counts[group_index])

        next_id_to_pattern = [None]
        pattern_to_next_id = {}
        for pattern in frequent_patterns:
            pattern_to_next_id[pattern] = len(next_id_to_pattern)
            next_id_to_pattern.append(pattern)

        group_to_next_id = np.zeros(unique_keys.size, dtype=np.int32)
        for group_index, candidate in enumerate(candidate_for_group):
            if candidate is not None:
                group_to_next_id[group_index] = pattern_to_next_id.get(
                    candidate, 0
                )

        if use_bincount:
            key_to_next_id = np.zeros(max_event_key + 1, dtype=np.int32)
            key_to_next_id[unique_keys] = group_to_next_id
            next_ids[endpoints] = key_to_next_id[event_keys]
        else:
            next_ids[endpoints] = group_to_next_id[inverse]
        return frequent_patterns, next_ids, next_id_to_pattern

    def frequent_pattern_fusion(self, p, q, relation):
        p1 = p[0]
        qm = q[-1]

        if p1 < qm:
            r = [p1]
            r.extend(q)
            for i in range(1, len(r)):
                if r[i] >= r[0]:
                    r[i] += 1
            return tuple(r)

        if p1 > qm:
            r = [p1 + 1]
            r.extend(q)
            for i in range(1, len(r)):
                if r[i] >= r[0]:
                    r[i] += 1
            return tuple(r)

        if relation == 0:
            return None

        middle = [value if value < p1 else value + 1 for value in p[1:]]
        if relation == 1:
            return tuple([p1] + middle + [p1 + 1])
        return tuple([p1 + 1] + middle + [p1])

    def run(self, file_path, max_updates=None):
        values = self.read_file(file_path)
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
        description="OPS-Enum: SOPP extension enumeration before PPC"
    )
    parser.add_argument("dataset", help="Path to a numeric time series")
    parser.add_argument("--window", type=int, required=True)
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--minsup", "--min-sup", type=int, required=True)
    parser.add_argument("--updates", type=int, default=None)
    args = parser.parse_args()

    algorithm = OPSEnumMiner(
        args.window,
        args.step,
        args.minsup,
    )
    result, updates = algorithm.run(args.dataset, args.updates)
    print(f"Data length: {len(algorithm.data)}")
    print(f"Window size: {args.window}")
    print(f"Step size: {args.step}")
    print(f"Minimum support: {args.minsup}")
    print(f"Updates: {updates}")
    print(f"Level counts: {[len(level) for level in result]}")
    print(f"Total frequent patterns: {sum(map(len, result))}")
