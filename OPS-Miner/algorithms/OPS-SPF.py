"""OPS-SPF: EFO-Miner with sliding-window occurrence reuse and SPF."""

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


class OPSSPF:
    def __init__(self, file_path, window_size, step_size, min_sup):
        self.data = read_file(file_path)
        self.window_size = int(window_size)
        self.step_size = int(step_size)
        self.minsup = int(min_sup)
        self.left = 0
        self.right = self.window_size - 1
        self.S = []

        self.Z = []
        self.Z2 = []
        self.Cd = []
        self.Cd2 = []
        self.L = []
        self.P = []
        self.O = {(1, 2): [], (2, 1): []}

        self.fre_num = 0
        self.frequent_num = 0
        self.candidate_num = 0
        self.valid_pair_num = 0
        self.window_results = []
        self.fusion_cache = {}
        self.fusion_cache_hits = 0
        self.fusion_cache_misses = 0

    def cached_pattern_fusion(self, p, q, relation):
        """Return an immutable fused pattern, reusing it across windows."""
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

    def grow_BaseP1(self, Ld, L):
        p, q = copy.deepcopy(L), copy.deepcopy(Ld)
        i, j = 1, 1
        self.Z.clear()
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i] + 1:
                    self.Z.append(copy.deepcopy(q[j]))
                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break
        L[0] = L[0] - len(self.Z)
        Ld[0] = Ld[0] - len(self.Z)
        return copy.deepcopy(self.Z)

    def grow_BaseP2(self, slen, Ld, L):
        first, fri, i, j = 0, 0, 1, 1
        p, q = copy.deepcopy(L), copy.deepcopy(Ld)
        self.Z.clear()
        self.Z2.clear()
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i] + 1:
                    first = q[j]
                    fri = first - slen
                    if self.S[first] > self.S[fri]:
                        self.Z.append(copy.deepcopy(q[j]))
                    elif self.S[first] != self.S[fri]:
                        self.Z2.append(copy.deepcopy(q[j]))
                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break
        L[0] = L[0] - len(self.Z) - len(self.Z2)
        Ld[0] = Ld[0] - len(self.Z) - len(self.Z2)
        return copy.deepcopy(self.Z), copy.deepcopy(self.Z2)

    def judge_fre(self, sup_num, Cd, Z):
        if sup_num >= self.minsup:
            self.P.append(copy.deepcopy(Z))
            self.L.append(copy.deepcopy(Cd))
            self.frequent_num = self.frequent_num + 1
            self.fre_num = self.fre_num + 1

    def judge_fre2(self, sup_num, Cd, Z):
        if sup_num >= self.minsup:
            self.P.append(copy.deepcopy(Z))
            self.L.append(copy.deepcopy(Cd))
            self.frequent_num = self.frequent_num + 1
            self.fre_num = self.fre_num + 1

    def find(self, first_window):
        self.S = self.data[self.left:self.right + 1]
        self.L.clear()
        self.P.clear()
        self.Cd.clear()
        self.Cd2.clear()
        self.Z.clear()
        self.Z2.clear()
        self.fre_num = 0

        self.Cd.append(1)
        self.Cd.append(2)
        self.Cd2.append(2)
        self.Cd2.append(1)

        if first_window:
            i, j = 0, 1
            while j < len(self.S):
                if self.S[j] > self.S[i]:
                    self.Z.append(j)
                elif self.S[j] != self.S[i]:
                    self.Z2.append(j)
                i = i + 1
                j = j + 1
        else:
            self.Z.extend(
                occ - self.step_size
                for occ in self.O[(1, 2)]
                if occ >= self.step_size + 1
            )
            self.Z2.extend(
                occ - self.step_size
                for occ in self.O[(2, 1)]
                if occ >= self.step_size + 1
            )

            j = max(1, self.window_size - self.step_size)
            i = j - 1
            while j < len(self.S):
                if self.S[j] > self.S[i]:
                    self.Z.append(j)
                elif self.S[j] != self.S[i]:
                    self.Z2.append(j)
                i = i + 1
                j = j + 1

        self.O[(1, 2)] = copy.deepcopy(self.Z)
        self.O[(2, 1)] = copy.deepcopy(self.Z2)
        self.candidate_num = 2
        self.valid_pair_num = 2
        self.judge_fre2(len(self.Z), self.Cd, self.Z)
        self.Cd.clear()
        self.judge_fre2(len(self.Z2), self.Cd2, self.Z2)
        self.Cd2.clear()

    def generate_fre(self):
        Lb = []
        slen = len(self.L[0])

        fre = copy.deepcopy(self.L)
        self.L.clear()
        fre_number = copy.deepcopy(self.fre_num)
        self.fre_num = 0

        pos = copy.deepcopy(self.P)
        self.P.clear()

        for x in range(fre_number):
            Lb.append([])

        self.Cd.clear()
        self.Cd2.clear()
        for y in range(slen + 1):
            self.Cd.append(0)
            self.Cd2.append(0)

        for s in range(fre_number):
            Lb[s].append(len(pos[s]))
            for d in range(len(pos[s])):
                Lb[s].append(copy.deepcopy(pos[s][d]))

        for i in range(fre_number):
            Q = copy.deepcopy(fre[i])
            Q = Q[1:]
            q = sort(Q)
            L = []
            size = len(pos[i])
            L.append(size)
            for k in range(size):
                L.append(copy.deepcopy(pos[i][k]))

            for j in range(fre_number):
                if L[0] >= self.minsup and Lb[j][0] >= self.minsup:
                    R = list(fre[j])
                    R.pop()
                    r = sort(R)
                    if q == r:
                        if fre[i][0] == fre[j][slen - 1]:
                            self.valid_pair_num = self.valid_pair_num + 2
                            Z, Z2 = self.grow_BaseP2(slen, Lb[j], L)

                            if len(Z) >= self.minsup:
                                candidate = self.cached_pattern_fusion(
                                    fre[i], fre[j], 1
                                )
                                self.candidate_num = self.candidate_num + 1
                                self.judge_fre(len(Z), candidate, Z)

                            if len(Z2) >= self.minsup:
                                candidate = self.cached_pattern_fusion(
                                    fre[i], fre[j], 2
                                )
                                self.candidate_num = self.candidate_num + 1
                                self.judge_fre(len(Z2), candidate, Z2)

                        elif fre[i][0] < fre[j][slen - 1]:
                            self.valid_pair_num = self.valid_pair_num + 1
                            Z = self.grow_BaseP1(Lb[j], L)
                            if len(Z) >= self.minsup:
                                candidate = self.cached_pattern_fusion(
                                    fre[i], fre[j], 0
                                )
                                self.candidate_num = self.candidate_num + 1
                                self.judge_fre(len(Z), candidate, Z)

                        else:
                            self.valid_pair_num = self.valid_pair_num + 1
                            Z = self.grow_BaseP1(Lb[j], L)
                            if len(Z) >= self.minsup:
                                candidate = self.cached_pattern_fusion(
                                    fre[i], fre[j], 0
                                )
                                self.candidate_num = self.candidate_num + 1
                                self.judge_fre(len(Z), candidate, Z)

        Lb.clear()
        pos.clear()
        fre.clear()

    def solve_window(self, first_window):
        hits_before = self.fusion_cache_hits
        misses_before = self.fusion_cache_misses
        self.frequent_num = 0
        self.find(first_window)
        while self.fre_num:
            self.generate_fre()
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
        for k in range(1, window_count):
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

    algorithm = OPSSPF(
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
