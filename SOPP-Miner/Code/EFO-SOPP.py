import copy
import os
import threading
import time
import tracemalloc
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
    minsup = 50

    def __init__(self, file_path='', output_filepath='', min_sup=50):
        """
        :param file_path: 输入文件位置
        :param output_filepath: 输出文件夹位置
        :param min_conf: 最小置信度
        :param min_sup: 最小支持度
        """
        self.S = read_file(file_path)
        self.output_filepath = output_filepath
        self.minsup = min_sup
        self.Cd.clear()
        self.Cd2.clear()
        self.Z.clear()
        self.Z2.clear()
        self.sopp=0
        self.maxsta=1
        self.a=0
        self.topk=dict()
        output_file = open(self.output_filepath + "/" + self.output_filename, 'w')
        output_file.close()

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
        if len(self.Z)>=self.minsup:
            gaps = np.diff(self.Z)
            mu = np.mean(gaps)
            gap_std = np.std(gaps)
            cv = gap_std / mu
            if cv <= self.maxsta:
                self.sopp += 1


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
        self.judge_fre(len(self.Z), self.Cd, self.Z)
        self.judge_fre(len(self.Z2), self.Cd2, self.Z2)
        if len(self.Z)>=self.minsup:
            gaps1 = np.diff(self.Z)
            mu1 = np.mean(gaps1)
            gap_std1 = np.std(gaps1)
            cv1 = gap_std1 / mu1
            if cv1 <= self.maxsta:
                self.sopp += 1
        if len(self.Z2) >= self.minsup:
            gaps2 = np.diff(self.Z2)
            mu2 = np.mean(gaps2)
            gap_std2 = np.std(gaps2)
            cv2 = gap_std2 / mu2
            if cv2 <= self.maxsta:
                self.sopp += 1


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
                #print(fre[i], L[0],fre[j],Lb[j][0])
                if L[0] >= self.minsup and Lb[j][0] >= self.minsup:
                    R = copy.deepcopy(fre[j])
                    R.pop()  # 求前缀
                    r = sort(R)
                    if q == r:
                        if fre[i][0] == fre[j][slen - 1]:  # 最前最后位置相等，拼接成两个模式
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
                            self.grow_BaseP2(len(self.Cd) - 1, Lb[j], L)


                        elif fre[i][0] < fre[j][slen - 1]:  # 第一个位置比最后一个位置小
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
            output_file = open(self.output_filepath + "/" + self.output_filename, 'a')
            strArr = "频繁模式："
            for i in Cd:
                strArr = strArr + str(i) + ","
            strArr = strArr + " 支持度为：" + str(sup_num)
            output_file.write(strArr + "\n")
            output_file.close()
            self.topk[tuple(Cd)] = sup_num
            self.rule_right = Cd
            self.rule_rightnum = sup_num
            self.allrulenum = self.allrulenum + 1
            self.frequent_num = self.frequent_num + 1
            self.fre_num = self.fre_num + 1


    def judge_fre2(self, sup_num, Cd, Z):
        if sup_num >= self.minsup:
            self.P.append(copy.deepcopy(Z))
            self.L.append(copy.deepcopy(Cd))
            output_file = open(self.output_filepath + "/" + self.output_filename, 'a')
            strArr = "频繁模式："
            for i in Cd:
                strArr = strArr + str(i) + ","
            strArr = strArr + " 支持度为：" + str(sup_num)
            output_file.write(strArr + "\n")
            output_file.close()
            self.topk[tuple(Cd)]=sup_num
            self.frequent_num = self.frequent_num + 1
            self.fre_num = self.fre_num + 1


    def find(self):
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

        self.judge_fre2(len(self.Z), self.Cd, self.Z)
        self.Cd.clear()
        self.judge_fre2(len(self.Z2), self.Cd2, self.Z2)
        self.Cd2.clear()


    def get_memory_usage(self):
        """获取当前进程的内存使用量（单位：MB）"""
        process = psutil.Process(os.getpid())
        memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        return memory_usage_mb

    def solve(self):

        begin_time = time.time()

        self.find()
        while self.fre_num:
            self.generate_fre()
        end_time = time.time()
        print("时间",end_time-begin_time)
        print("频繁", self.frequent_num)
        print("候选", self.a+2)
        print("sopp",self.sopp)

def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / (1024 * 1024)
    return memory_usage_mb


def main():
    file_path = ("/Users/zyj/Desktop/SOPP-Miner/Datasets/SDB3_2000KB.txt")
    #file_path = ("/Users/zyj/Desktop/SOPP-Miner/Datasets/SDB3.1-3.10/SDB3_1000KB.txt")
    min_sup = 50
    output_filepath = "/Users/zyj/PycharmProjects/incremental/IOPP"
    memory_before = get_memory_usage()
    miner = OPRMiner(file_path = file_path, output_filepath = output_filepath,min_sup=min_sup)
    miner.solve()
    memory_after = get_memory_usage()
    print("内存", memory_after - memory_before)



    print('\n')


if __name__ == '__main__':
    main()

