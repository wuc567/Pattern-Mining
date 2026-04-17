# -*- coding: utf-8 -*-

import ast
import json
import copy

import time
from collections import defaultdict

class Sanitizer2:

    def __init__(self):
        pass

    def convert_S_to_dataset(self, S, SeqNum):
        dataset = [{} for _ in range(SeqNum)]
        for item, sequences in S.items():
            for transaction_id, positions in enumerate(sequences):
                if len(positions) > 0:
                    dataset[transaction_id][item] = len(positions)
        return dataset

    def compute_risu(self, dataset, sensitive_patterns, external_utilities):
        risu = defaultdict(int)

        item_count_in_sen_patterns = defaultdict(int)
        for pattern in sensitive_patterns:
            for item in pattern:
                item_count_in_sen_patterns[item] += 1

        matched_items = set()
        for transaction in dataset:
            for pattern in sensitive_patterns:
                if set(pattern).issubset(set(transaction.keys())):
                    matched_items.update(pattern)

        for item in matched_items:
            internal_utility = item_count_in_sen_patterns[item]
            external_utility = external_utilities.get(item, 1)
            risu[item] += internal_utility * external_utility

        return risu

    def classify_pattern(self, util, minutil, epsilon, delta):
        diff = int(util) - int(minutil)

        if 0 <= diff <= epsilon:
            priority_level = "High"
        #elif delta < diff <= epsilon:
            #priority_level = "Moderate"
        else:  # diff > epsilon
            priority_level = "Low"

        return priority_level, diff

    def assign_priority(self, priority_level):
        priority_map = {
            "High": 2,
            #"Moderate": 2,
            "Low": 1
        }
        return priority_map.get(priority_level, 1)


    def compute_epsilon_delta_by_utility(self, util_list, minutil, steps=2, delta_ratio=0.2):
        if not util_list:
            return 1, 1
        max_util = max(util_list)
        R = float(max_util) - float(minutil)
        if R <= 0:
            return 1.0, 1.0
        epsilon = max(1.0, (R / steps))
        delta = max(1.0, (epsilon * delta_ratio))
        return epsilon, delta


    def _get_cached_occurrences(self, pattern, pattern_ItemS_map, seq_num=None):
        if pattern_ItemS_map is None:
            return []

        entry = pattern_ItemS_map.get(str(pattern))
        if entry is None:
            return []

        if isinstance(entry, list) and len(entry) > 0 and isinstance(entry[0], dict) and 'seq' in entry[0]:
            return entry

        normalized = []

        if seq_num is None:
            seq_num = len(entry)
        for seq in range(seq_num):
            poslist = []
            if seq < len(entry):
                poslist = entry[seq] or []
            if poslist:
                normalized.append({"seq": seq, "positions": poslist})
        return normalized


    def build_sensitive_meta(self, sensitive_patterns, mine_cache, epsilon, delta, minutil):
        meta = []
        util_map = mine_cache.get("util_map", {})
        pattern_ItemS_map = mine_cache.get("pattern_ItemS", {})
        seq_num = mine_cache.get("seq_num", None)

        for p in sensitive_patterns:
            p_str = str(p)

            util = util_map.get(p_str, 0.0)

            priority_level, diff = self.classify_pattern(util, minutil, epsilon, delta)
            priority = self.assign_priority(priority_level)

            occurrences = self._get_cached_occurrences(p_str, pattern_ItemS_map, seq_num)

            meta.append({
                "pattern": [i[0] for i in p] if isinstance(p[0], list) else p,
                "util": util,
                "util_after": util,  # 初始为相同值
                "priority_level": priority_level,
                "diff": diff,
                "priority": priority,
                "status": "pending",
                "occurrences": occurrences
            })

        return meta


    def group_meta_by_partition(self, meta_list):
        grouped = defaultdict(list)
        for m in meta_list:
            priority_level = m['priority_level']  # "High" / "Moderate" / "Low"
            grouped[priority_level].append(m)
        return grouped


    def compute_seq_overlap(self, non_sensitive_patterns, mine_cache):
        pattern_ItemS_map = mine_cache.get("pattern_ItemS", {})
        seq_num = mine_cache.get("seq_num", None)
        util_dict = mine_cache.get("Utility", {})
        overlap = defaultdict(int)

        for nsp in non_sensitive_patterns:
            p_str = str(nsp)
            occs = self._get_cached_occurrences(p_str, pattern_ItemS_map, seq_num)
            if not occs:
                continue
            nsp_util = 0
            nsp_list = ast.literal_eval(nsp)
            for item in nsp_list:
                nsp_util += util_dict.get(item)

            for occ in occs:
                seq_id = occ.get("seq")
                positions = occ.get("positions", [])
                if seq_id is not None:
                    overlap[seq_id] += len(positions)

        return overlap


    def prefix_overlap(self, sensitive_pattern, non_sensitive_patterns, threshold=0.8):
        for nsp in non_sensitive_patterns:
            if len(nsp) < len(sensitive_pattern):
                continue
            overlap_len = 0
            for i in range(len(sensitive_pattern)):
                if i >= len(nsp):
                    break
                if sensitive_pattern[i] == nsp[i]:
                    overlap_len += 1
                else:
                    break
            if overlap_len / len(sensitive_pattern) >= threshold:
                return True
        return False


    def select_sacrifice_sequence(self, meta, non_sensitive_patterns, seq_overlap=None, alpha=1.0):
        best_occ = None
        best_score = -float("inf")
        occs = meta.get("occurrences", [])
        if not occs:
            return None

        for occ in occs:
            seq_id = occ["seq"]
            num_positions = len(occ.get("positions", []))
            sensitive_contrib = num_positions or meta.get("util", 1.0)
            overlap_penalty = seq_overlap.get(seq_id, 0) if seq_overlap else 0
            score = sensitive_contrib - overlap_penalty

            if score > best_score:
                best_score = score
                best_occ = occ
        return best_occ


    def select_victim_items_by_partition(self, meta, priority_level, risu_values, dataset, non_sensitive_patterns,
                                         best_occ):
        victim_items = {}
        seq_id = best_occ["seq"]
        positions = best_occ.get("positions", [])

        pattern = meta['pattern']

        use_tail = False
        if non_sensitive_patterns and self.prefix_overlap(pattern, non_sensitive_patterns, threshold=0.8):
            use_tail = True

        chosen = None

        if priority_level == "High":
            pattern_risu = {x: risu_values.get(x, float("inf")) for x in pattern}
            chosen = min(pattern_risu, key=pattern_risu.get)

        elif priority_level == "Low":
            pattern_risu = {x: risu_values.get(x, float("inf")) for x in pattern}
            chosen = max(pattern_risu, key=pattern_risu.get)

        victim_items[tuple(meta["pattern"])] = {
            "victim": chosen,
            "use_tail": use_tail,
            "seq_id": seq_id,
            "positions": positions
        }
        return victim_items

    def _get_position_priority(self, pos, occurrence, victim_idx):
        if victim_idx == 0:
            return (0, pos)  # occurrence 的第一个位置
        elif victim_idx == len(occurrence) - 1:
            return (1, pos)  # occurrence 的最后一个位置
        else:
            return (2, pos)  # occurrence 的中间位置

    def _select_best_position_to_delete(self, victim_item, seq_id, S, pattern_positions, pattern):
        if victim_item not in S or seq_id >= len(S[victim_item]):
            return None, None

        available_positions = S[victim_item][seq_id]

        if not available_positions:
            return None, None

        victim_indices = [idx for idx, item in enumerate(pattern) if item == victim_item]

        if not victim_indices:
            return None, None

        candidates = []

        for occ_idx, occurrence in enumerate(pattern_positions):

            if isinstance(occurrence, tuple):
                occurrence = list(occurrence)

            if not isinstance(occurrence, list) or not occurrence:
                continue

            for victim_idx in victim_indices:
                if victim_idx >= len(occurrence):
                    continue

                pos = occurrence[victim_idx]

                if pos in available_positions:
                    priority, _ = self._get_position_priority(pos, occurrence, victim_idx)
                    candidates.append((occ_idx, pos, priority, victim_idx))  # 保存 victim_idx 用于调试

        if not candidates:
            return None, None

        candidates.sort(key=lambda x: (x[2], x[1]))

        best_occ_idx, best_pos, best_priority, best_victim_idx = candidates[0]

        return best_occ_idx, best_pos


    def apply_modification(self, S2, best_seq, victim_item, sanitize_mode, pattern):
        removed_count = 0
        if not best_seq or not victim_item:
            return S2, removed_count

        seq_id = best_seq.get("seq")
        positions = best_seq.get("positions", [])

        if sanitize_mode == "delete":
            occ_idx, pos_to_remove = self._select_best_position_to_delete(
                victim_item, seq_id, S2, positions, pattern
            )
            if pos_to_remove is not None:
                if victim_item in S2 and seq_id < len(S2[victim_item]):
                    if pos_to_remove in S2[victim_item][seq_id]:
                        S2[victim_item][seq_id].remove(pos_to_remove)
                        removed_count += 1
            return S2, removed_count


        elif sanitize_mode == "tail":
            for occurrence in positions:
                if not occurrence or not isinstance(occurrence, (list, tuple)):
                    continue

                if isinstance(occurrence, tuple):
                    occurrence = list(occurrence)

                last_pos = occurrence[-1]

                if victim_item in S2 and seq_id < len(S2[victim_item]):
                    if last_pos in S2[victim_item][seq_id]:
                        S2[victim_item][seq_id].remove(last_pos)
                        removed_count += 1

            return S2, removed_count

        return S2, removed_count

    def normalize_S(self, S, seq_num):
        for item in S:
            if len(S[item]) < seq_num:
                S[item].extend([[] for _ in range(seq_num - len(S[item]))])
            for j in range(seq_num):
                if not isinstance(S[item][j], list):
                    S[item][j] = []
        return S


    def _find_pattern_occurrences_incremental(self, pattern, seq_id, S2):
        if not pattern or len(pattern) == 0:
            return []

        first_item = pattern[0]
        if first_item not in S2 or seq_id >= len(S2[first_item]):
            return []

        first_positions = S2[first_item][seq_id]
        if not first_positions:
            return []

        current_paths = [[pos] for pos in first_positions]

        for item_idx in range(1, len(pattern)):
            next_item = pattern[item_idx]
            if next_item not in S2 or seq_id >= len(S2[next_item]):
                return []

            next_positions = S2[next_item][seq_id]
            if not next_positions:
                return []

            new_paths = []
            for path in current_paths:
                last_pos = path[-1]
                for next_pos in next_positions:
                    if next_pos > last_pos:
                        new_paths.append(path + [next_pos])

            current_paths = new_paths

            if not current_paths:
                return []

        return current_paths

    def update_meta_after_modification(self, meta, victim_item, best_seq, S2, external_utilities, minutil,
                                       removed_count):
        seq_id = best_seq["seq"]
        pattern = meta["pattern"]

        new_positions_in_seq = self._find_pattern_occurrences_incremental(pattern, seq_id, S2)
        new_occurrences = []
        for o in meta["occurrences"]:
            if o["seq"] != seq_id:
                new_occurrences.append(o)

        if new_positions_in_seq:
            new_occurrences.append({
                "seq": seq_id,
                "positions": new_positions_in_seq
            })

        meta["occurrences"] = new_occurrences

        pattern_length = len(pattern)

        total_external_utility = 0
        for item in pattern:
            total_external_utility += external_utilities.get(item, 0)

        total_count = 0
        for occ in new_occurrences:
            total_count += len(occ.get("positions", []))

        # 使用 au = (sum of external utilities) * count / pattern_length
        if pattern_length > 0 and total_count > 0:
            new_util_after = (total_external_utility * total_count) / pattern_length
        else:
            new_util_after = 0.0

        meta["util_after"] = max(0, new_util_after)

        if new_util_after < float(minutil):
            meta["status"] = "hidden"
        else:
            meta["status"] = "active"

        return meta

    def sanitize_patterns_by_partition(
            self,
            sensitive_patterns,
            non_sensitive_patterns,
            external_utilities,
            S,
            minutil,

            epsilon=None,
            delta=None,

            mine_cache=None
    ):

        if isinstance(mine_cache, str):
            with open(mine_cache, "r", encoding="utf-8") as f:
                mine_cache = json.load(f)

        util_map = mine_cache.get("util_map", {})
        positions_cache = mine_cache.get("pattern_ItemS", {})
        utility_dict = mine_cache.get("Utility", {})

        if epsilon is None or delta is None:
            util_list = util_map.values()
            epsilon, delta = self.compute_epsilon_delta_by_utility(util_list, minutil)

        meta_list = self.build_sensitive_meta(sensitive_patterns, mine_cache, epsilon, delta, minutil)

        partitions = self.group_meta_by_partition(meta_list)

        partition_priority = [
            "High",  # 0 ≤ diff ≤ delta (最高优先级)
            #"Moderate",  # delta < diff ≤ epsilon (中等优先级)
            "Low"  # diff > epsilon (低优先级)
        ]

        partition_summary = {
            partition_name: {
                "count": len(metas),
                "total_util": sum(m["util"] for m in metas),
                "avg_util": (sum(m["util"] for m in metas) / len(metas)) if metas else 0
            }
            for partition_name, metas in partitions.items()
        }

        seq_num = mine_cache.get("seq_num", len(next(iter(S.values()), [])))
        dataset = self.convert_S_to_dataset(S, seq_num)
        risu_values = self.compute_risu(dataset, sensitive_patterns, external_utilities)
        seq_overlap = self.compute_seq_overlap(non_sensitive_patterns, mine_cache)

        S2 = copy.deepcopy(S)


        for partition_name in partition_priority:
            if partition_name not in partitions:
                continue

            metas = partitions[partition_name]

            for meta in metas:
                pattern = meta["pattern"]
                util_after = meta.get("util_after", meta.get("util", 0))

                if meta.get("status") == "hidden":
                    continue

                if util_after < float(minutil):
                    meta["status"] = "hidden"
                    continue

                iter_count = 0
                while util_after >= float(minutil):
                    iter_count += 1

                    #  选择牺牲序列
                    best_seq = self.select_sacrifice_sequence(meta, non_sensitive_patterns, seq_overlap)
                    if not best_seq:
                        break

                    #  选择牺牲项
                    priority_level = meta["priority_level"]  # "High" / "Moderate" / "Low"
                    victim_map = self.select_victim_items_by_partition(
                        meta, priority_level, risu_values, dataset,
                        non_sensitive_patterns, best_seq
                    )

                    if not victim_map:
                        break

                    victim_info = victim_map.get(tuple(meta["pattern"]))
                    if not victim_info or not victim_info.get("victim"):
                        break

                    victim_item = victim_info["victim"]
                    sanitize_mode = "tail" if victim_info.get("use_tail") else "delete"

                    seq_id = best_seq["seq"]
                    positions = best_seq.get("positions", [])

                    util_before = meta.get("util_after", meta.get("util", 0.0))

                    S2, removed_count = self.apply_modification(S2, best_seq, victim_item, sanitize_mode,
                                                                meta["pattern"])

                    meta = self.update_meta_after_modification(meta, victim_item, best_seq, S2, external_utilities,
                                                               minutil, removed_count)
                    util_after = meta["util_after"]

                    if util_after < float(minutil):
                        meta["status"] = "hidden"
                        break

                    meta["util_after"] = util_after

                if meta.get("status") != "hidden":
                    meta["status"] = "failed" if util_after >= float(minutil) else "hidden"

        S2 = self.normalize_S(S2, seq_num)
        return S2


if __name__ == "__main__":
    sanitizer = Sanitizer2()


    mine_cache_path = "datasets/test_mine_results.json"

    sensitive_patterns = [[["a"], ["b"]]]
    non_sensitive_patterns = []
    dataset = []
    S = {
        "a": [[0, 2, 5], [1], [2]],
        "b": [[3], [4], [5]]
    }

    S2= sanitizer.sanitize_patterns_by_partition(
        sensitive_patterns=sensitive_patterns,
        non_sensitive_patterns=non_sensitive_patterns,

        external_utilities={},
        S=S,
        minutil=20,


        mine_cache=mine_cache_path
    )

    print(json.dumps(S2, ensure_ascii=False, indent=2))