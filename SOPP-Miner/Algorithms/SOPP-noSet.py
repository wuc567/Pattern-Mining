import os
import time
import tracemalloc
import copy
import time
from itertools import chain
from tkinter import END
import numpy as np
import re
import datetime
from concurrent.futures import ThreadPoolExecutor

import psutil

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
                break
            T.extend([float(x) for x in line.split(" ") if x])
        T_size = len(T) - 1


class NEFOMiner:
    def __init__(self, file_path, output_dic, minsup):
        self.file_path = file_path
        self.output_dic = output_dic
        self.minsup = minsup
        self.output_filename = output_filename
        self.Fm = list()
        self.Flist = list()
        self.SFP=list()
        self.maxsta=0.5
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
    # 挖掘长度为2的频繁模式 find_2()
    # 这个函数查找时间序列中长度为2的模式 (1, 2) 和 (2, 1)。
    # 它遍历序列 T 中的每个相邻元素，检查相邻值的大小关系，并记录其索引。如果这些模式的出现次数达到最小支持度 (min_sup)，则将它们添加到 FOP 集合中。
        global cand_cnt
        self.Fm.append(dict())
        self.Flist.append(set())
        self.SFP.append(set())
        occ_r = set()
        occ_h = set()

        # 计算长度为2的模式出现

        for i in range(1, T_size):
            if T[i] < T[i + 1]:
                occ_r.add(i + 1)
            if T[i] > T[i + 1]:
                occ_h.add(i + 1)

        if len(occ_r) >= self.minsup:
            #print(12344,len(occ_r))
            self.Fm[-1][(1, 2)] = occ_r
            self.Flist[-1].add((1, 2))
            gaprlist = np.diff(list(occ_r))
            gap_std12 = np.std(gaprlist)
            mu = np.mean(gap_std12)
            cv = gap_std12 / mu
            if cv <= self.maxsta:
                self.SFP[-1].add((1, 2))


        if len(occ_h) >= self.minsup:
            #print(124235,len(occ_h))
            self.Fm[-1][(2, 1)] = occ_h
            self.Flist[-1].add((2, 1))
            gaphlist = np.diff(list(occ_h))
            gap_std21 = np.std(gaphlist)
            mu = np.mean(gap_std21)
            cv = gap_std21 / mu
            if cv <= self.maxsta:
                self.SFP[-1].add((2, 1))


        with open(self.output_dic + "/" + self.output_filename, 'a') as output_file:
            for pattern in self.Fm[-1]:
                output_str = f"频繁模式: {pattern} -> 支持度: {len(self.Fm[-1][pattern])}\n"
                output_file.write(output_str)

    def cal_occ_1(self, prefix_occ, suffix_occ):
        prefix_list = sorted(prefix_occ)
        suffix_list = sorted(suffix_occ)
        p, q = copy.deepcopy(prefix_list), copy.deepcopy(suffix_list)
        i, j = 0, 0
        cand_occ = []
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i]+1:
                    cand_occ.append(copy.deepcopy(q[j]))
                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break
        # 一次性更新集合
        cand_occ = set(cand_occ)
        prefix_occ -={occ - 1 for occ in cand_occ}
        suffix_occ -=cand_occ
        return cand_occ

    def cal_occ_r(self, r_len, prefix_occ, suffix_occ):
        occ_r = []

        # 将集合转换为有序列表
        prefix_list = sorted(prefix_occ)
        suffix_list = sorted(suffix_occ)
        p, q = copy.deepcopy(prefix_list), copy.deepcopy(suffix_list)
        i, j = 0, 0
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i]+1:
                    first = q[j]
                    fri = first - (r_len-1)
                    if T[first] > T[fri]:
                        occ_r.append(copy.deepcopy(q[j]))
                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break
        occ_r = set(occ_r)
        # 一次性更新集合
        prefix_occ -= {occ - 1 for occ in occ_r}
        suffix_occ -= occ_r
        return occ_r

    def cal_occ_h(self, r_len, prefix_occ, suffix_occ):
        occ_h = []
        # 将集合转换为有序列表
        prefix_list = sorted(prefix_occ)
        suffix_list = sorted(suffix_occ)
        p, q = copy.deepcopy(prefix_list), copy.deepcopy(suffix_list)
        i, j = 0, 0
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i]+1:
                    first = q[j]
                    fri = first - (r_len-1)
                    if T[first] < T[fri]:
                        occ_h.append(copy.deepcopy(q[j]))

                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break

        occ_h = set(occ_h)

        # 一次性更新集合
        prefix_occ -= {occ - 1 for occ in occ_h}
        suffix_occ -= occ_h
        return occ_h



    def find_m(self):
        a=0

        while self.Flist[-1]:
            new_FOP=dict()
            O=copy.deepcopy(self.Fm[-1])

            for pattern in self.Flist[-1]:
                if pattern in O:
                    try:
                        p_len=len(pattern)
                        for i in range(1, p_len + 2):
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

                            if suffix_sup in self.Fm[-1]:
                                if len(O[pattern])>=self.minsup and len(self.Fm[-1][suffix_sup])>=self.minsup:

                                    #如何在这里设置一个条件使得当此处出现keyError时跳出这个pattern，继续遍历下一个pattern in O

                                    if pattern[0] == suffix_sup[-1]:
                                        if super_op[0] < super_op[-1]:
                                            r = tuple(super_op)
                                            a = a + 1
                                            #print(123)
                                            #print(len(O[pattern]),len(self.Fm[-1][suffix_sup]))
                                            occ_r = self.cal_occ_r(len(super_op),O[pattern], self.Fm[-1][suffix_sup])
                                            #print(len(O[pattern]),len(self.Fm[-1][suffix_sup]))
                                            #print(456)
                                            if len(O[pattern])<self.minsup:
                                                del O[pattern]
                                            if len(self.Fm[-1][suffix_sup]) < self.minsup:
                                                del self.Fm[-1][suffix_sup]
                                            if len(occ_r)>= self.minsup:
                                                new_FOP[r]=occ_r
                                                canddlist = sorted(occ_r)
                                                gaps = np.diff(canddlist)
                                                mu = np.mean(gaps)
                                                gap_std = np.std(gaps)
                                                cv = gap_std / mu
                                                if cv <= self.maxsta:
                                                    self.SFP[-1].add(r)
                                        if super_op[0] > super_op[-1]:
                                            h = tuple(super_op)
                                            a = a + 1

                                            occ_h = self.cal_occ_h(len(super_op),O[pattern], self.Fm[-1][suffix_sup])

                                            if len(O[pattern])<self.minsup:
                                                del O[pattern]
                                            if len(self.Fm[-1][suffix_sup]) < self.minsup:
                                                del self.Fm[-1][suffix_sup]
                                            if len(occ_h)>= self.minsup:
                                                new_FOP[h]=occ_h
                                                canddlist = sorted(occ_h)
                                                gaps = np.diff(canddlist)
                                                mu = np.mean(gaps)
                                                gap_std = np.std(gaps)
                                                cv = gap_std / mu
                                                if cv <= self.maxsta:
                                                    self.SFP[-1].add(h)

                                    if pattern[0] != suffix_sup[-1]:
                                        a = a + 1
                                        super_occ = self.cal_occ_1(O[pattern], self.Fm[-1][suffix_sup])
                                        if len(O[pattern]) < self.minsup:
                                            del O[pattern]
                                        if len(self.Fm[-1][suffix_sup]) < self.minsup:
                                            del self.Fm[-1][suffix_sup]
                                        if len(super_occ) >= self.minsup:
                                            new_FOP[tuple(super_op)] = super_occ
                                            canddlist = sorted(super_occ)
                                            gaps = np.diff(canddlist)
                                            mu = np.mean(gaps)
                                            gap_std = np.std(gaps)
                                            cv = gap_std / mu
                                            if cv <= self.maxsta:
                                                self.SFP[-1].add(tuple(super_op))
                    except KeyError:
                        continue

            self.Fm.append(new_FOP)
            self.Flist.append(set())
            for pattern in tuple(self.Fm[-1].keys()):
                self.Flist[-1].add(pattern)
        e=0
        for lists in self.Flist:
            e+=len(lists)
        print("频繁模式",e)
        print("候选模式",a+2)


    def get_memory_usage(self):
        """获取当前进程的内存使用量（单位：MB）"""
        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / (1024 * 1024)  # 转换为MB
        return memory

    def FOP_miner(self):
        memeory_before = self.get_memory_usage()
        starttime=time.time()
        self.find_2()
        self.find_m()
        endtime = time.time()
        memeory_after = self.get_memory_usage()
        print("NEFO-noSet")
        print("内存",memeory_after-memeory_before)
        print("时间",endtime-starttime)
        print("SOPP", len(self.SFP[-1]))

from memory_profiler import memory_usage
def main():

    #file_path="/Users/zyj/Desktop/NEFOMiner/AAPL.txt"
    #     ,"/Users/zyj/Desktop/NEFOMiner/GOOG.txt",
    #           "/Users/zyj/Desktop/NEFOMiner/KO.txt","/Users/zyj/Desktop/NEFOMiner/XOM2.txt",
    #           "/Users/zyj/Desktop/NEFOMiner/beijing_PM2.5.txt","/Users/zyj/Desktop/NEFOMiner/beijing_O3.txt",
    #           "/Users/zyj/Desktop/NEFOMiner/shanghai.txt","/Users/zyj/Desktop/NEFOMiner/mel_temperature.txt"]
    # for file_path in filelist:
    #     print(file_path)

    #starttime = time.time()
    #file_path = "/Users/zyj/Desktop/NEFOMiner/GOOG.txt"
    #file_path = '/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_1000KB.txt'
    file_path = ("/Users/zyj/PycharmProjects/incremental"
                 "/实验/最终对比试验文件/新的对比实验/SDB3_2000KB.txt")
    read_file(file_path)
    output_dic = "/Users/zyj/PycharmProjects/incremental/IOPP"

    minsup = 50
        #10Kb 3
        #50Kb 10
        #100Kb 18
        #200Kb 60
        #250Kb 70
        #500Kb 145
        #750Kb 225
        #1000Kb 290


    miner = NEFOMiner(file_path = file_path, output_dic = output_dic, minsup = minsup)
    a = memory_usage(miner.FOP_miner)
    print(max(a) - min(a))
    print('\n')


if __name__ == '__main__':
    main()


