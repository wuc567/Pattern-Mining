"""OPS-ISC: OPS-SPF with SOPP occurrence-intersection support."""

import argparse
import copy
import re

import numpy as np


# The benchmark runner replaces this name with an in-memory float64 array.
# The original standalone text reader is retained only for reference.
# def read_file(file_path):
#     file = open(file_path, "r")
#     all_lines = file.readlines()
#     dataset = []
#     for i in range(len(all_lines)):
#         if not all_lines[i].isspace():
#             for x in re.split(r"[\s,]+", all_lines[i].strip()):
#                 if x:
#                     dataset.append(float(x))
#     return dataset


def sort(src):
    src = np.array(src)
    src = src.argsort()
    src = src.argsort() + 1
    return src.tolist()


class OPSISC:
    def __init__(self, file_path, window_size, step_size, min_sup):
        self.data = read_file(file_path)
        self.window_size = int(window_size)
        self.step_size = int(step_size)
        self.minsup = int(min_sup)
        self.left = 0
        self.right = self.window_size - 1
        self.S = []

        self.Z = set()
        self.Z2 = set()
        self.Cd = []
        self.Cd2 = []
        self.Fm = {}
        self.O2 = {(1, 2): set(), (2, 1): set()}

        self.frequent_num = 0
        self.candidate_num = 0
        self.valid_pair_num = 0
        self.window_results = []
        self.fusion_cache = {}
        self.fusion_cache_hits = 0
        self.fusion_cache_misses = 0

    def cached_pattern_fusion(self, p, q, relation):
        key = (tuple(p), tuple(q), int(relation))
        if key in self.fusion_cache:
            self.fusion_cache_hits += 1
            return self.fusion_cache[key]

        p1 = p[0]
        qm = q[-1]
        if p1 < qm:
            candidate = [p1]
            candidate.extend(q)
            for i in range(1, len(candidate)):
                if candidate[i] >= candidate[0]:
                    candidate[i] += 1
        elif p1 > qm:
            candidate = [p1 + 1]
            candidate.extend(q)
            for i in range(1, len(candidate)):
                if candidate[i] >= candidate[0]:
                    candidate[i] += 1
        else:
            middle = [value if value < p1 else value + 1 for value in p[1:]]
            if relation == 1:
                candidate = [p1] + middle + [p1 + 1]
            elif relation == 2:
                candidate = [p1 + 1] + middle + [p1]
            else:
                candidate = None

        result = tuple(candidate) if candidate is not None else None
        self.fusion_cache[key] = result
        self.fusion_cache_misses += 1
        return result

    def cal_occ_1(self, cand_occ, prefix_occ, suffix_occ):
        prefix_occ -= cand_occ
        suffix_occ -= cand_occ
        return cand_occ

    def cal_occ_r(self, r_len, cand_occ, prefix_occ, suffix_occ):
        occ_r = set()
        for occ in cand_occ:
            t_begin = self.S[occ - r_len + 1]
            t_end = self.S[occ]
            if t_begin == t_end:
                continue
            if t_begin < t_end:
                occ_r.add(occ)
            else:
                continue
        prefix_occ -= occ_r
        suffix_occ -= occ_r
        return occ_r

    def cal_occ_h(self, r_len, cand_occ, prefix_occ, suffix_occ):
        occ_h = set()
        for occ in cand_occ:
            t_begin = self.S[occ - r_len + 1]
            t_end = self.S[occ]
            if t_begin == t_end:
                continue
            if t_begin < t_end:
                continue
            else:
                occ_h.add(occ)
        prefix_occ -= occ_h
        suffix_occ -= occ_h
        return occ_h

    def find(self, first_window):
        self.S = self.data[self.left:self.right + 1]
        self.Fm.clear()
        self.Z.clear()
        self.Z2.clear()

        if first_window:
            for i in range(len(self.S) - 1):
                if self.S[i] < self.S[i + 1]:
                    self.Z.add(i + 1)
                if self.S[i] > self.S[i + 1]:
                    self.Z2.add(i + 1)
        else:
            self.Z.update(
                occ - self.step_size
                for occ in self.O2[(1, 2)]
                if occ >= self.step_size + 1
            )
            self.Z2.update(
                occ - self.step_size
                for occ in self.O2[(2, 1)]
                if occ >= self.step_size + 1
            )

            start = max(1, self.window_size - self.step_size)
            for endpoint in range(start, len(self.S)):
                if self.S[endpoint - 1] < self.S[endpoint]:
                    self.Z.add(endpoint)
                if self.S[endpoint - 1] > self.S[endpoint]:
                    self.Z2.add(endpoint)

        self.O2[(1, 2)] = set(self.Z)
        self.O2[(2, 1)] = set(self.Z2)
        self.candidate_num = 2
        self.valid_pair_num = 2
        if len(self.Z) >= self.minsup:
            self.Fm[(1, 2)] = set(self.Z)
        if len(self.Z2) >= self.minsup:
            self.Fm[(2, 1)] = set(self.Z2)

    def generate_fre(self):
        slen = len(next(iter(self.Fm)))
        patterns = list(self.Fm)
        O = {
            pattern: {occ + 1 for occ in values}
            for pattern, values in self.Fm.items()
        }
        F = {
            pattern: set(values)
            for pattern, values in self.Fm.items()
        }
        new_FOP = {}

        self.Cd = [0] * (slen + 1)
        self.Cd2 = [0] * (slen + 1)

        for pattern in patterns:
            Q = copy.deepcopy(pattern)
            Q = Q[1:]
            q = sort(Q)

            for suffix_pattern in patterns:
                if (
                    len(O[pattern]) >= self.minsup
                    and len(F[suffix_pattern]) >= self.minsup
                ):
                    R = list(copy.deepcopy(suffix_pattern))
                    R.pop()
                    r = sort(R)
                    if q == r:
                        cand_occ = O[pattern] & F[suffix_pattern]

                        if pattern[0] == suffix_pattern[slen - 1]:
                            self.valid_pair_num = self.valid_pair_num + 2
                            occ_r = self.cal_occ_r(
                                slen + 1,
                                cand_occ,
                                O[pattern],
                                F[suffix_pattern],
                            )
                            occ_h = self.cal_occ_h(
                                slen + 1,
                                cand_occ,
                                O[pattern],
                                F[suffix_pattern],
                            )

                            if len(occ_r) >= self.minsup:
                                candidate = self.cached_pattern_fusion(
                                    pattern, suffix_pattern, 1
                                )
                                self.candidate_num = self.candidate_num + 1
                                new_FOP[candidate] = occ_r

                            if len(occ_h) >= self.minsup:
                                candidate = self.cached_pattern_fusion(
                                    pattern, suffix_pattern, 2
                                )
                                self.candidate_num = self.candidate_num + 1
                                new_FOP[candidate] = occ_h

                        elif pattern[0] < suffix_pattern[slen - 1]:
                            self.valid_pair_num = self.valid_pair_num + 1
                            super_occ = self.cal_occ_1(
                                cand_occ,
                                O[pattern],
                                F[suffix_pattern],
                            )
                            if len(super_occ) >= self.minsup:
                                candidate = self.cached_pattern_fusion(
                                    pattern, suffix_pattern, 0
                                )
                                self.candidate_num = self.candidate_num + 1
                                new_FOP[candidate] = super_occ

                        else:
                            self.valid_pair_num = self.valid_pair_num + 1
                            super_occ = self.cal_occ_1(
                                cand_occ,
                                O[pattern],
                                F[suffix_pattern],
                            )
                            if len(super_occ) >= self.minsup:
                                candidate = self.cached_pattern_fusion(
                                    pattern, suffix_pattern, 0
                                )
                                self.candidate_num = self.candidate_num + 1
                                new_FOP[candidate] = super_occ

        return new_FOP

    def solve_window(self, first_window):
        hits_before = self.fusion_cache_hits
        misses_before = self.fusion_cache_misses
        self.find(first_window)
        self.frequent_num = len(self.Fm)
        while self.Fm:
            new_FOP = self.generate_fre()
            if not new_FOP:
                break
            self.frequent_num += len(new_FOP)
            self.Fm = new_FOP
        result = {
            "frequent_patterns": self.frequent_num,
            "candidate_patterns": self.candidate_num,
            "generated_candidate_patterns": 2 + self.fusion_cache_misses - misses_before,
            "fusion_cache_hits": self.fusion_cache_hits - hits_before,
            "fusion_cache_misses": self.fusion_cache_misses - misses_before,
            "valid_pattern_pairs": self.valid_pair_num,
        }
        self.window_results.append(result)
        return result

    def slide(self):
        if self.right + self.step_size >= len(self.data):
            return None
        self.left = self.left + self.step_size
        self.right = self.right + self.step_size
        return self.solve_window(False)

    def run(self, window_count=1):
        result = self.solve_window(True)
        for _ in range(1, window_count):
            result = self.slide()
            if result is None:
                break
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument("--window", type=int, required=True)
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--minsup", type=int, required=True)
    parser.add_argument("--windows", type=int, default=1)
    args = parser.parse_args()

    algorithm = OPSISC(
        args.dataset,
        args.window,
        args.step,
        args.minsup,
    )
    result = algorithm.run(args.windows)
    print(f"Data length: {len(algorithm.data)}")
    print(f"Window size: {args.window}")
    print(f"Step size: {args.step}")
    print(f"Minimum support: {args.minsup}")
    print(f"Windows: {len(algorithm.window_results)}")
    print(f"Frequent patterns: {result['frequent_patterns']}")
    print(f"Candidate patterns: {result['candidate_patterns']}")
    print(f"Valid pattern pairs: {result['valid_pattern_pairs']}")
