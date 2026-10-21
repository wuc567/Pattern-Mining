import argparse
import os
import heapq
import time
import tracemalloc
import copy
import time
from itertools import chain
from tkinter import END
import re
import datetime
from concurrent.futures import ThreadPoolExecutor

import psutil
from memory_profiler import memory_usage
T = list()
T_size = 0
FOP = list()
PFOP = list()
fFOP = list()
pfFOP = list()
F_FOP=list()
PF_FOP = list()
SUP = list()
# 模式出现字典{(1,2):{2, 4, 6, 7}, (2,1):{....}...}
occ_dic = dict()
focc_dic = dict()
pocc_dic = dict()
pfocc_dic = dict()
# 模式前缀字典,用来记录一个模式的前缀,避免重复计算
prefix_dic = dict()
# 模式后缀字典,同上
suffix_dic = dict()
output_filename = "../IOPP/NEFO_456.txt"
output_dic = ""

cand_cnt = 0
prune_cnt = 0
enum_cnt = 0
enum_failed_cnt = 0
cal_cnt = 0

fusion_time = 0
cal_time = 0

def read_file(file_name):
    global T, T_size
    with open(file_name, 'r') as file:
        T.append(0)  # 确保出现位置与列表下标一致
        for line in file:
            if line.strip() == "":
                continue
            T.extend([float(x) for x in line.split(",") if x])
        T_size = len(T) - 1


class NEFOMiner:
    def __init__(self, file_path, output_dic, minsup):
        self.file_path = file_path
        self.output_dic = output_dic
        self.minsup = minsup
        self.output_filename = output_filename
        self.Fm = list()
        self.Flist = list()
        self.opcount = 0
        self.topk=dict()
        self.score = dict()
        output_file = open(self.output_dic + "/" + self.output_filename, 'w')
        output_file.close()


    def read_file(self, file_name):
        global T, T_size
        with open(file_name, 'r') as file:
            T.append(0)  # 确保出现位置与列表下标一致
            for line in file:
                if line.strip() == "":
                    break
                T.extend([float(x) for x in line.split(" ") if x])
            T_size = len(T) - 1


    def find_2(self):
        global cand_cnt
        self.Fm.append(dict())

        self.Flist.append(set())
        occ_r = set()
        occ_h = set()

        for i in range(1, T_size):
            if T[i] < T[i + 1]:
                occ_r.add(i + 1)
            if T[i] > T[i + 1]:
                occ_h.add(i + 1)

        if len(occ_r) >= self.minsup:
            self.Fm[-1][(1, 2)] = occ_r
            self.Flist[-1].add((1, 2))


        if len(occ_h) >= self.minsup:
            self.Fm[-1][(2, 1)] = occ_h
            self.Flist[-1].add((2, 1))

        with open(self.output_dic + "/" + self.output_filename, 'a') as output_file:
                for pattern in self.Fm[-1]:
                    output_str = f"频繁模式: {pattern} -> 支持度: {len(self.Fm[-1][pattern])}\n"
                    output_file.write(output_str)


    def cal_occ_1(self,cand_occ,  prefix_occ, suffix_occ):
        prefix_occ -= cand_occ
        suffix_occ -= cand_occ
        return cand_occ

    def cal_occ_r(self, r_len,cand_occ,  prefix_occ, suffix_occ):
        #cand_occ = prefix_occ & suffix_occ
        occ_r = set()
        for occ in cand_occ:
            t_begin = T[occ - r_len + 1]
            t_end = T[occ]
            if t_begin == t_end:
                continue
            if t_begin < t_end:
                occ_r.add(occ)
            else:
                continue
        prefix_occ -= occ_r
        suffix_occ -= occ_r


        return occ_r

    def cal_occ_h(self, r_len, cand_occ,  prefix_occ, suffix_occ):
        #cand_occ=prefix_occ &suffix_occ
        occ_h = set()
        for occ in cand_occ:
            t_begin = T[occ - r_len + 1]
            t_end = T[occ]
            if t_begin == t_end:
                continue
            if t_begin < t_end:
                continue
            else:
                occ_h.add(occ)
        prefix_occ -= occ_h
        suffix_occ -= occ_h


        return occ_h


    def find_m(self):
        w=0
        self.opcount += 1
        while self.Flist[-1]:
            new_FOP=dict()
            O={key: {occ+1 for occ in values} for key, values in self.Fm[-1].items()}
            for pattern in self.Flist[-1]:
                if pattern in O:
                    try:
                        p_len=len(pattern)
                        for i in range(1, p_len + 2):
                            self.opcount += 1
                            super_op = list(pattern)
                            super_op.append(i)
                            for j in range(p_len):
                                if super_op[j] >= super_op[-1]:
                                    super_op[j] += 1
                            suffix_sup = super_op[1:]
                            for j in range(p_len):
                                if suffix_sup[j] > super_op[0]:
                                    suffix_sup[j] -= 1
                            suffix_sup = tuple(suffix_sup)
                            self.opcount += 1

                            if suffix_sup in self.Fm[-1]:
                                self.opcount += 1
                                if len(O[pattern])>=self.minsup and len(self.Fm[-1][suffix_sup])>=self.minsup:
                                        cand_occ=O[pattern]&self.Fm[-1][suffix_sup]
                                        if pattern[0] == suffix_sup[-1]:
                                            if super_op[0] < super_op[-1]:
                                                r = tuple(super_op)
                                                w = w + 1
                                                occ_r= self.cal_occ_r(len(super_op),cand_occ, O[pattern], self.Fm[-1][suffix_sup])
                                                if len(O[pattern])<self.minsup:
                                                    del O[pattern]
                                                if len(self.Fm[-1][suffix_sup]) < self.minsup:
                                                    del self.Fm[-1][suffix_sup]
                                                if len(occ_r)>= self.minsup:
                                                    new_FOP[r]=occ_r

                                            if super_op[0] > super_op[-1]:
                                                h = tuple(super_op)
                                                w = w + 1
                                                occ_h= self.cal_occ_h(len(super_op),cand_occ, O[pattern], self.Fm[-1][suffix_sup])
                                                if len(O[pattern])<self.minsup:
                                                    del O[pattern]
                                                if len(self.Fm[-1][suffix_sup]) < self.minsup:
                                                    del self.Fm[-1][suffix_sup]
                                                if len(occ_h)>= self.minsup:
                                                    new_FOP[h]=occ_h

                                        if pattern[0] != suffix_sup[-1]:
                                            w = w + 1
                                            super_occ= self.cal_occ_1(cand_occ, O[pattern], self.Fm[-1][suffix_sup])
                                            if len(O[pattern]) < self.minsup:
                                                del O[pattern]
                                            if len(self.Fm[-1][suffix_sup]) < self.minsup:
                                                del self.Fm[-1][suffix_sup]
                                            if len(super_occ) >= self.minsup:
                                                new_FOP[tuple(super_op)] = super_occ

                    except KeyError:
                        continue

            self.Fm.append(new_FOP)

            self.Flist.append(set())
            for pattern in tuple(self.Fm[-1].keys()):
                self.Flist[-1].add(pattern)
        e=0
        for lists in self.Flist:
            e+=len(lists)
        self.frequent_num = e
        self.candidate_num = w + 2

    def get_memory_usage(self):
        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / (1024 * 1024)  # 转换为MB
        return memory


class SOPPOPS:
    """Run the original SOPP miner independently in every sliding window."""

    def __init__(self, window_size, step_size, min_sup):
        self.window_size = int(window_size)
        self.step_size = int(step_size)
        self.min_sup = int(min_sup)
        self.window_runtimes = []

    # Not used by the benchmark runner; retained for reference only.
    # def read_file(self, file_path):
    #     values = []
    #     with open(file_path, "r", encoding="utf-8") as stream:
    #         for line in stream:
    #             values.extend(
    #                 float(token)
    #                 for token in line.replace(",", " ").split()
    #             )
    #     return values

    def mine_window(self, window):
        global T, T_size
        T = [0] + list(window)
        T_size = len(window)

        miner = NEFOMiner.__new__(NEFOMiner)
        miner.file_path = ""
        miner.output_dic = ""
        miner.minsup = self.min_sup
        miner.output_filename = "dev/null"
        miner.Fm = []
        miner.Flist = []
        miner.opcount = 0
        miner.topk = {}
        miner.score = {}

        start = time.perf_counter()
        miner.find_2()
        miner.find_m()
        runtime = time.perf_counter() - start
        return {
            "frequent": miner.frequent_num,
            "candidates": miner.candidate_num,
            "level_counts": [len(level) for level in miner.Flist],
            "runtime": runtime,
        }

    def run(self, file_path, max_updates=None):
        data = self.read_file(file_path)
        if len(data) < self.window_size:
            raise ValueError("data shorter than window")

        results = []
        left = 0
        while left + self.window_size <= len(data):
            results.append(
                self.mine_window(data[left:left + self.window_size])
            )
            if max_updates is not None and len(results) > max_updates:
                break
            left += self.step_size
        self.window_runtimes = [result["runtime"] for result in results]
        return data, results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SOPP-Miner with OPS sliding windows and no reuse"
    )
    parser.add_argument("dataset")
    parser.add_argument("--window", type=int, required=True)
    parser.add_argument("--step", type=int, required=True)
    parser.add_argument("--minsup", "--min-sup", type=int, required=True)
    parser.add_argument("--updates", type=int, default=None)
    args = parser.parse_args()

    algorithm = SOPPOPS(args.window, args.step, args.minsup)
    data, results = algorithm.run(args.dataset, args.updates)
    last = results[-1]
    print(f"Data length: {len(data)}")
    print(f"Window size: {args.window}")
    print(f"Step size: {args.step}")
    print(f"Minimum support: {args.minsup}")
    print(f"Updates: {len(results) - 1}")
    print(f"Level counts: {last['level_counts']}")
    print(f"Total frequent patterns: {last['frequent']}")
    print(f"Candidate patterns: {last['candidates']}")
    print(f"Total runtime: {sum(algorithm.window_runtimes):.6f} s")
