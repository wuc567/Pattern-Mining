import copy
import os
import time
from tkinter import END
import numpy as np
import ctypes

import psutil

T=list()
def sort(src):
    src = src.argsort()
    src = src.argsort() + 1
    return src

def read_file(file_name):
    global T, T_size
    with open(file_name, 'r') as file:
        T.append(0)  # 确保出现位置与列表下标一致
        for line in file:
            if line.strip() == "":
                break
            T.extend([float(x) for x in line.split(" ") if x])
        T_size = len(T) - 1

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
    minsup = 12
    maxsta=0.5

    def __init__(self, file_path='', output_filepath='',
                 min_conf=0.4, min_sup=50):
        """
        :param file_path: 输入文件位置
        :param output_filepath: 输出文件夹位置
        :param min_conf: 最小置信度
        :param min_sup: 最小支持度
        """
        self.input_filepath = file_path
        self.output_filepath = output_filepath
        self.minconf = min_conf
        self.minsup = min_sup
        self.maxsta = 0.5
        self.sopp=0
        self.L2 = np.zeros((700, 700))
        self.L = np.zeros((1500, 1500))
        self.C = np.zeros((5000, 5000))
        self.text = [0] * 50000
        self.pattern = [0] * 100000
        self.sorted_pat = [0] * 100000
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
        output_file = open(self.output_filepath + "/" + self.output_filename, 'a')
        self.gen_aux(self.aux, pattern_size)
        output_file = open(self.output_filepath + "/" + self.output_filename, 'a')
        self.transform_text(text, txt_size - 1)
        self.transform_pattern(pattern, pattern_size - 1)
        self.pattern_num= self.BNDM(self.trans_text, self.trans_pattern, txt_size - 1, pattern_size - 1)
        return self.pattern_num

    def matching2(self, text, pattern, txt_size, pattern_size):
        for i in range(pattern_size):
            self.sorted_pat[i] = pattern[i]
        self.radix_sort(self.sorted_pat, pattern_size)
        self.gen_aux(self.aux, pattern_size)
        self.transform_text(text, txt_size - 1)
        self.transform_pattern(pattern, pattern_size - 1)
        self.pattern_num =self.SBNDM(self.trans_text, self.trans_pattern, txt_size - 1, pattern_size - 1)
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
                """output_file = open(self.output_filepath + "/" + self.output_filename, 'a')
                strArr = "模式（"
                for i in self.L[self.frequent_num]:
                    if i != 0:
                        strArr = strArr + str(int(i)) + ","
                strArr = strArr + "）频繁"
                strArr = strArr + "置信度为：" + str(support_full)
                output_file.write(strArr + "\n")
                output_file.close()"""
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
            Q = Q[1:slen]
            q = sort(Q)
            for j in range(self.frequent_num):
                R = copy.deepcopy(fre[j])
                R = R[:slen - 1]
                r = sort(R)
                if (q[:slen - 1] == r[:slen - 1]).all():
                    if fre[i][0] == fre[j][slen - 1]:  # 最前最后位置相等，拼接成两个模式
                        self.C[self.candidate_num][0] = fre[i][0]
                        self.C[self.candidate_num + 1][0] = fre[i][0] + 1
                        self.C[self.candidate_num][slen] = fre[i][0] + 1
                        self.C[self.candidate_num + 1][slen] = fre[i][0]
                        for t in range(1, slen):
                            if fre[i][t] > fre[j][slen - 1]:  # 中间位置增长
                                self.C[self.candidate_num][t] = fre[i][t] + 1
                                self.C[self.candidate_num + 1][t] = fre[i][t] + 1
                            else:
                                self.C[self.candidate_num][t] = fre[i][t]
                                self.C[self.candidate_num + 1][t] = fre[i][t]
                        self.candidate_num = self.candidate_num + 2
                        self.compnum = self.compnum + 2
                        self.scan_num = self.scan_num + 2

                    elif fre[i][0] < fre[j][slen - 1]:  # 第一个位置比最后一个位置小
                        self.C[self.candidate_num][0] = fre[i][0]  # 小的不变
                        self.C[self.candidate_num][slen] = fre[j][slen - 1] + 1  # 大的加一
                        for t in range(1, slen):
                            if fre[i][t] > fre[j][slen - 1]:
                                self.C[self.candidate_num][t] = fre[i][t] + 1  # 中间位置增长
                            else:
                                self.C[self.candidate_num][t] = fre[i][t]
                        self.candidate_num = self.candidate_num + 1
                        self.compnum = self.compnum + 1
                        self.scan_num = self.scan_num + 1
                    else:
                        self.C[self.candidate_num][0] = fre[i][0] + 1  # 大的加一
                        self.C[self.candidate_num][slen] = fre[j][slen - 1]  # 小的不变
                        for t in range(slen - 1):
                            if fre[j][t] > fre[i][0]:

                                self.C[self.candidate_num][t + 1] = fre[j][t] + 1  # 中间位置增长
                            else:
                                self.C[self.candidate_num][t + 1] = fre[j][t]
                        self.candidate_num = self.candidate_num + 1
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
                    """output_file = open(self.output_filepath + "/" + self.output_filename, 'a')
                    strArr = "模式（"
                    for i in self.L[self.frequent_num]:
                        if i != 0:
                            strArr = strArr + str(int(i)) + ","
                    strArr = strArr + "）频繁"
                    strArr = strArr + "置信度为：" + str(suppoty_full)
                    output_file.write(strArr + "\n")
                    output_file.close()"""
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
        lmplist=[]
        while pos <= txt_length - pat_length:
            self.read_num = self.read_num + 1
            j = pat_length - 1
            last = pat_length
            D = -1
            D = ctypes.c_uint32(D).value
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
        if len(lmplist)>=self.minsup:
            gaps = np.diff(lmplist)
            mu = np.mean(gaps)
            gap_std = np.std(gaps)
            cv = gap_std / mu
            if cv <= self.maxsta:
                self.sopp += 1

        return self.pattern_num



    def SBNDM(self, txt, pat, txt_length, pat_length):
        D, k, q= 0, 0, 0
        lmplist=[]
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

        return self.pattern_num


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
        """
        :param file_path: 文件位置
        :return: 文件内容列表
        """
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
        memeory_before = self.get_memory_usage()
        self.read_file(self.input_filepath)
        begin_time = time.time()
        self.generate_candL2()
        self.generate_fre(self.pattern, self.L2)
        self.Cancalute()
        memeory_after = self.get_memory_usage()
        print("内存", round((memeory_after - memeory_before),2))
        end_time = time.time()
        time_consuming = end_time - begin_time
        print("The time-consuming:",round(time_consuming,4))
        print("频繁模式", self.count)
        print("候选模式", self.compnum)
        print("SOPP",self.sopp)



def main():
    file_path=('/Users/zyj/PycharmProjects/incremental'
                  '/实验/最终对比试验文件/新的对比实验/SDB3_1000KB.txt')
    # file_path = "/Users/zyj/Desktop/NEFOMiner/GOOG.txt"
    read_file(file_path)
    output_dic = "/Users/zyj/PycharmProjects/incremental/IOPP"
    min_conf=0.4
    minsup=50
    miner = OPPMiner(file_path=file_path, output_filepath=output_dic, min_conf=min_conf, min_sup=minsup)
    miner.solve()

if __name__ == '__main__':
    main()

