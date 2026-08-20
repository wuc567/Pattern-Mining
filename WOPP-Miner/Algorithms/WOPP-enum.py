import argparse
import time
from collections import defaultdict

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
        self.operation=0
        self.reset_stats()
        self.candidate_num=0

    def reset_stats(self):
        self.candidate_generated_count = 2
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

    # def cal_occ_2(self, r_len, prefix_occ_bitarray, suffix_occ_bitarray):
    #     cand_occ = prefix_occ_bitarray & suffix_occ_bitarray
    #     occ_r = cand_occ.copy()
    #     occ_h = cand_occ.copy()
    #     occ_index = cand_occ.search(1)

    #     for occ in occ_index:
    #         t_begin = self.current_window_data[occ - r_len + 1]
    #         t_end = self.current_window_data[occ]

    #         if t_begin == t_end:
    #             occ_r[occ] = 0
    #             occ_h[occ] = 0
    #             continue

    #         if t_begin < t_end:
    #             occ_h[occ] = 0
    #         else:
    #             occ_r[occ] = 0

    #     prefix_occ_bitarray ^= cand_occ
    #     suffix_occ_bitarray ^= cand_occ
    #     self.support_calc_count += 1
    #     return occ_r, occ_h
    def cal_occ_r(self, r_len, cand_occ,prefix_occ_bitarray, suffix_occ_bitarray):
        occ_r = cand_occ.copy()
        occ_index = cand_occ.search(1)

        for occ in occ_index:
            t_begin = self.current_window_data[occ - r_len + 1]
            t_end = self.current_window_data[occ]
            if t_begin >= t_end:
                occ_r[occ] = 0

        prefix_occ_bitarray ^= occ_r
        suffix_occ_bitarray ^= occ_r
        self.support_calc_count += 1
        return occ_r

    def cal_occ_h(self, r_len, cand_occ,prefix_occ_bitarray, suffix_occ_bitarray):
        occ_h = cand_occ.copy()
        occ_index = cand_occ.search(1)

        for occ in occ_index:
            t_begin = self.current_window_data[occ - r_len + 1]
            t_end = self.current_window_data[occ]
            if t_begin <= t_end:
                occ_h[occ] = 0
        prefix_occ_bitarray ^= occ_h
        suffix_occ_bitarray ^= occ_h
        self.support_calc_count += 1
        return occ_h
    

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
            f2[(1, 2)] = occ_r
            self.Flist.append((1, 2))
            self.candidate_num+=1

        if sup_h >= self.min_sup:
            f2[(2, 1)] = occ_h
            self.Flist.append((2, 1))
            self.candidate_num+=1

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


            for p in sorted(current_patterns):
                if p in prefix_occ_map:
                    self.operation += 1
                    try:
                        p_len = len(p)
                        for i in range(1, p_len + 2):
                            self.operation+=1
                            super_op = list(p)
                            super_op.append(i)
                            for j in range(p_len):
                                if super_op[j] >= super_op[-1]:
                                    super_op[j] += 1

                            suffix_sup = super_op[1:]
                            for j in range(p_len):
                                if suffix_sup[j] > super_op[0]:
                                    suffix_sup[j] -= 1
                            q = tuple(suffix_sup)

                            if q in suffix_occ_map and q in current_patterns:
                                if prefix_occ_map[p].count(1) >= self.min_sup and suffix_occ_map[q].count(1) >= self.min_sup:
                                    self.candidate_generated_count += 1
                                
                                    if p[0] == q[-1]:
                                        
                                        cand_occ = prefix_occ_map[p] & suffix_occ_map[q]
                                        if super_op[0] < super_op[-1]:
                                            
                                            cand = tuple(super_op)
                                            self.candidate_checked_count += 1
                                            self.fusion_count += 1
                                            occ_r = self.cal_occ_r(len(super_op),cand_occ,prefix_occ_map[p],suffix_occ_map[q])

                                            if prefix_occ_map[p].count(1) < self.min_sup:
                                                del prefix_occ_map[p]
                                            if suffix_occ_map[q].count(1) < self.min_sup:
                                                del suffix_occ_map[q]
                                            if occ_r.count(1) >= self.min_sup:
                                                next_patterns[cand] = occ_r

                                        if super_op[0] > super_op[-1]:
                                            
                                            cand = tuple(super_op)
                                            self.candidate_checked_count += 1
                                            self.fusion_count += 1
                                            
                                            occ_h = self.cal_occ_h(len(super_op),cand_occ,prefix_occ_map[p],suffix_occ_map[q])

                                            if prefix_occ_map[p].count(1) < self.min_sup:
                                                del prefix_occ_map[p]
                                            if suffix_occ_map[q].count(1) < self.min_sup:
                                                del suffix_occ_map[q]
                                            if occ_h.count(1) >= self.min_sup:
                                                next_patterns[cand] = occ_h

                                    if p[0] != q[-1]:
                                        cand = tuple(super_op)
                                        
                                        self.candidate_checked_count += 1
                                        self.fusion_count += 1
                                        supp_occ = self.cal_occ(prefix_occ_map[p], suffix_occ_map[q])
                                        
                                        if prefix_occ_map[p].count(1) < self.min_sup:
                                            del prefix_occ_map[p]
                                        if suffix_occ_map[q].count(1) < self.min_sup:
                                            del suffix_occ_map[q]
                                        if supp_occ.count(1) >= self.min_sup:
                                            next_patterns[cand] = supp_occ
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
