import argparse
import copy
import time
from collections import defaultdict

from bitarray import bitarray


class WindowOPRMinerOptimized:
    def __init__(self, window_len, step=None, min_sup=12):
        self.window_len = window_len
        self.step = window_len if step is None else step
        self.min_sup = min_sup

        self.prefix_pattern_dict = defaultdict(list)
        self.suffix_pattern_dict = {}

        self.window_level_results = []
        self.window_stats = []
        self.current_window_data = []
        self.S = []
        self.Cd = []
        self.Cd2 = []
        self.Z = []
        self.Z2 = []
        self.Flist = []
        self.level_counts = []
        self.candidate_generated_count = 0
        self.operation = 0
        self.reset_stats()

    def reset_stats(self):
        self.candidate_checked_count = 2
        self.fusion_count = 0
        self.support_calc_count = 0
        self.runtime = 0.0

    def make_occ_list(self, occs):
        occ_list = [occs.count(1)]
        occ_list.extend(occs.search(1))
        return occ_list

    def make_occ_bitarray(self, occ_list):
        occs = bitarray(len(self.current_window_data))
        occs.setall(0)
        for occ in occ_list:
            occs[occ] = 1
        return occs

    def make_occ_list_from_value(self, occs):
        if isinstance(occs, bitarray):
            return self.make_occ_list(occs)
        return list(occs)

    def grow_BaseP1(self, Ld, L):
        p, q = copy.deepcopy(L), copy.deepcopy(Ld)
        i, j = 1, 1
        Z = []
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i] + 1:
                    Z.append(copy.deepcopy(q[j]))
                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break

        L[0] = L[0] - len(Z)
        Ld[0] = Ld[0] - len(Z)
        self.support_calc_count += 1
        return self.make_occ_bitarray(Z)

    def grow_BaseP2(self, slen, Ld, L):
        first, fri, i, j = 0, 0, 1, 1
        p, q = copy.deepcopy(L), copy.deepcopy(Ld)
        Z = []
        Z2 = []
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i] + 1:
                    first = q[j]
                    fri = first - slen
                    if self.current_window_data[first] > self.current_window_data[fri]:
                        Z.append(copy.deepcopy(q[j]))
                    elif self.current_window_data[first] != self.current_window_data[fri]:
                        Z2.append(copy.deepcopy(q[j]))
                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break

        L[0] = L[0] - len(Z) - len(Z2)
        Ld[0] = Ld[0] - len(Z) - len(Z2)
        self.support_calc_count += 1
        return self.make_occ_bitarray(Z), self.make_occ_bitarray(Z2)

    def fuse_patterns(self, p, q):
        p1 = p[0]
        qm = q[-1]
        candidates = []

        if p1 != qm:
            r = []
            if p[0] < q[len(q) - 1]:
                r.append(p[0])
            else:
                r.append(p[0] + 1)
            r.extend(list(q))
            for i in range(1, len(r)):
                if r[i] >= r[0]:
                    r[i] += 1
            candidates.append(tuple(r))

        if p1 == qm:
            r = list(p)
            r.append(q[len(q) - 1])
            h = list(p)
            h.append(q[len(q) - 1])
            for i in range(1, len(r)):
                if r[i] > r[0]:
                    r[i] += 1
                if h[i] > h[0]:
                    h[i] += 1
            r[len(r) - 1] += 1
            h[0] += 1

            candidates.append(tuple(r))
            candidates.append(tuple(h))

        return candidates

    def find_2(self):
        self.Cd.clear()
        self.Cd2.clear()
        self.Z.clear()
        self.Z2.clear()

        i, j = 0, 1
        self.Cd.append(1)
        self.Cd.append(2)
        self.Cd2.append(2)
        self.Cd2.append(1)
        while j < len(self.S):
            if self.S[j] > self.S[i]:
                self.Z.append(j + 1)
            elif self.S[j] != self.S[i]:
                self.Z2.append(j + 1)
            i = i + 1
            j = j + 1

        f2 = {}
        sup_r = len(self.Z)
        sup_h = len(self.Z2)

        if sup_r >= self.min_sup:
            f2[tuple(self.Cd)] = [sup_r] + self.Z
            self.Flist.append((1, 2))

        if sup_h >= self.min_sup:
            f2[tuple(self.Cd2)] = [sup_h] + self.Z2
            self.Flist.append((2, 1))

        return f2

    def find_m(self, f2):
        current_patterns = f2
        self.level_counts = []
        self.prefix_pattern_dict.clear()
        self.suffix_pattern_dict.clear()

        while current_patterns:
            self.level_counts.append(len(current_patterns))

            next_patterns = {}
            next_prefix_pattern_dict = defaultdict(list)
            next_suffix_pattern_dict = {}

            Lb = []
            slen = len(next(iter(current_patterns)))

            fre = copy.deepcopy(list(current_patterns.keys()))
            fre_number = copy.deepcopy(len(fre))
            pos = []

            for p in fre:
                occ_list = self.make_occ_list_from_value(current_patterns[p])
                pos.append(copy.deepcopy(occ_list[1:]))

            for x in range(fre_number):
                Lb.append([])

            self.Cd.clear()
            self.Cd2.clear()
            for y in range(slen + 1):
                self.Cd.append(0)
                self.Cd2.append(0)

            prefix_occ_list_map = {}
            suffix_occ_list_map = {}

            for s in range(fre_number):
                Lb[s].append(len(pos[s]))
                for d in range(len(pos[s])):
                    Lb[s].append(copy.deepcopy(pos[s][d]))
            
                prefix_occ_list_map[fre[s]] = Lb[s].copy()
                suffix_occ_list_map[fre[s]] = Lb[s].copy()

            for i in range(fre_number):
                p = fre[i]
                if p in prefix_occ_list_map:
                    self.operation += 1
                    try:
                        if len(p) == 2:
                            matching_qs = list(current_patterns.keys())
                        else:
                            suffix_p = self.suffix_pattern_dict[p]
                            matching_qs = self.prefix_pattern_dict[suffix_p]

                        for q in matching_qs:
                            self.operation += 1
                            if q in suffix_occ_list_map:
                                candidates_to_check = self.fuse_patterns(p, q)
                                self.fusion_count += len(candidates_to_check)

                                self.candidate_checked_count += len(candidates_to_check)

                                if prefix_occ_list_map[p][0] >= self.min_sup and suffix_occ_list_map[q][0] >= self.min_sup:
                                    if p[0] != q[-1]:
                                        self.candidate_generated_count += 1
                                        supp_occ = self.grow_BaseP1(suffix_occ_list_map[q], prefix_occ_list_map[p])

                                        sup_cand = supp_occ.count(1)

                                        if sup_cand >= self.min_sup:
                                            for cand in candidates_to_check:
                                                next_patterns[cand] = supp_occ
                                                next_prefix_pattern_dict[p].append(cand)
                                                next_suffix_pattern_dict[cand] = q
                                        if prefix_occ_list_map[p][0] < self.min_sup:
                                            del prefix_occ_list_map[p]
                                        if suffix_occ_list_map[q][0] < self.min_sup:
                                            del suffix_occ_list_map[q]
                                    else:
                                        self.candidate_generated_count += 2
                                        occ_r, occ_h = self.grow_BaseP2(
                                            len(p), suffix_occ_list_map[q], prefix_occ_list_map[p])

                                        for cand in candidates_to_check:
                                            if cand[0] < cand[-1]:
                                                sup_r = occ_r.count(1)
                                                if sup_r >= self.min_sup:
                                                    next_patterns[cand] = occ_r
                                                    next_prefix_pattern_dict[p].append(cand)
                                                    next_suffix_pattern_dict[cand] = q
                                            else:
                                                sup_h = occ_h.count(1)
                                                if sup_h >= self.min_sup:
                                                    next_patterns[cand] = occ_h
                                                    next_prefix_pattern_dict[p].append(cand)
                                                    next_suffix_pattern_dict[cand] = q
                                        if prefix_occ_list_map[p][0] < self.min_sup:
                                            del prefix_occ_list_map[p]
                                        if suffix_occ_list_map[q][0] < self.min_sup:
                                            del suffix_occ_list_map[q]
                    except KeyError:
                        continue

            if not next_patterns:
                break

            current_patterns = next_patterns
            self.prefix_pattern_dict = next_prefix_pattern_dict
            self.suffix_pattern_dict = next_suffix_pattern_dict

    def mine_window(self, window_data, window_id=1):
        self.prefix_pattern_dict.clear()
        self.suffix_pattern_dict.clear()
        self.Flist.clear()
        self.level_counts = []
        self.reset_stats()
        self.candidate_generated_count += 2

        start = time.perf_counter()
        self.S = window_data
        self.current_window_data = [0] + window_data

        f2 = self.find_2()
        self.find_m(f2)

        self.window_level_results.append(self.level_counts.copy())
        self.runtime = time.perf_counter() - start

        stats = self.stats_dict()
        stats["window_id"] = window_id
        stats["level_counts"] = self.level_counts.copy()
        self.window_stats.append(stats)

    def run(self, data, dates=None):
        self.window_level_results.clear()
        self.window_stats.clear()
        self.candidate_generated_count = 0
        self.operation = 0

        for i, (window_data, _start_idx) in enumerate(self.get_windows(data)):
            self.mine_window(window_data, window_id=i + 1)

        return self.window_level_results

    def get_windows(self, data):
        n = len(data)
        for i in range(0, n - self.window_len + 1, self.step):
            yield data[i : i + self.window_len], i

    def stats_dict(self):
        return {
            "candidate_generated_count": self.candidate_generated_count,
            "candidate_checked_count": self.candidate_checked_count,
            "fusion_count": self.fusion_count,
            "support_calc_count": self.support_calc_count,
            "runtime": self.runtime,
            "operation": self.operation,
        }


WindowOPRCleanPQMiner = WindowOPRMinerOptimized


def read_numeric_series(file_name):
    data = []
    with open(file_name, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            for value in line.replace(",", " ").split():
                try:
                    data.append(float(value))
                except ValueError:
                    continue
    return data


def main():
    parser = argparse.ArgumentParser(description="Clean WOPP miner")
    parser.add_argument(
        "dataset",
        nargs="?",
        default="/Users/zyj/Desktop/WOPP消融实验/AAPL.txt",
    )
    parser.add_argument("--window-len", type=int, default=None)
    parser.add_argument("--step", type=int, default=None)
    parser.add_argument("--min-sup", type=int, default=12)
    args = parser.parse_args()

    data = read_numeric_series(args.dataset)
    if not data:
        raise ValueError(f"No numeric values read from {args.dataset}")

    window_len = args.window_len or len(data)
    step = args.step or window_len

    start = time.perf_counter()
    miner = WindowOPRMinerOptimized(
        window_len=window_len,
        step=step,
        min_sup=args.min_sup,
    )
    miner.run(data)
    total_time = time.perf_counter() - start

    print(f"Execution time: {total_time:.6f} seconds")
    print(f"Window count: {len(miner.window_level_results)}")
    if miner.window_level_results:
        print(f"Last window level counts: {miner.window_level_results[-1]}")
    if miner.window_stats:
        print(f"Last window stats: {miner.window_stats[-1]}")


if __name__ == "__main__":
    main()
