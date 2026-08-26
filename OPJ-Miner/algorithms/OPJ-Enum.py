import copy
import os
import time
import tracemalloc

import numpy as np
from memory_profiler import memory_usage
from scipy.stats import laplace, norm


def read_file(file_name):
    global T, T_size
    with open(file_name, 'r') as file:
        # 出现位置比列表下标大1
        content = file.read().strip()  # 去除首尾空白字符（如换行、空格）
        if not content:  # 处理空文件
            return []
        T = [float(x) for x in content.split(' ') if x]
        T_size = len(T)


def pattern_enum(opj, new_FOP, new_occ_dic):
    global cand_cnt
    # op是OPJ中的保序部分((1,2),(L))中的(1,2)
    op_len = len(opj[0])
    # 枚举保序的最后一个位置，从1开始
    last_rank = 1
    # 最后一位从i=1开始枚举
    while last_rank <= op_len + 1:
        # s_op是op的超模式，其的前缀是op本身
        s_opp = list(opj[0])
        # 末尾添加枚举的位置
        s_opp.append(last_rank)
        # 调整末尾前面的元素秩序，让超模式满足op定义
        for j in range(op_len):
            if s_opp[j] >= last_rank:
                s_opp[j] += 1
        # 获取超模式的后缀，并使其满足保序定义
        s_opp_suf = s_opp[1:]
        for j in range(op_len):
            if s_opp_suf[j] > s_opp[0]:
                s_opp_suf[j] -= 1
        s_opp = tuple(s_opp)
        s_opp_suf = tuple(s_opp_suf)

        # 开始枚举MLP
        for last_level in syb_list:
            cand_cnt += 1

            s_mlp = list(opj[1])
            s_mlp.append(last_level)
            # print(s_opp)

            s_mlp_suf = s_mlp[1:]
            s_mlp = tuple(s_mlp)
            s_mlp_suf = tuple(s_mlp_suf)
            s_opj_suf = (s_opp_suf, s_mlp_suf)
            # print(s_opp_suf)

            # print(r, h)
            for opj_suf in FOP[-1]:
                if s_opj_suf == opj_suf:
                    s_opj = (s_opp, s_mlp)
                    # print(s_opj)
                    # 产生r或h
                    if opj[0][0] == s_opp_suf[-1]:
                        # 产生r
                        if s_opp[0] < s_opp[-1]:
                            occ_enum = cal_occ_r(len(s_opp), opj, s_opj_suf)
                        # 产生h
                        else:
                            occ_enum = cal_occ_h(len(s_opp), opj, s_opj_suf)
                        if len(occ_enum) >= min_sup:
                            new_FOP.append(s_opj)
                            new_occ_dic[s_opj] = occ_enum
                    else:
                        occ_enum = cal_occ_1(opj, s_opj_suf)
                        if len(occ_enum) >= min_sup:
                            new_FOP.append(s_opj)
                            new_occ_dic[s_opj] = occ_enum

        last_rank += 1


'''
计算只生成r的出现
'''


def cal_occ_1(prefix, suffix):
    global prefix_occ, suffix_occ
    cand_occ = prefix_occ[prefix] & suffix_occ[suffix]
    prefix_occ[prefix] -= cand_occ
    suffix_occ[suffix] -= cand_occ
    return cand_occ


'''
计算r
'''


def cal_occ_r(op_len, prefix, suffix):
    global prefix_occ, suffix_occ
    occ_r = set()
    cand_occ = prefix_occ[prefix] & suffix_occ[suffix]

    for occ in cand_occ:
        t_begin = T[occ - op_len + 1]
        t_end = T[occ]

        if t_begin == t_end:
            continue
        if t_begin < t_end:
            occ_r.add(occ)

    prefix_occ[prefix] -= occ_r
    suffix_occ[suffix] -= occ_r
    return occ_r


def cal_occ_h(op_len, prefix, suffix):
    global prefix_occ, suffix_occ
    occ_h = set()
    cand_occ = prefix_occ[prefix] & suffix_occ[suffix]

    for occ in cand_occ:
        t_begin = T[occ - op_len + 1]
        t_end = T[occ]
        if t_begin == t_end:
            continue
        if t_begin > t_end:
            occ_h.add(occ)

    prefix_occ[prefix] -= occ_h
    suffix_occ[suffix] -= occ_h
    return occ_h


def find_2():
    L_cnt = 0
    M_cnt = 0
    H_cnt = 0
    # 获取t_max-t_min
    # diff = np.diff(T)
    max_diff = max(T) - min(T)

    # print(max_diff)
    # max_diff = max(diff)

    # print(max_diff)

    # 波动等级映射，f是变化率
    def encode(f_r):
        f_r = abs(f_r)
        # print(f_r)
        if f_r <= ratio_l:
            return 'L'  # 变化最小
        elif f_r <= ratio_m:
            return 'M'  # 变化中等
        else:
            return 'H'  # 变化最大

    FOP.append(list())
    # 为长度为2的模式开辟空间
    for syb in syb_list:
        occ_dic[((1, 2), (syb,))] = set()
        occ_dic[((2, 1), (syb,))] = set()
    # 计算长度为2的出现位置
    for i in range(T_size - 1):
        delta = T[i + 1] - T[i]
        level_i = encode(delta / max_diff)
        # level_i = encode(delta / T[i])
        # print(delta / T[i])
        if level_i == 'L':
            L_cnt += 1
        elif level_i == 'M':
            M_cnt += 1
        else:
            H_cnt += 1

        # print(delta, delta / max_diff, level_i)
        # delta为差值, =0 不是出现; <0是(2,1); >0是(1,2)
        if delta == 0:
            continue
        elif delta > 0:
            occ_dic[((1, 2), (level_i,))].add(i + 1)
        else:
            occ_dic[((2, 1), (level_i,))].add(i + 1)

    print("L:", L_cnt)
    print("M:", M_cnt)
    print("H:", H_cnt)
    # 函数查找长度为2的频繁模式，并加入结果集
    for p in occ_dic:
        # print(p, occ_dic[p])
        if len(occ_dic[p]) >= min_sup:
            FOP[-1].append(p)
    # print(sorted(occ_dic[((1, 2), ('M',))]))
    # print(sorted(occ_dic[((2, 1), ('M',))]))


def find_m():
    global occ_dic, cand_cnt, cal_cnt
    opp_cnt = 0
    while FOP[-1]:
        # 增加长度为length的FOP结果集
        new_FOP = list()
        new_occ_dic = dict()
        # 用来存放p作为前缀和作为后缀的出现
        prefix_occ.clear()
        suffix_occ.clear()

        for p in FOP[-1]:
            # 前后缀出现，前缀提前+1
            prefix_occ[p] = {occ + 1 for occ in occ_dic[p]}
            suffix_occ[p] = occ_dic[p]
        occ_dic.clear()
        # 对前缀opp-mlp字典遍历其中的opp
        for opj in FOP[-1]:
            pattern_enum(opj, new_FOP, new_occ_dic)

        occ_dic = new_occ_dic
        FOP.append(new_FOP)
        # current, peak = tracemalloc.get_traced_memory()
        # print(f"Current memory usage is {current / 10 ** 6:.2f} MB; Peak was {peak / 10 ** 6:.2f} MB")
    print(opp_cnt)
    # print(fusion_time)
    # print(cal_time)


def FOP_miner():
    find_2()
    find_m()


def ratio_cal():
    diff = np.diff(T)
    max_diff = max(T) - min(T)
    flc = np.abs(diff / max_diff)
    return np.percentile(flc, q=33), np.percentile(flc, q=66)
    # return np.percentile(flc, q=70), np.percentile(flc, q=90)
    # return np.percentile(flc, q=20), np.percentile(flc, q=80)
    # return np.percentile(flc, q=10), np.percentile(flc, q=30)


# 时间序列
T = list()
T_size = 0
syb_list = ["L", "M", "H"]
FOP = list()
# 模式出现字典{(1,2):{2, 4, 6, 7}, (2,1):{....}...}
occ_dic = dict()
# 模式作为前缀的出现，已经加1
prefix_occ = dict()
# 模式作为后缀的出现
suffix_occ = dict()

ratio_l = 0.40
ratio_m = 0.80
# ratio_l = 0.06
# ratio_m = 0.15
min_sup = 100

# 候选模式计数
cand_cnt = 6
# 频繁模式计数
fre_cnt = 0

if __name__ == '__main__':
    # read_file("../datasets/Plant_1_Weather_Sensor_Data.txt")
    # read_file("../datasets/New_York_Air_Quality.txt")
    # read_file("../datasets/KURIAS-ECG_HeartRate.txt")
    # read_file("../datasets/Metro_Interstate_Traffic_Volume.txt")
    # read_file("../datasets/股票Russell2000（1987.9.10~2019.12.27）.txt")
    # read_file("../datasets/Nasdaq.txt")
    # read_file("../datasets/S&P500.txt")
    read_file("../datasets/NYSE.txt")

    ratio_l, ratio_m = ratio_cal()

    # 不同minsup的影
    # min_sup = 70
    # min_sup = 60
    # min_sup = 50
    # min_sup = 40
    # min_sup = 30
    # min_sup = 20

    # # 可扩展性实验
    # T_2 = []
    # min_sup = 0
    # for i in range(6):
    #     T_2.extend(T)
    #     min_sup += 20
    # T = T_2
    # T_size = len(T)
    # print(T_size)

    tracemalloc.start()
    starttime = time.time()
    FOP_miner()
    # mem = memory_usage((FOP_miner,), interval=0.001)
    # print("内存:", round(max(mem) - min(mem), 3), "MB")
    endtime = time.time()
    for l in FOP:
        fre_cnt += len(l)
        # print(len(l))

    print("候选数量：", cand_cnt, "频繁模式数量", fre_cnt)
    print("Running time: " + str(round(endtime * 1000 - starttime * 1000, 2)) + "ms")
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6:.3f} MB; Peak was {peak / 10 ** 6:.3f} MB")
