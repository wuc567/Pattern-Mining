import copy
import time
import tracemalloc
from tkinter import END
import numpy as np
import ctypes

import psutil


def sort(src):
    src = src.argsort()
    src = src.argsort() + 1
    return src


class OPPMiner:
    """
    OPP算法
    """
    count = 0
    candidate_num = 0
    compnum = 2
    L2 = np.zeros((700, 700))
    L = np.zeros((1500, 1500))
    scan_num = 0
    read_num = 0
    C = np.zeros((5000, 5000))
    Snum = 0
    frequent_num = 0
    LEN = 0
    text = [0]*50000
    pattern = [0]*100000
    sorted_pat = [0]*100000
    aux = [0]*100000
    trans_text = [0]*49999
    trans_pattern = [0] *199999
    pattern_num = 0
    sDB = [[], 0]

    output_filepath = ""
    output_filename = "OPP-Miner-Output.txt"
    minconf = 0.4
    minsup = 200

    def __init__(self, file_path='', output_filepath='',
                 min_conf=0.4, min_sup=200):

        self.input_filepath = file_path
        self.output_filepath = output_filepath
        self.minconf = min_conf
        self.minsup = min_sup
        self.L2 = np.zeros((700, 700))
        self.L = np.zeros((1500, 1500))
        self.C = np.zeros((5000, 5000))
        self.text = [0] * 50000
        self.pattern = [0] * 100000
        self.sorted_pat = [0] * 100000
        self.maxsta=0.5
        self.sopp=0
        self.aux = [0] * 100000
        self.trans_text = [0] * 199999
        self.trans_pattern = [0] * 199999
        self.sDB = [[], 0]

        output_file = open(self.output_filepath + "/" + self.output_filename, 'w')
        output_file.close()


    def matching1(self, text, pattern, txt_size, pattern_size):
        for i in range(pattern_size):
            self.sorted_pat[i] = pattern[i]
        self.radix_sort(self.sorted_pat, pattern_size)
        self.gen_aux(self.aux, pattern_size)
        self.transform_text(text, txt_size - 1)
        self.transform_pattern(pattern, pattern_size - 1)
        self.BNDM(self.trans_text, self.trans_pattern, txt_size - 1, pattern_size - 1)
        return self.pattern_num

    def matching2(self, text, pattern, txt_size, pattern_size):
        for i in range(pattern_size):
            self.sorted_pat[i] = pattern[i]
        self.radix_sort(self.sorted_pat, pattern_size)
        self.gen_aux(self.aux, pattern_size)
        self.transform_text(text, txt_size - 1)
        self.transform_pattern(pattern, pattern_size - 1)
        self.SBNDM(self.trans_text, self.trans_pattern, txt_size - 1, pattern_size - 1)
        return self.pattern_num

    def generate_candL2(self):
        c = [[1, 2], [2, 1]]
        for j in range(2):
            self.scan_num = self.scan_num + 1
            self.pattern = c[j]
            support_full = self.matching1(self.sDB[0], self.pattern, self.sDB[1], 2)
            if support_full >= self.minsup:
                self.count = self.count + 1
                self.L[self.frequent_num][:2] = copy.deepcopy(c[j][:2])
                self.frequent_num = self.frequent_num + 1
                for x in range(2):
                    self.L2[j][x] = c[j][x]


    def generate_fre(self, min, fre):
        slen = 0
        Q = [0]
        R = [0]
        for y in range(50):
            if fre[0][y] != 0:
                slen = slen + 1
        for i in range(self.frequent_num):
            Q = copy.deepcopy(fre[i])
            Q = Q[0:slen]
            Q=Q.astype(int)
            for k in range(1, slen + 2):
                super_op = list(Q)
                super_op.append(k)
                for j in range(slen):
                    if super_op[j] >= super_op[-1]:
                        super_op[j] += 1
                suffix_sup = super_op[1:]
                for j in range(slen):
                    if suffix_sup[j] > super_op[0]:
                        suffix_sup[j] -= 1
                suffix_sup = tuple(suffix_sup)
                if np.any(np.all(fre[:, :len(suffix_sup)] == suffix_sup, axis=1)):



                    if Q[0] == suffix_sup[-1]:
                        if super_op[0] < super_op[-1]:
                            r=copy.deepcopy(super_op)
                            self.C[self.candidate_num][:slen+1]=r
                            self.candidate_num += 1
                            self.compnum = self.compnum + 1
                            self.scan_num = self.scan_num + 1
                            super_op[0], super_op[-1] = super_op[-1], super_op[0]
                            h = copy.deepcopy(super_op)
                            self.C[self.candidate_num][:slen+1] = h
                            self.compnum = self.compnum + 1
                            self.scan_num = self.scan_num + 1
                            self.candidate_num += 1


                    else:
                        r2=copy.deepcopy(super_op)
                        self.C[self.candidate_num, :slen+1] = r2
                        self.candidate_num += 1
                        self.compnum = self.compnum + 1
                        self.scan_num = self.scan_num + 1


    def Cancalute(self):
        Len, suppoty_full, r= 0, 0, 0
        self.frequent_num = 0
        while self.candidate_num != 0:
            for r in range(50):
                if self.C[0][r] != 0:
                    Len = Len + 1

            for v in range(self.candidate_num):
                self.pattern = copy.deepcopy(self.C[v])
                suppoty_full = self.matching2(self.sDB[0], self.C[v], self.sDB[1], Len)
                if suppoty_full >= self.minsup:
                    self.count = self.count + 1
                    self.L[self.frequent_num][:Len] = copy.deepcopy(self.C[v][:Len])
                    self.frequent_num = self.frequent_num + 1
            Len = 0
            self.C = np.zeros((2000, 2000))
            self.candidate_num = 0
            self.generate_fre(self.pattern, self.L)
            self.L = np.zeros((700, 700))
            self.frequent_num = 0

    def transform_text(self, txt, txt_length):
        for loop in range(txt_length):
            if txt[loop] < txt[loop + 1]:
                self.trans_text[loop] = 49
            else:
                self.trans_text[loop] = 48

    def transform_pattern(self, pat, pat_length):
        for loop in range(pat_length):
            if pat[loop] < pat[loop + 1]:
                self.trans_pattern[loop] = 49
            else:
                self.trans_pattern[loop] = 48

    def BNDM(self, txt, pat, txt_length, pat_length):
        flag, f, pos, lmp = 0, 0, 0, 0
        self.pattern_num = 0
        B = [0]*256
        for i in range(pat_length):
            B[int(pat[i])] = ctypes.c_uint32(B[int(pat[i])]).value | 1 << (pat_length - i - 1)
        while pos <= txt_length - pat_length:
            self.read_num = self.read_num + 1
            j = pat_length - 1
            last = pat_length
            D = -1
            D = ctypes.c_uint32(D).value
            lmplist=[]
            while D:
                D = D & B[int(txt[pos + j])]
                if (D & (1 << (pat_length - 1))) != 0:
                    if j > 0:
                        last = j
                    else:
                        len_cand = pos + pat_length
                        k = 0
                        cand = pos
                        for x in range(pos, len_cand):
                            if self.sDB[0][cand - 1 + self.aux[k]] >= self.sDB[0][cand - 1 + self.aux[k+1]]:
                                f = 0
                                break
                            else:
                                f = 1
                            k = k + 1
                        if f > 0:
                            flag = 1
                            lmp = pos - pat_length + 2
                            lmplist.append(lmp)
                            self.pattern_num = self.pattern_num + 1
                j = j - 1
                D = D << 1
            pos = pos + last
            if len(lmplist) >= self.minsup:
                gaps = np.diff(lmplist)
                mu = np.mean(gaps)
                gap_std = np.std(gaps)
                cv = gap_std / mu
                if cv <= self.maxsta:
                    self.sopp += 1

    def SBNDM(self, txt, pat, txt_length, pat_length):
        lmplist = []
        self.pattern_num = 0
        flag, f = 0, 0
        B = [0]*256

        for j in range(pat_length):
            B[int(pat[j])] = ctypes.c_uint32(B[int(pat[j])]).value | (1 << (pat_length - j - 1))
            self.read_num = self.read_num + 1
        pos = pat_length - 1
        while pos <= txt_length - 1:
            D = (B[txt[pos - 1]]) & (B[txt[pos]] << 1)
            if D != 0:
                j = pos - pat_length + 1
                while True:
                    pos = pos - 1
                    if pos == 0:
                        D = 0
                    else:
                        D = (D << 1) & B[txt[pos - 1]]
                    if D == 0:
                        break
                if j == pos:
                    len_cand = j + pat_length
                    k = 0
                    cand = j
                    for x in range(j, len_cand):
                        if self.sDB[0][cand - 1 + self.aux[k]] >= self.sDB[0][cand - 1 + self.aux[k + 1]]:
                            f = 0
                            break
                        else:
                            f = 1
                        k = k + 1
                    if f > 0:
                        flag = 1
                        lmp = pos - pat_length + 2
                        lmplist.append(lmp)
                        self.pattern_num = self.pattern_num + 1
                    pos = pos + 1
            pos = pos + pat_length - 1

        if len(lmplist)>=self.minsup:
            gaps = np.diff(lmplist)
            mu = np.mean(gaps)
            gap_std = np.std(gaps)
            cv = gap_std / mu
            if cv <= self.maxsta:
                self.sopp += 1

    def radix_sort(self, arr, length):
        countArr = []
        copyArr = [0] * length
        for pas in range(4):
            countArr = [0] * 256
            for j in range(length):
                countArr[(ctypes.c_uint32(int(arr[j])).value >> 8 * pas) & 255] = countArr[(ctypes.c_uint32(int(arr[j])).value >> 8 * pas) & 255] + 1
            for k in range(1, 256):
                countArr[k] = countArr[k] + countArr[k - 1]
            for m in range(length - 1, -1, -1):
                countArr[(ctypes.c_uint32(int(arr[m])).value >> 8 * pas) & 255] = countArr[(ctypes.c_uint32(int(arr[m])).value >> 8 * pas) & 255] - 1
                copyArr[countArr[(ctypes.c_uint32(int(arr[m])).value >> 8 * pas) & 255]] = arr[m]
            for n in range(length):
                arr[n] = copyArr[n]
        copyArr.clear()

    def gen_aux(self, arr, length):
        for i in range(length):
            for j in range(length):
                if self.sorted_pat[i] == self.pattern[j]:
                    arr[i] = j + 1

    def read_file(self, file_path):
        file = open(file_path, 'r')
        all_lines = file.readlines()
        for i in range(len(all_lines)):
            if not all_lines[i].isspace():
                self.sDB[0].append(float(all_lines[i]))
                self.sDB[1] = self.sDB[1] + 1

    def get_memory_usage(self):
        process = psutil.Process(os.getpid())
        memory = process.memory_info().rss / (1024 * 1024)  # 转换为MB
        return memory

    def solve(self):


        self.read_file(self.input_filepath)
        memeory_before = self.get_memory_usage()

        begin_time = time.time()

        self.generate_candL2()
        self.generate_fre(self.pattern, self.L2)
        self.Cancalute()
        end_time = time.time()
        memeory_after = self.get_memory_usage()
        print("NEFO-Mat")
        print("内存",memeory_after-memeory_before)
        print("时间",end_time - begin_time)
        print("候选模式",self.compnum)
        print("频繁",self.count)
        print("sopp",self.sopp)

import os
def get_memory_usage():
    """获取当前进程的内存使用量（单位：MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def main():
    #file_path="/Users/zyj/Desktop/NEFOMiner/AAPL.txt"
              # ,"/Users/zyj/Desktop/NEFOMiner/GOOG.txt",)
              # "/Users/zyj/Desktop/NEFOMiner/KO.txt","/Users/zyj/Desktop/NEFOMiner/XOM2.txt",
              # "/Users/zyj/Desktop/NEFOMiner/beijing_PM2.5.txt","/Users/zyj/Desktop/NEFOMiner/beijing_O3.txt",
              # "/Users/zyj/Desktop/NEFOMiner/shanghai.txt","/Users/zyj/Desktop/NEFOMiner/mel_temperature.txt"]
    # for file_path in filelist:
    #     print(file_path)
    #file_path = "/Users/zyj/Desktop/NEFOMiner/XOM2.txt"
    file_path=("/Users/zyj/PycharmProjects/incremental"
               "/实验/最终对比试验文件/新的对比实验/SDB3_1000KB.txt")

    output_dic = "/Users/zyj/PycharmProjects/incremental/IOPP"
    minconf=0.4
    min_sup=50
        #10Kb 3
        #50Kb 10
        #100Kb 18
        #200Kb 60
        #250Kb 70
        #500Kb 145
        #750Kb 225
        #1000Kb 290

    miner = OPPMiner(file_path=file_path, output_filepath=output_dic,min_conf=minconf, min_sup=min_sup)
    miner.solve()
    print('\n')






if __name__ == '__main__':
    main()
