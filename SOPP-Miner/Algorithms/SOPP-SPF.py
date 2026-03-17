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
    Z = []
    Z2 = []
    def __init__(self, file_path, output_dic, minsup):
        self.file_path = file_path
        self.output_dic = output_dic
        self.minsup = minsup
        self.output_filename = output_filename
        self.Fm = list()
        self.sopp=0
        self.Flist = list()
        self.opcount = 0
        self.Z.clear()
        self.Z2.clear()
        self.SFP = list()
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
            self.Fm[-1][(1, 2)] = occ_r
            self.Flist[-1].add((1, 2))
            gaphlist=np.diff(list(occ_r))
            gap_std21=np.std(gaphlist)
            mu = np.mean(gap_std21)
            cv=gap_std21/mu
            if cv <= self.maxsta:
                self.SFP[-1].add((1, 2))
                self.sopp += 1



        if len(occ_h) >= self.minsup:
            self.Fm[-1][(2, 1)] = occ_h
            self.Flist[-1].add((2, 1))
            gaphlist=np.diff(list(occ_h))
            gap_std21=np.std(gaphlist)
            mu = np.mean(gap_std21)
            cv=gap_std21/mu
            if cv <= self.maxsta:
                self.SFP[-1].add((2, 1))
                self.sopp += 1



        with open(self.output_dic + "/" + self.output_filename, 'a') as output_file:
            for pattern in self.Fm[-1]:
                output_str = f"频繁模式: {pattern} -> 支持度: {len(self.Fm[-1][pattern])}\n"
                output_file.write(output_str)



    def grow_BaseP1(self, Ld, L):
        p, q = copy.deepcopy(sorted(L[1:])), copy.deepcopy(sorted(Ld[1:]))
        i=0
        j=0
        Z=[]
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i] + 1:
                    Z.append(copy.deepcopy(q[j]))
                    j=j+1
                    i=i+1
                elif p[i] < q[j]:
                    i=i+1
                else:
                    j=j+1
            else:
                break

        L[0] = L[0] - len(Z)
        Ld[0] = Ld[0] - len(Z)
        #occ = copy.deepcopy(set(Z))
        occ=Z
        return occ

    def grow_r(self, slen, Ld, L):

        first, fri, i, j = 0, 0, 0, 0
        p, q = copy.deepcopy(sorted(L[1:])), copy.deepcopy(sorted(Ld[1:]))
        Z1=[]

        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i] + 1:
                    first = q[j]
                    fri = first - slen
                    if T[first] > T[fri]:
                        Z1.append(copy.deepcopy(q[j]))
                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break

        L[0] = L[0] - len(Z1)
        Ld[0] = Ld[0] - len(Z1)

        #occ_r = copy.deepcopy(set(Z1))
        occ_r = copy.deepcopy(Z1)

        return occ_r

    def grow_h(self, slen, Ld, L):

        first, fri, i, j = 0, 0, 0, 0
        p, q = copy.deepcopy(sorted(L[1:])), copy.deepcopy(sorted(Ld[1:]))
        Z2=[]
        while True:
            if i < len(p) and j < len(q):
                if q[j] == p[i] + 1:
                    first = q[j]
                    fri = first - slen
                    if T[first] < T[fri]:
                        Z2.append(copy.deepcopy(q[j]))

                    j = j + 1
                    i = i + 1
                elif p[i] < q[j]:
                    i = i + 1
                else:
                    j = j + 1
            else:
                break

        L[0] = L[0] - len(Z2)
        Ld[0] = Ld[0] - len(Z2)
        occ_h = Z2

        return occ_h



    def find_m(self):
        w=0
        asd=0
        self.opcount += 1
        while self.Flist[-1]:
            new_FOP=dict()
            Lb=[]
            fre = copy.deepcopy(list(self.Flist[-1]))
            slen=len(fre[0])
            fre_number=len(self.Flist[-1])
            for x in range(fre_number):
                Lb.append([])

            for pat in fre:

                s=fre.index(pat)
                Lb[s].append(len(self.Fm[-1][pat]))

                for pos in list(self.Fm[-1][pat]):
                    Lb[s].append(pos)

            #print(len(fre))
            for pattern in fre:
                    L=[]
                    size = len(self.Fm[-1][pattern])
                    L.append(size)
                    for pos in list(self.Fm[-1][pattern]):
                        L.append(pos)

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

                        if suffix_sup in fre:

                            j=fre.index(tuple(suffix_sup))
                            #print(pattern,L[0], suffix_sup, Lb[j][0])

                            if L[0]>=self.minsup and Lb[j][0]>=self.minsup:

                                    #print(super_op)
                                    w=w+1

                                    if pattern[0] == suffix_sup[-1]:
                                        if super_op[0] < super_op[-1]:
                                            r = tuple(super_op)
                                            #w = w + 1
                                            occ_r = self.grow_r(slen,Lb[j],L)
                                            if len(occ_r)>= self.minsup:
                                                new_FOP[r]=occ_r
                                                gaps = np.diff(occ_r)
                                                mu = np.mean(gaps)
                                                gap_std = np.std(gaps)
                                                cv=gap_std/mu
                                                if cv <= self.maxsta:
                                                    self.SFP[-1].add(r)
                                                    self.sopp += 1
                                        if super_op[0] > super_op[-1]:
                                            h = tuple(super_op)
                                            #w = w + 1

                                            occ_h = self.grow_h(slen,Lb[j],L)



                                            if len(occ_h)>= self.minsup:
                                                new_FOP[h]=occ_h
                                                gaps = np.diff(occ_h)
                                                mu = np.mean(gaps)
                                                gap_std = np.std(gaps)
                                                cv=gap_std/mu
                                                if cv <= self.maxsta:
                                                    self.SFP[-1].add(h)
                                                    self.sopp += 1

                                    if pattern[0] != suffix_sup[-1]:

                                        super_occ = self.grow_BaseP1(Lb[j],L)


                                        if len(super_occ) >= self.minsup:
                                            new_FOP[tuple(super_op)] = super_occ
                                            gaps = np.diff(super_occ)
                                            mu = np.mean(gaps)
                                            gap_std = np.std(gaps)
                                            cv = gap_std / mu
                                            if cv <= self.maxsta:
                                                self.SFP[-1].add(tuple(super_op))
                                                self.sopp+=1

            self.Fm.append(new_FOP)


            self.Flist.append(set())
            for pattern in tuple(self.Fm[-1].keys()):
                self.Flist[-1].add(pattern)
        e=0
        for lists in self.Flist:
            e+=len(lists)
        print("频繁模式",e)
        print("候选模式：", w+2)
        print("SOPP", len(self.SFP[-1]))



    def get_memory_usage(self):
        """获取当前进程的内存使用量（单位：MB）"""
        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / (1024 * 1024)  # 转换为MB
        return memory

    def FOP_miner(self):
        tracemalloc.start()
        begin_time = time.time()
        start_mem, _ = tracemalloc.get_traced_memory()
        memeory_begin = self.get_memory_usage()
        self.find_2()
        self.find_m()
        end_time = time.time()
        memeory_after = self.get_memory_usage()
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print("neicun", memeory_after-memeory_begin)
        print("时间",end_time-begin_time)


def main():

    minsup = 50

    file_path = ('/Users/zyj/PycharmProjects/incremental/实验'
                 '/最终对比试验文件/新的对比实验/SDB3_1000KB.txt')
    read_file(file_path)
    output_dic = "/Users/zyj/PycharmProjects/incremental/IOPP"

    #10Kb 3
    #50Kb 10
    #100Kb 18
    #200Kb 60
    #250Kb 70
    #500Kb 145
    #750Kb 225
    #1000Kb 290


    miner = NEFOMiner(file_path = file_path, output_dic = output_dic, minsup = minsup)
    miner.FOP_miner()
    # a = memory_usage(miner.FOP_miner)
    # print(max(a)-min(a))
    print('\n')


if __name__ == '__main__':
    main()
