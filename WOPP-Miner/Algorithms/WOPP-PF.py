import argparse
import copy
import time
from collections import defaultdict

import numpy as np
from bitarray import bitarray


class WindowOPRMinerOptimized:
    def __init__(self, window_len, step=None, min_sup=12):
        self.window_len = window_len
        self.step = window_len if step is None else step
        self.min_sup = min_sup

        self.candidate_dict = {}
        self.pattern_fusion_dict = defaultdict(list)

        self.window_level_results = []
        self.window_stats = []
        self.current_window_data = []
        self.Flist = []
        self.level_counts = []
        self.candidate_generated_count = 0
        self.operation=0
        self.reset_stats()
        self.candidate_num=0

    def reset_stats(self):
        self.candidate_checked_count = 2
        self.fusion_count = 0
        self.cached_fusion_hit_count = 0
        self.support_calc_count = 0
        self.runtime = 0.0

    def cal_occ(self, prefix_occ_bitarray, suffix_occ_bitarray):
        cand_occ = prefix_occ_bitarray & suffix_occ_bitarray
        prefix_occ_bitarray ^= cand_occ
        suffix_occ_bitarray ^= cand_occ
        self.support_calc_count += 1
        return cand_occ

    def cal_occ_2(self, r_len, prefix_occ_bitarray, suffix_occ_bitarray):
        cand_occ = prefix_occ_bitarray & suffix_occ_bitarray
        occ_r = cand_occ.copy()
        occ_h = cand_occ.copy()
        occ_index = cand_occ.search(1)

        for occ in occ_index:
            t_begin = self.current_window_data[occ - r_len + 1]
            t_end = self.current_window_data[occ]

            if t_begin == t_end:
                occ_r[occ] = 0
                occ_h[occ] = 0
                continue

            if t_begin < t_end:
                occ_h[occ] = 0
            else:
                occ_r[occ] = 0

        prefix_occ_bitarray ^= cand_occ
        suffix_occ_bitarray ^= cand_occ
        self.support_calc_count += 1
        return occ_r, occ_h

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

    def sort(self, src):
        src = np.array(src)
        src = src.argsort()
        src = src.argsort() + 1
        return src.tolist()

    def find_2(self):
        t_size = len(self.current_window_data) - 1
        occ_r = bitarray(t_size + 1)
        occ_r.setall(0)
        occ_h = bitarray(t_size + 1)
        occ_h.setall(0)

        for i in range(1, t_size):
            if self.current_window_data[i] < self.current_window_data[i + 1]:
                occ_r[i + 1] = 1
            elif self.current_window_data[i] > self.current_window_data[i + 1]:
                occ_h[i + 1] = 1

        f2 = {}
        sup_r = occ_r.count(1)
        sup_h = occ_h.count(1)

        if sup_r >= self.min_sup:
            self.candidate_num+=1
            f2[(1, 2)] = occ_r
            self.Flist.append((1, 2))

        if sup_h >= self.min_sup:
            self.candidate_num+=1
            f2[(2, 1)] = occ_h
            self.Flist.append((2, 1))

        return f2

    def find_m(self, f2):
        current_patterns = f2
        self.level_counts = []
        self.pattern_fusion_dict.clear()

        while current_patterns:
            self.level_counts.append(len(current_patterns))

            next_patterns = {}

            prefix_occ_map = {}
            suffix_occ_map = {}

            for p, occs in current_patterns.items():
                prefix_occ_map[p] = bitarray("0") + occs[:-1]
                suffix_occ_map[p] = occs.copy()


            patterns = list(current_patterns.keys()).copy()
            pattern_number = len(patterns)
            slen = len(patterns[0])
            Cd = [0] * (slen + 1)
            Cd2 = [0] * (slen + 1)

            for i in range(pattern_number):
                self.operation+=1
                p = patterns[i]
                Q = copy.deepcopy(list(p))
                Q = Q[1:]
                q_suffix = self.sort(Q)

                for j in range(pattern_number):
                    self.operation+=1
                    q = patterns[j]

                    try:
                        if prefix_occ_map[p].count(1) >= self.min_sup and suffix_occ_map[q].count(1) >= self.min_sup:
                            R = copy.deepcopy(list(q))
                            R.pop()
                            r_prefix = self.sort(R)
                            if q_suffix == r_prefix:
                                if p[0] == q[slen - 1]:
                                    self.candidate_num+=2
                                    Cd[0] = p[0]
                                    Cd2[0] = p[0] + 1
                                    Cd[slen] = p[0] + 1
                                    Cd2[slen] = p[0]
                                    for t in range(1, slen):
                                        if p[t] > q[slen - 1]:
                                            Cd[t] = p[t] + 1
                                            Cd2[t] = p[t] + 1
                                        else:
                                            Cd[t] = p[t]
                                            Cd2[t] = p[t]
                                    candidates_to_check = [tuple(Cd), tuple(Cd2)]
                                elif p[0] < q[slen - 1]:
                                    self.candidate_num+=1
                                    Cd[0] = p[0]
                                    Cd[slen] = q[slen - 1] + 1
                                    for t in range(1, slen):
                                        if p[t] > q[slen - 1]:
                                            Cd[t] = p[t] + 1
                                        else:
                                            Cd[t] = p[t]
                                    candidates_to_check = [tuple(Cd)]
                                else:
                                    self.candidate_num+=1
                                    Cd[0] = p[0] + 1
                                    Cd[slen] = q[slen - 1]
                                    for t in range(slen - 1):
                                        if q[t] > p[0]:
                                            Cd[t + 1] = q[t] + 1
                                        else:
                                            Cd[t + 1] = q[t]
                                    candidates_to_check = [tuple(Cd)]

                                self.candidate_generated_count += len(candidates_to_check)
                                self.fusion_count += len(candidates_to_check)

                                self.candidate_checked_count += len(candidates_to_check)

                                if p[0] != q[-1]:
                                    supp_occ = self.cal_occ(prefix_occ_map[p], suffix_occ_map[q])
                                    sup_cand = supp_occ.count(1)

                                    if sup_cand >= self.min_sup:
                                        for cand in candidates_to_check:
                                            next_patterns[cand] = supp_occ
                                    if prefix_occ_map[p].count(1) < self.min_sup:
                                        del prefix_occ_map[p]

                                    if suffix_occ_map[q].count(1) < self.min_sup:
                                        del suffix_occ_map[q]

                                else:
                                    occ_r, occ_h = self.cal_occ_2(
                                        len(p) + 1, prefix_occ_map[p], suffix_occ_map[q]
                                    )

                                    for cand in candidates_to_check:
                                        if cand[0] < cand[-1]:
                                            sup_r = occ_r.count(1)
                                            if sup_r >= self.min_sup:
                                                next_patterns[cand] = occ_r
                                        else:
                                            sup_h = occ_h.count(1)
                                            if sup_h >= self.min_sup:
                                                next_patterns[cand] = occ_h
                                    if prefix_occ_map[p].count(1) < self.min_sup:
                                        del prefix_occ_map[p]

                                    if suffix_occ_map[q].count(1) < self.min_sup:
                                        del suffix_occ_map[q]
                    except KeyError:
                        continue


            if not next_patterns:
                break

            current_patterns = next_patterns

    def mine_window(self, window_data, window_id=1):
        self.pattern_fusion_dict.clear()
        self.Flist.clear()
        self.level_counts = []
        self.reset_stats()
        self.candidate_generated_count += 2

        start = time.perf_counter()
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
            "cached_fusion_hit_count": self.cached_fusion_hit_count,
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

    windowsize = len(data)
    window_len = args.window_len or windowsize
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
