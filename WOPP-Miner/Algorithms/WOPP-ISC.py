import argparse
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

    def cal_occ_1(self, prefix_occ, suffix_occ):
        cand_occ = prefix_occ & suffix_occ
        prefix_occ -= cand_occ
        suffix_occ -= cand_occ
        self.support_calc_count += 1
        return cand_occ

    # def cal_occ_r(self, r_len,cand_occ,  prefix_occ, suffix_occ):
    #     #cand_occ = prefix_occ & suffix_occ
    #     occ_r = set()
    #     for occ in cand_occ:
    #         t_begin = self.current_window_data[occ - r_len + 1]
    #         t_end = self.current_window_data[occ]
    #         if t_begin == t_end:
    #             continue
    #         if t_begin < t_end:
    #             occ_r.add(occ)
    #         else:
    #             continue
    #     prefix_occ -= occ_r
    #     suffix_occ -= occ_r


    #     return occ_r

    # def cal_occ_h(self, r_len, cand_occ,  prefix_occ, suffix_occ):
    #     #cand_occ=prefix_occ &suffix_occ
    #     occ_h = set()
    #     for occ in cand_occ:
    #         t_begin = self.current_window_data[occ - r_len + 1]
    #         t_end = self.current_window_data[occ]
    #         if t_begin == t_end:
    #             continue
    #         if t_begin < t_end:
    #             continue
    #         else:
    #             occ_h.add(occ)
    #     prefix_occ -= occ_h
    #     suffix_occ -= occ_h


    #     return occ_h
    
    
    
    def cal_occ_2(self, r_len, prefix_occ, suffix_occ):
        occ_r = set()
        occ_h = set()
        cand_occ = prefix_occ & suffix_occ

        for occ in cand_occ:
            t_begin = self.current_window_data[occ - r_len + 1]
            t_end = self.current_window_data[occ]

            if t_begin == t_end:
                continue

            if t_begin < t_end:
                occ_r.add(occ)
            else:
                occ_h.add(occ)

        # used_occ = occ_r | occ_h
        prefix_occ -= cand_occ
        suffix_occ -= cand_occ
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

    def find_2(self):
        t_size = len(self.current_window_data) - 1
        occ_r = set()
        occ_h = set()

        for i in range(1, t_size):
            if self.current_window_data[i] < self.current_window_data[i + 1]:
                occ_r.add(i + 1)
            elif self.current_window_data[i] > self.current_window_data[i + 1]:
                occ_h.add(i + 1)

        f2 = {}
        sup_r = len(occ_r)
        sup_h = len(occ_h)

        if sup_r >= self.min_sup:
            f2[(1, 2)] = occ_r
            self.Flist.append((1, 2))

        if sup_h >= self.min_sup:
            f2[(2, 1)] = occ_h
            self.Flist.append((2, 1))

        return f2

    def find_m(self, f2):
        prf_sup_dic = {}
        suf_sup_dic = {}
        current_patterns = f2
        self.level_counts = []
        self.prefix_pattern_dict.clear()
        self.suffix_pattern_dict.clear()

        while current_patterns:
            self.level_counts.append(len(current_patterns))

            next_patterns = {}
            next_prefix_pattern_dict = defaultdict(list)
            next_suffix_pattern_dict = {}

            O = {
                key: {
                    occ + 1
                    for occ in values
                    if occ < len(self.current_window_data) - 1
                }
                for key, values in current_patterns.items()
            }
            F=current_patterns.copy()
            

            for p, occs in current_patterns.items():
                prf_sup_dic[p] = len(O[p])
                suf_sup_dic[p] = len(occs)

            for p in F:
                if p in O:
                    self.operation += 1
                    try:
                        if len(p) == 2:
                            matching_qs = list(current_patterns.keys())
                        else:
                            suffix_p = self.suffix_pattern_dict[p]
                            matching_qs = self.prefix_pattern_dict[suffix_p]
                            
                        for q in matching_qs:
                            self.operation += 1
                            if q in current_patterns:
                                candidates_to_check = self.fuse_patterns(p, q)
                                self.fusion_count += len(candidates_to_check)

                                self.candidate_checked_count += len(candidates_to_check)

                    
                                if len(O[p])>= self.min_sup and len(current_patterns[q]) >= self.min_sup:
                                    if p[0] != q[-1]:
                                        self.candidate_generated_count+=1
                                        supp_occ = self.cal_occ_1(O[p], current_patterns[q])
                                        sup_cand = len(supp_occ)


                                        if sup_cand >= self.min_sup:
                                            for cand in candidates_to_check:
                                                next_patterns[cand] = supp_occ
                                                next_prefix_pattern_dict[p].append(cand)
                                                next_suffix_pattern_dict[cand] = q
                                        if len(O[p]) < self.min_sup:
                                            del O[p]

                                        if len(current_patterns[q]) < self.min_sup:
                                            del current_patterns[q]

                                    else:
                                        
                                        occ_r, occ_h=self.cal_occ_2(len(p) + 1, O[p], current_patterns[q])

                                        for cand in candidates_to_check:
                                            if cand[0] < cand[-1]:
                                                self.candidate_generated_count+=1
                                                
                                                sup_r = len(occ_r)
                                                if sup_r >= self.min_sup:
                                                    next_patterns[cand] = occ_r
                                                    next_prefix_pattern_dict[p].append(cand)
                                                    next_suffix_pattern_dict[cand] = q

                                            else:
                                                self.candidate_generated_count+=1
                                                
                                                sup_h = len(occ_h)
                                                if sup_h >= self.min_sup:
                                                    next_patterns[cand] = occ_h
                                                    next_prefix_pattern_dict[p].append(cand)
                                                    next_suffix_pattern_dict[cand] = q
                                        if len(O[p]) < self.min_sup:
                                            del O[p]
                                        if len(current_patterns[q]) < self.min_sup:
                                            del current_patterns[q]

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
