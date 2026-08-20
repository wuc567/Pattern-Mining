import copy
import argparse
import os
import time
from tkinter import END
import numpy as np
import re

import psutil


def read_file(file_path):
    """
    :param file_path: 文件位置
    :return: 文件内容列表
    """
    file = open(file_path, 'r')
    all_lines = file.readlines()
    dataset = []
    for i in range(len(all_lines)):
        if not all_lines[i].isspace():
            for x in re.split(',', all_lines[i]):
                dataset.append(float(x))
    return dataset


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


def sort(src):
    src = np.array(src)
    src = src.argsort()
    src = src.argsort() + 1
    return src.tolist()


class OPRMiner:
    """
    OPR算法
    """
    rule_num = 0  # 规则数量
    rule_left = []  # 规则前件
    rule_right = []  # 规则后件
    rule_leftnum = 0  # 规则前件支持度
    rule_rightnum = 0  # 规则后件支持度
    frequent_num = 0  # 总的频繁模式数量
    cd_num = 2  # 候选模式数量
    allrulenum = 0
    Z = []  # 存放本次生成的末尾数组
    Z2 = []
    Cd = []  # 存放本次生成的模式
    Cd2 = []
    L = []  # 存放每次生成的频繁模式
    S = []  # 存放序列
    P = []  # 存放末位的数组

    fre_num = 0

    output_filepath = ""
    output_filename = "OPR-Miner-Output.txt"
    minconf = 0.4
    minsup = 12

    def __init__(self, file_path='', output_filepath='',
                 min_conf=0.4, min_sup=12, window_len=None, step=None):
        """
        :param file_path: 输入文件位置
        :param output_filepath: 输出文件夹位置
        :param min_conf: 最小置信度
        :param min_sup: 最小支持度
        """
        self.S = read_numeric_series(file_path) if file_path else []
        self.output_filepath = output_filepath
        self.minconf = min_conf
        self.minsup = min_sup
        self.window_len = window_len
        self.step = window_len if step is None else step
        self.window_level_results = []
        self.window_stats = []
        self.current_window_data = []
        self.level_counts = []
        self.candidate_num=0
        self.operation = 0
        self.reset_window_state()
        if self.output_filepath:
            output_file = open(self.output_filepath + "/" + self.output_filename, 'w')
            output_file.close()

    def reset_window_state(self):
        self.rule_num = 0
        self.rule_left = []
        self.rule_right = []
        self.rule_leftnum = 0
        self.rule_rightnum = 0
        self.frequent_num = 0
        self.cd_num = 2
        self.allrulenum = 0
        self.Z = []
        self.Z2 = []
        self.Cd = []
        self.Cd2 = []
        self.L = []
        self.P = []
        self.fre_num = 0
        self.a = 0
        self.topk = dict()
        self.level_counts = []
        self.runtime = 0.0

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
        self.judge_fre(len(self.Z), self.Cd, self.Z)

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
        #print(self.Cd2, len(self.Z2))
        self.judge_fre(len(self.Z), self.Cd, self.Z)
        self.judge_fre(len(self.Z2), self.Cd2, self.Z2)

    # 模式融合
    def generate_fre(self):
        Lb = []
        slen = len(self.L[0])  # 模式长度


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
            self.operation += 1
            Q = copy.deepcopy(fre[i])  # 求后缀
            Q = Q[1:]
            q = sort(Q)
            L = []
            size = len(pos[i])

            self.rule_left = fre[i]
            self.rule_leftnum = size
            L.append(size)
            for k in range(size):
                L.append(copy.deepcopy(pos[i][k]))

            for j in range(fre_number):
                self.operation += 1
                #print(fre[i], L[0],fre[j],Lb[j][0])
                if L[0] >= self.minsup and Lb[j][0] >= self.minsup:
                    R = copy.deepcopy(fre[j])
                    R.pop()  # 求前缀
                    r = sort(R)
                    if q == r:
                        if fre[i][0] == fre[j][slen - 1]: 
                            self.candidate_num+=2 # 最前最后位置相等，拼接成两个模式
                            self.Cd[0] = fre[i][0]
                            self.Cd2[0] = fre[i][0] + 1
                            self.Cd[slen] = fre[i][0] + 1
                            self.Cd2[slen] = fre[i][0]
                            for t in range(1, slen):
                                if fre[i][t] > fre[j][slen - 1]:  # 中间位置增长
                                    self.Cd[t] = fre[i][t] + 1
                                    self.Cd2[t] = fre[i][t] + 1
                                else:
                                    self.Cd[t] = fre[i][t]
                                    self.Cd2[t] = fre[i][t]
                            self.cd_num = self.cd_num + 2
                            self.a = self.a + 2
                            # print(123)
                            # print(L)
                            # print(len(L))
                            # print(456)
                            # print(len(Lb),len(Lb[0]))
                            self.grow_BaseP2(len(self.Cd) - 1, Lb[j], L)

                            # print(len(Lb[j]), len(L))
                            # print(456)

                        elif fre[i][0] < fre[j][slen - 1]:  # 第一个位置比最后一个位置小
                            self.candidate_num+=1
                            self.Cd[0] = fre[i][0]  # 小的不变
                            self.Cd[slen] = fre[j][slen - 1] + 1  # 大的加一
                            for t in range(1, slen):
                                if fre[i][t] > fre[j][slen - 1]:
                                    self.Cd[t] = fre[i][t] + 1  # 中间位置增长
                                else:
                                    self.Cd[t] = fre[i][t]
                            self.cd_num = self.cd_num + 1
                            self.a = self.a + 1
                            self.grow_BaseP1(Lb[j], L)
                        else:
                            self.candidate_num+=1
                            self.Cd[0] = fre[i][0] + 1  # 大的加一
                            self.a=self.a+1
                            self.Cd[slen] = fre[j][slen - 1]  # 小的不变
                            for t in range(slen - 1):
                                if fre[j][t] > fre[i][0]:
                                    self.Cd[t + 1] = fre[j][t] + 1  # 中间位置增长
                                else:
                                    self.Cd[t + 1] = fre[j][t]
                            self.cd_num = self.cd_num + 1
                            self.grow_BaseP1(Lb[j], L)
        Lb.clear()
        pos.clear()
        fre.clear()


    def judge_fre(self, sup_num, Cd, Z):  #频繁模式挖掘
        if sup_num >= self.minsup:
            self.P.append(copy.deepcopy(Z))
            self.L.append(copy.deepcopy(Cd))

            if self.output_filepath:
                output_file = open(self.output_filepath + "/" + self.output_filename, 'a')
                strArr = "频繁模式："
                for i in Cd:
                    strArr = strArr + str(i) + ","
                strArr = strArr + " 支持度为：" + str(sup_num)
                output_file.write(strArr + "\n")
                output_file.close()
            cand = tuple(Cd)
            self.topk[cand] = sup_num
            self.rule_right = Cd
            self.rule_rightnum = sup_num
            #self.recommend(self.rule_leftnum, self.rule_rightnum, self.rule_left, self.rule_right)

            self.allrulenum = self.allrulenum + 1

            self.frequent_num = self.frequent_num + 1
            self.fre_num = self.fre_num + 1


    def judge_fre2(self, sup_num, Cd, Z):
        if sup_num >= self.minsup:
            self.P.append(copy.deepcopy(Z))
            self.L.append(copy.deepcopy(Cd))

            if self.output_filepath:
                output_file = open(self.output_filepath + "/" + self.output_filename, 'a')
                strArr = "频繁模式："
                for i in Cd:
                    strArr = strArr + str(i) + ","
                strArr = strArr + " 支持度为：" + str(sup_num)
                output_file.write(strArr + "\n")
                output_file.close()
            cand = tuple(Cd)
            self.topk[cand] = sup_num
            self.frequent_num = self.frequent_num + 1
            self.fre_num = self.fre_num + 1


    def find(self):
        self.candidate_num += 2
        i, j = 0, 1
        self.Cd.append(1)
        self.Cd.append(2)
        self.Cd2.append(2)
        self.Cd2.append(1)
        while j < len(self.S):
            if self.S[j] > self.S[i]:
                self.Z.append(j)
            elif self.S[j] != self.S[i]:
                self.Z2.append(j)
            i = i + 1
            j = j + 1
        #print(len(self.Z))
        self.judge_fre2(len(self.Z), self.Cd, self.Z)
        self.Cd.clear()
        # print(len(self.Z2))
        self.judge_fre2(len(self.Z2), self.Cd2, self.Z2)
        self.Cd2.clear()
        #print(topk)
        #print(sorted(topk.items(), key=lambda x: x[1], reverse=True)[:12])


    def get_memory_usage(self):
        """获取当前进程的内存使用量（单位：MB）"""
        process = psutil.Process(os.getpid())
        memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        return memory_usage_mb

    def solve(self):

        memory_before = self.get_memory_usage()
        begin_time = time.time()

        self.find()
        while self.fre_num:
            self.level_counts.append(self.fre_num)
            self.generate_fre()
        #print(self.topk)
        #print(sorted(self.topk.items(), key=lambda x: x[1], reverse=True)[:12])

        end_time = time.time()
        memory_after = self.get_memory_usage()
        print("时间",end_time-begin_time)
        print("内存",memory_after-memory_before)
        print("频繁", self.frequent_num)
        print("候选", self.candidate_num)

    def mine_window(self, window_data, window_id=1):
        self.reset_window_state()
        begin_time = time.perf_counter()
        self.S = window_data
        self.current_window_data = window_data

        self.find()
        while self.fre_num:
            self.level_counts.append(self.fre_num)
            self.generate_fre()

        self.runtime = time.perf_counter() - begin_time
        self.window_level_results.append(self.level_counts.copy())
        stats = self.stats_dict()
        stats["window_id"] = window_id
        stats["level_counts"] = self.level_counts.copy()
        self.window_stats.append(stats)

    def run(self, data, dates=None):
        self.window_level_results.clear()
        self.window_stats.clear()
        self.candidate_num = 0
        self.operation = 0

        if self.window_len is None:
            self.window_len = len(data)
        if self.step is None:
            self.step = self.window_len

        for i, (window_data, _start_idx) in enumerate(self.get_windows(data)):
            self.mine_window(window_data, window_id=i + 1)

        return self.window_level_results

    def get_windows(self, data):
        n = len(data)
        for i in range(0, n - self.window_len + 1, self.step):
            yield data[i : i + self.window_len], i

    def stats_dict(self):
        return {
            "candidate_generated_count": self.candidate_num,
            "candidate_checked_count": self.candidate_num,
            "fusion_count": self.a,
            "total_frequent_count": self.frequent_num,
            "runtime": self.runtime,
            "operation": self.operation,
        }



def main():
    parser = argparse.ArgumentParser(description="EFO miner with WOPP window")
    parser.add_argument("dataset", nargs="?", default="AAPL.txt")
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
    miner = OPRMiner(
        min_sup=args.min_sup,
        window_len=window_len,
        step=step,
    )
    miner.run(data)
    total_time = time.perf_counter() - start

    print(f"Execution time: {total_time:.6f} seconds")
    print(f"Window count: {len(miner.window_level_results)}")
    if miner.window_level_results:
        print(f"Last window level counts: {miner.window_level_results[-1]}")
    if miner.window_stats:
        print(f"Last window stats: {miner.window_stats[-1]}")


if __name__ == '__main__':
    main()

