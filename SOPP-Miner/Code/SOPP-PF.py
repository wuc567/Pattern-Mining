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
        self.Flist = list()
        self.maxsta=0.5
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
            if cv <= self.maxsta:
                self.SFP[-1].add((1, 2))

        if len(occ_h) >= self.minsup:
            self.L[-1].append([2, 1])
            self.Fm[-1][(2, 1)]=occ_h
            gaphlist = np.diff(list(occ_h))
            gap_std21 = np.std(gaphlist)
            mu = np.mean(gap_std21)
            cv = gap_std21 / mu
            if cv <= self.maxsta:
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


    def cal_occ_2(self, r_len, prefix_occ, suffix_occ):
        occ_r = set()
        occ_h = set()
        cand_occ = prefix_occ & suffix_occ

        for occ in cand_occ:
            t_begin = T[occ - r_len + 1]
            t_end = T[occ]
            if t_begin == t_end:
                continue
            if t_begin < t_end:
                occ_r.add(occ)
            else:
                occ_h.add(occ)
        prefix_occ-=(occ_r|occ_h)
        suffix_occ-=(occ_r|occ_h)

        return occ_r, occ_h




    def find_m(self):
        self.opcount = 0
        a=0
        x=0
        generatetime=[]
        while self.L[-1]:
            T1=time.time()
            newpattern=list()
            newocc=dict()
            Cd=[]
            Cd2=[]
            patterns=self.L[-1]
            pattern_number=len(patterns)

            slen=len(patterns[0])
            Om = copy.deepcopy({key: {occ + 1 for occ in values} for key, values in self.Fm[-1].items()})

            for ss in range(slen + 1):
                Cd.append(0)
                Cd2.append(0)
            cal_time = 0

            for i in range(pattern_number):

                Q = copy.deepcopy(patterns[i])
                Q = Q[1:]
                q = self.sort(Q)
                #L = []
                for j in range(pattern_number):

                    if len(Om[tuple(patterns[i])])>=self.minsup and len(self.Fm[-1][tuple(patterns[j])])>=self.minsup:


                        R=copy.deepcopy(patterns[j])
                        R.pop()
                        r = self.sort(R)
                        if q == r:

                            if patterns[i][0]==patterns[j][slen-1]:
                                Cd[0] = patterns[i][0]
                                Cd2[0] = patterns[i][0] + 1
                                Cd[slen] = patterns[i][0] + 1
                                Cd2[slen] = patterns[i][0]
                                for t in range(1, slen):
                                    if patterns[i][t] > patterns[j][slen - 1]:
                                        Cd[t] = patterns[i][t] + 1
                                        Cd2[t] = patterns[i][t] + 1
                                    else:
                                        Cd[t] = patterns[i][t]
                                        Cd2[t] = patterns[i][t]
                                r = copy.deepcopy(Cd)
                                h = copy.deepcopy(Cd2)

                                a=a+2

                                cd_occ, cd2_occ = self.cal_occ_2(slen + 1, Om[tuple(patterns[i])], self.Fm[-1][tuple(patterns[j])])

                                if len(cd_occ) >= self.minsup:
                                    x+=1
                                    newpattern.append(r)
                                    newocc[tuple(r)] = cd_occ
                                    canddlist = sorted(cd_occ)
                                    gaps = np.diff(canddlist)
                                    mu = np.mean(gaps)
                                    gap_std = np.std(gaps)
                                    cv = gap_std / mu
                                    if cv <= self.maxsta:
                                        self.SFP[-1].add(tuple(r))
                                if len(cd2_occ) >= self.minsup:
                                    x+=1
                                    newpattern.append(h)
                                    newocc[tuple(h)] = cd2_occ
                                    canddlist = sorted(cd2_occ)
                                    gaps = np.diff(canddlist)
                                    mu = np.mean(gaps)
                                    gap_std = np.std(gaps)
                                    cv = gap_std / mu
                                    if cv <= self.maxsta:
                                        self.SFP[-1].add(tuple(h))


                            elif patterns[i][0] < patterns[j][slen - 1]:  # 第一个位置比最后一个位置小
                                a=a+1
                                Cd[0] = patterns[i][0]  # 小的不变
                                Cd[slen] = patterns[j][slen - 1] + 1  # 大的加一
                                for t in range(1, slen):
                                    if patterns[i][t] > patterns[j][slen - 1]:
                                        Cd[t] = patterns[i][t] + 1  # 中间位置增长
                                    else:
                                        Cd[t] = patterns[i][t]
                                Cd3=copy.deepcopy(Cd)

                                occ = self.cal_occ_1(Om[tuple(patterns[i])], self.Fm[-1][tuple(patterns[j])])

                                if len(occ) >= self.minsup:
                                    x+=1
                                    newpattern.append(Cd3)
                                    newocc[tuple(Cd3)] = occ
                                    canddlist = sorted(occ)
                                    gaps = np.diff(canddlist)
                                    mu = np.mean(gaps)
                                    gap_std = np.std(gaps)
                                    cv = gap_std / mu
                                    if cv <= self.maxsta:
                                        self.SFP[-1].add(tuple(Cd3))

                            else:
                                a=a+1
                                Cd[0] = patterns[i][0] + 1  # 大的加一
                                Cd[slen] = patterns[j][slen - 1]  # 小的不变
                                for t in range(slen - 1):
                                    if patterns[j][t] > patterns[i][0]:
                                        Cd[t + 1] = patterns[j][t] + 1  # 中间位置增长
                                    else:
                                        Cd[t + 1] = patterns[j][t]
                                Cd4 = copy.deepcopy(Cd)
                                occ = self.cal_occ_1(Om[tuple(patterns[i])], self.Fm[-1][tuple(patterns[j])])

                                if len(occ) >= self.minsup:
                                    x+=1
                                    newpattern.append(Cd4)
                                    newocc[tuple(Cd4)] = occ
                                    canddlist = sorted(occ)
                                    gaps = np.diff(canddlist)
                                    mu = np.mean(gaps)
                                    gap_std = np.std(gaps)
                                    cv = gap_std / mu
                                    if cv <= self.maxsta:
                                        self.SFP[-1].add(tuple(Cd4))

            T2=time.time()
            alb=T2-T1-cal_time
            generatetime.append(alb)

            self.L.append(newpattern)
            self.Fm.append(newocc)

        print("候选模式数量：", a+2)
        x=0
        for l in self.L:
            x+=(len(l))
        print("频繁模式数量：", x)

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
        print("NEFO-PF")
        print("内存",memeory_after-memeory_before)
        print("SOPP", len(self.SFP[-1]))
        #print("时间",endtime2-starttime1)


from memory_profiler import memory_usage
def main():
    file_path = ('/Users/zyj/PycharmProjects/incremental/实验'
                 '/最终对比试验文件/新的对比实验/SDB3_2000KB.txt')
    # file_path ="/Users/zyj/Desktop/NEFOMiner/AAPL.txt"

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
    starttime1 = time.time()
    miner = NEFOMiner(file_path = file_path, output_dic = output_dic, minsup = minsup)
    miner.FOP_miner()
    endtime2 = time.time()
    print(endtime2 - starttime1)
    print("\n")


if __name__ == '__main__':
    main()


