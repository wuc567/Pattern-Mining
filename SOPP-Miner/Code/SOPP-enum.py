import os
import time
import tracemalloc
import copy
import time
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
        self.L = list()
        self.P = list()
        self.Fm = list()
        self.Lc = list()
        self.Flist = list()
        self.sta=0.5
        self.SFP=list()
        output_file = open(self.output_dic + "/" + self.output_filename, 'w')
        output_file.close()
        self.opcount=0


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
        self.L.append(list())
        self.P.append(list())
        self.Fm.append(dict())
        self.SFP.append(set())
        occ_r = set()
        occ_h = set()

        for i in range(1, T_size):
            if T[i] < T[i + 1]:
                occ_r.add(i + 1)
            if T[i] > T[i + 1]:
                occ_h.add(i + 1)

        if len(occ_r) >= self.minsup:
            self.L[-1].append([1, 2])
            self.Fm[-1][(1, 2)]=occ_r
            gaprlist = np.diff(list(occ_r))
            gap_std12 = np.std(gaprlist)
            mu = np.mean(gap_std12)
            cv = gap_std12 / mu
            if cv <= self.sta:
                self.SFP[-1].add((1, 2))

        if len(occ_h) >= self.minsup:
            self.L[-1].append([2, 1])
            self.Fm[-1][(2, 1)]=occ_h
            gaphlist = np.diff(list(occ_h))
            gap_std21 = np.std(gaphlist)
            mu = np.mean(gap_std21)
            cv = gap_std21 / mu
            if cv <= self.sta:
                self.SFP[-1].add((2, 1))

    def sort(self, src):
        src = np.array(src)
        src = src.argsort()
        src = src.argsort() + 1
        return src.tolist()

    def cal_occ_1(self, prefix_occ, suffix_occ):
        cand_occ = prefix_occ & suffix_occ
        prefix_occ -=cand_occ
        suffix_occ-=cand_occ
        return cand_occ


    def cal_occ_r(self, r_len,prefix_occ, suffix_occ):
        cand_occ = prefix_occ & suffix_occ
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

    def cal_occ_h(self, r_len, prefix_occ, suffix_occ):
        cand_occ=prefix_occ &suffix_occ

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
        self.opcount = 0
        a=0
        e=0
        while self.L[-1]:
            T1=time.time()
            newpattern=list()
            newocc=dict()
            Cd=[]
            self.L= copy.deepcopy(list(self.L[-1]))
            Lcd = copy.deepcopy(self.L)
            Ld = copy.deepcopy(self.L)
            self.Lc.clear()
            self.L.clear()
            Len = len(Ld[0])
            Om = copy.deepcopy({key: {occ + 1 for occ in values} for key, values in self.Fm[-1].items()})

            for ss in range(Len + 1):
                Cd.append(0)

            i=0
            while i< len(Ld):
                for temp in range(1,Len+2):
                    for j in range(Len):
                        if Ld[i][j]< temp:
                            Cd[j] = Ld[i][j]
                        else:
                            Cd[j] = Ld[i][j] + 1
                    Cd[Len]=temp
                    a+=1
                    Q=copy.deepcopy(Cd)
                    Q=Q[1:]
                    q=self.sort(Q)
                    size=len(Lcd)
                    for k in range(size):
                        r=self.sort(Lcd[k])
                        if q==r:
                            if Ld[i][0] != Lcd[k][-1]:
                                super_occ = self.cal_occ_1(Om[tuple(Ld[i])], self.Fm[-1][tuple(Lcd[k])])
                                if len(super_occ) >= self.minsup:
                                    newpattern.append(tuple(Cd))
                                    e += 1
                                    newocc[tuple(Cd)] = super_occ
                                    canddlist = sorted(super_occ)
                                    gaps = np.diff(canddlist)
                                    mu = np.mean(gaps)
                                    gap_std = np.std(gaps)
                                    cv = gap_std / mu
                                    if cv <= self.sta:
                                        self.SFP[-1].add(tuple(Cd))
                            else:
                                if Cd[0] < Cd[-1]:
                                    occ_r = self.cal_occ_r(len(Cd), Om[tuple(Ld[i])], self.Fm[-1][tuple(Lcd[k])])
                                    if len(occ_r) >= self.minsup:
                                        newpattern.append(tuple(Cd))
                                        newocc[tuple(Cd)] = occ_r
                                        e+=1
                                        canddlist = sorted(occ_r)
                                        gaps = np.diff(canddlist)
                                        mu = np.mean(gaps)
                                        gap_std = np.std(gaps)
                                        cv = gap_std / mu
                                        if cv <= self.sta:
                                            self.SFP[-1].add(tuple(Cd))
                                else:
                                    occ_h = self.cal_occ_h(len(Cd), Om[tuple(Ld[i])], self.Fm[-1][tuple(Lcd[k])])
                                    if len(occ_h) >= self.minsup:
                                        newpattern.append(tuple(Cd))
                                        newocc[tuple(Cd)] = occ_h
                                        e+=1
                                        canddlist = sorted(occ_h)
                                        gaps = np.diff(canddlist)
                                        mu = np.mean(gaps)
                                        gap_std = np.std(gaps)
                                        cv = gap_std / mu
                                        if cv <= self.sta:
                                            self.SFP[-1].add(tuple(Cd))
                i=i+1

            self.L.append(newpattern)
            self.Fm.append(newocc)
            self.Flist.append(set())
            for pattern in tuple(self.Fm[-1].keys()):
                self.Flist[-1].add(pattern)

        print("候选模式数量：", a + 2)
        print("频繁模式数量：", e)
        print("SOPP", len(self.SFP[-1]))

    def get_memory_usage(self):
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
        print("NEFO-PF")
        print("内存",memeory_after-memeory_before)
        print("SOPP", len(self.SFP[-1]))
        print("时间",endtime-starttime)

def main():

    file_path = ('/Users/zyj/PycharmProjects/incremental'
                 '/实验/最终对比试验文件/新的对比实验/SDB3_2000KB.txt')
    read_file(file_path)
    output_dic = "/Users/zyj/PycharmProjects/incremental/IOPP"
    minsup =50
    miner = NEFOMiner(file_path = file_path, output_dic = output_dic, minsup = minsup)
    miner.FOP_miner()
    print("\n")

if __name__ == '__main__':
    main()


