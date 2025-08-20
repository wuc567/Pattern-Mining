import os
import heapq
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
SPF=[]

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
        self.maxsta=0.5
        self.SFP= list()
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
        self.SFP.append(set())
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
            gaprlist=np.diff(list(occ_r))
            gap_std12=np.std(gaprlist)
            mu = np.mean(gap_std12)
            cv=gap_std12/mu
            if cv<=self.maxsta:
                self.SFP[-1].add((1, 2))


        if len(occ_h) >= self.minsup:
            self.Fm[-1][(2, 1)] = occ_h
            self.Flist[-1].add((2, 1))
            gaphlist=np.diff(list(occ_h))
            gap_std21=np.std(gaphlist)
            mu = np.mean(gap_std21)
            cv=gap_std21/mu
            if cv<=self.maxsta:
                self.SFP[-1].add((2, 1))

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
                                                    rlist=sorted(occ_r)
                                                    gaps=np.diff(rlist)
                                                    mu = np.mean(gaps)
                                                    gap_std=np.std(gaps)
                                                    cv=gap_std/mu
                                                    if cv <=self.maxsta:
                                                        self.SFP[-1].add(r)

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
                                                    hlist = sorted(occ_h)
                                                    gaps = np.diff(hlist)
                                                    mu = np.mean(gaps)
                                                    gap_std = np.std(gaps)
                                                    cv = gap_std/mu
                                                    if cv<=self.maxsta:
                                                        self.SFP[-1].add(h)

                                        if pattern[0] != suffix_sup[-1]:
                                            w = w + 1
                                            super_occ= self.cal_occ_1(cand_occ, O[pattern], self.Fm[-1][suffix_sup])
                                            if len(O[pattern]) < self.minsup:
                                                del O[pattern]
                                            if len(self.Fm[-1][suffix_sup]) < self.minsup:
                                                del self.Fm[-1][suffix_sup]
                                            if len(super_occ) >= self.minsup:
                                                new_FOP[tuple(super_op)] = super_occ
                                                canddlist=sorted(super_occ)
                                                gaps = np.diff(canddlist)
                                                mu = np.mean(gaps)
                                                gap_std = np.std(gaps)
                                                cv=gap_std/mu
                                                if cv <=self.maxsta:
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
        print("候选模式：", w+2)
        print("SOPP",len(self.SFP[-1]))

    def get_memory_usage(self):
        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / (1024 * 1024)  # 转换为MB
        return memory


#     def FOP_miner(self):
#         memeory_before = self.get_memory_usage()
#         starttime=time.time()
#         self.find_2()
#         self.find_m()
#         endtime = time.time()
#         memeory_after = self.get_memory_usage()
#         print(self.SFP)
#         print("NEFO-PF")
#         print("内存",memeory_after-memeory_before)
#         print("时间",endtime-starttime)
#
# def main():
#
#     #file_path = "/Users/zyj/Desktop/NEFOMiner/.txt"
#     #file_path = "/Users/zyj/Desktop/NEFOMiner/GOOG.txt"
#     #file_path = '/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_50KB.txt'
#     file_path = ("/Users/zyj/Desktop/NEFOMiner/AAPL.txt")
#     #file_path = "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/复核对比试验/car.txt"
#     read_file(file_path)
#     output_dic = "/Users/zyj/PycharmProjects/incremental/IOPP"
#     minsup = 10
#     #10Kb 3
#     #50Kb 10
#     #100Kb 18
#     #200Kb 60
#     #250Kb 70
#     #500Kb 145
#     #750Kb 225
#     #1000Kb 290
#
#     miner = NEFOMiner(file_path = file_path, output_dic = output_dic, minsup = minsup)
#     miner.FOP_miner()
#
#
#     #print('Memory usage: ', max(a) - min(a))
#
#     print("\n")


    def FOP_miner(self):
        memeory_before = self.get_memory_usage()
        starttime=time.time()
        self.find_2()
        self.find_m()
        endtime = time.time()
        memeory_after = self.get_memory_usage()

        print("内存",memeory_after-memeory_before)
        print("时间",endtime-starttime)


# from memory_profiler import memory_usage
# def main():
#     # filelist=["/Users/zyj/Desktop/NEFOMiner/AAPL.txt","/Users/zyj/Desktop/NEFOMiner/GOOG.txt",
#     #           "/Users/zyj/Desktop/NEFOMiner/KO.txt","/Users/zyj/Desktop/NEFOMiner/XOM2.txt",
#     #           "/Users/zyj/Desktop/NEFOMiner/beijing_PM2.5.txt","/Users/zyj/Desktop/NEFOMiner/beijing_O3.txt",
#     #           "/Users/zyj/Desktop/NEFOMiner/shanghai.txt","/Users/zyj/Desktop/NEFOMiner/mel_temperature.txt"]
#     filelist = ["/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_10KB.txt",
#                 "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_50KB.txt",
#                 "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_100KB.txt",
#                 "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_200KB.txt",
#                 "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_250KB.txt",
#                 "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_500KB.txt",
#                 "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_750KB.txt",
#                 "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_1000KB.txt"]
#     minsuplist=[3,10,18,60,70,145,225,290]
#     i=0
#     while i <= 7:
#     # for file_path in filelist and minsup in minsuplist:
#     #     print(file_path)
#     #file_path = "/Users/zyj/Desktop/NEFOMiner/.txt"
#     #file_path = "/Users/zyj/Desktop/NEFOMiner/GOOG.txt"
#     #file_path = '/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_50KB.txt'
#     # file_path = ('/Users/zyj/PycharmProjects/incremental'
#     #              '/实验/最终对比试验文件/新的对比实验/SDB3_1000KB.txt')
#     #file_path = "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/复核对比试验/car.txt"
#         file_path=(filelist[i])
#         read_file(filelist[i])
#         output_dic = "/Users/zyj/PycharmProjects/incremental/IOPP"
#         minsup = minsuplist[i]
#         print(minsup)
#         #10Kb 3
#         #50Kb 10
#         #100Kb 18
#         #200Kb 60
#         #250Kb 70
#         #500Kb 145
#         #750Kb 225
#         #1000Kb 290
#
#         miner = NEFOMiner(file_path=file_path, output_dic=output_dic, minsup=minsup)
#         miner.FOP_miner()
#         # a = memory_usage(miner.FOP_miner)
#         # print("最终内存", max(a) - min(a))
#         print('\n')
#
#
#         #print('Memory usage: ', max(a) - min(a))
#
#
#         i=i+1

from memory_profiler import memory_usage
def main():
    #file_path = "/Users/zyj/Desktop/NEFOMiner/mel_temperature.txt"
    #

    #file_path = "/Users/zyj/Desktop/NEFOMiner/.txt"
    #file_path = "/Users/zyj/Desktop/NEFOMiner/GOOG.txt"
    #file_path = '/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/新的对比实验/SDB3_50KB.txt'
    file_path = ('/Users/zyj/PycharmProjects/incremental'
                 '/实验/最终对比试验文件/新的对比实验/SDB3_2000KB.txt')
    #file_path = "/Users/zyj/PycharmProjects/incremental/实验/最终对比试验文件/复核对比试验/car.txt"
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
    miner.FOP_miner()



if __name__ == '__main__':
    main()
