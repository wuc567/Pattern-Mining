import copy
import ctypes
import os
import time
import tracemalloc

import numpy as np
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


def enum_and_check_opp(opp, new_FOP):
    global cand_cal_cnt
    # op是OPJ中的保序部分((1,2),(L))中的(1,2)
    op_len = len(opp)
    # 枚举保序的最后一个位置，从1开始
    last_rank = 1
    # 最后一位从i=1开始枚举
    while last_rank <= op_len + 1:
        # cand_cal_cnt += 1
        # s_op是op的超模式，其的前缀是op本身
        enum_opp = list(opp)
        # 末尾添加枚举的位置
        enum_opp.append(last_rank)
        # 调整末尾前面的元素秩序，让超模式满足op定义
        for j in range(op_len):
            if enum_opp[j] >= last_rank:
                enum_opp[j] += 1
        # print(enum_opp)
        # 获取超模式的后缀，并使其满足保序定义
        s_opp_suf = enum_opp[1:]
        for j in range(op_len):
            if s_opp_suf[j] > enum_opp[0]:
                s_opp_suf[j] -= 1
        enum_opp = tuple(enum_opp)
        s_opp_suf = tuple(s_opp_suf)
        # print(s_opp_suf)

        # 判断后缀保序是不是频繁的，即在不在字典中
        if s_opp_suf in OPJ_dic:
            # print(s_opp_suf)
            # 进入mlp枚举，比如前缀(1,2):{L,M,H},last_rank=1,超模式为(2,3,1),后缀为(2,1)
            # 由于(2,1):{L,M},此时开始检查(2,3,1):{LL,LM,ML,...}

            # 判断保序生成rh还是r，枚举从1开始枚举，优先产生h，实际上r在下一次枚举产生，直接跳过即可
            r_opp = ()
            h_opp = ()
            if last_rank == opp[0]:
                # 1开始枚举优先h
                h_opp = enum_opp
                r_opp = list(h_opp)
                r_opp[0], r_opp[-1] = r_opp[-1], r_opp[0]
                r_opp = tuple(r_opp)
                # print(r_opp, h_opp)
            else:
                # 如果不产生两个opp，r_opp就是s_opp
                r_opp = enum_opp

            mlp_join(r_opp, h_opp, opp, s_opp_suf, new_FOP)

        if last_rank == opp[0]:
            last_rank += 2
        else:
            last_rank += 1


# 若传入h_opp为空，则代表只生成一个super-OPP r
def mlp_join(r_opp, h_opp, s_opp_prf, s_opp_suf, new_FOP):
    global cand_cnt
    # 拿到超模式opp的前缀opp_prf对应的频繁mlp集合
    mlp_prf_list = OPJ_dic[s_opp_prf]
    # 拿到超模式opp的后缀opp_suf对应的频繁mlp集合
    mlp_suf_list = OPJ_dic[s_opp_suf]
    for mlp_prf in mlp_prf_list:
        for mlp_suf in mlp_suf_list:
            if mlp_prf[1:] == mlp_suf[:-1]:
                s_mlp = list(mlp_prf)
                s_mlp.append(mlp_suf[-1])
                s_mlp = tuple(s_mlp)
                if h_opp:
                    cand_cnt += 2
                    # 枚举先产生h
                    r = (r_opp, s_mlp)
                    h = (h_opp, s_mlp)
                    occ_r_cnt = matching_opj(r, len(r_opp))
                    occ_h_cnt = matching_opj(h, len(h_opp))
                    # 判断rh是否频繁
                    if occ_r_cnt >= min_sup:
                        new_FOP.append(r)
                        # print(r, len(occ_r))
                    if occ_h_cnt >= min_sup:
                        new_FOP.append(h)
                        # print(h, len(occ_h))
                else:
                    cand_cnt += 1
                    r = (r_opp, s_mlp)
                    occ_r_cnt = matching_opj(r, len(r_opp))

                    if occ_r_cnt >= min_sup:
                        new_FOP.append(r)


# def verify(opp_occ_list, opj, aux_arr):
#     print(opj)
#     print(aux_arr)
#     pat_length = len(opj[0])
#     occ_cnt = 0
#     for occ in opp_occ_list:
#         j = occ - pat_length
#         flag = 1
#         for i in range(0, pat_length):
#             if T[occ - 1 + aux_arr[i]] >= T[occ - 1 + aux_arr[i + 1]] or level_seq[occ - 1] != opj[1][i]:
#                 break
#             else:
#                 flag = 1
#         if flag:
#             occ_cnt += 1
#     return occ_cnt


def transform(txt):
    txt_len = len(txt)
    trans_txt = [0] * (txt_len - 1)
    for i in range(txt_len - 1):
        if txt[i] < txt[i + 1]:
            trans_txt[i] = 49
        else:
            trans_txt[i] = 48
    return trans_txt


def matching_opj(pattern, pattern_size):
    sorted_pat = [i for i in range(1, pattern_size + 1)]
    aux_arr = gen_aux(pattern[0], sorted_pat, pattern_size)
    trans_pattern = transform(pattern[0])
    return SBNDM(trans_pattern, aux_arr, pattern[1])


def gen_aux(pattern, sorted_pat, length):
    aux = [0] * length
    for i in range(length):
        for j in range(length):
            if sorted_pat[i] == pattern[j]:
                aux[i] = j + 1
    return aux


# pat为转换后的pattern, 大小比原来少1, aux_arr为辅助数组，用来快速验证OPP出现
def SBNDM(pat, aux_arr, mlp):
    # occ_list = []
    occ_cnt = 0
    B = [0] * 256
    txt_length = len(trans_T)
    pat_length = len(pat)
    for j in range(pat_length):
        B[int(pat[j])] = ctypes.c_uint32(B[int(pat[j])]).value | (1 << (pat_length - j - 1))
    pos = pat_length - 1
    while pos <= txt_length - 1:
        D = (B[trans_T[pos - 1]]) & (B[trans_T[pos]] << 1)
        if D != 0:
            j = pos - pat_length + 1
            while True:
                pos = pos - 1
                if pos == 0:
                    D = 0
                else:
                    D = (D << 1) & B[trans_T[pos - 1]]
                if D == 0:
                    break
            if j == pos:
                f = 1  # 先假设满足条件
                for k in range(pat_length):
                    # 用j直接替代cand，简化索引计算
                    if T[j - 1 + aux_arr[k]] >= T[j - 1 + aux_arr[k + 1]] or mlp[k] != level_seq[pos + k]:
                        f = 0
                        break
                if f:  # f>0等价于f为1
                    occ_cnt += 1
                    # occ_list.append(pos + pat_length)
                pos += 1  # 简化自增
        pos += pat_length - 1

    return occ_cnt


def find_2():
    global level_seq
    L_cnt = 0
    M_cnt = 0
    H_cnt = 0
    # 获取t_max-t_min
    max_diff = max(T) - min(T)

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

    occ_cnt_dic = dict()
    FOP.append(list())
    # 为长度为2的模式开辟空间
    for syb in syb_list:
        occ_cnt_dic[((1, 2), (syb,))] = 0
        occ_cnt_dic[((2, 1), (syb,))] = 0
    # 计算长度为2的出现位置
    for i in range(T_size - 1):
        delta = T[i + 1] - T[i]
        level_i = encode(delta / max_diff)
        level_seq += level_i
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
            occ_cnt_dic[((1, 2), (level_i,))] += 1
        else:
            occ_cnt_dic[((2, 1), (level_i,))] += 1

    print("L:", L_cnt)
    print("M:", M_cnt)
    print("H:", H_cnt)
    # 函数查找长度为2的频繁模式，并加入结果集
    for p in occ_cnt_dic:
        # print(p, occ_dic[p])
        if occ_cnt_dic[p] >= min_sup:
            FOP[-1].append(p)


def find_m():
    global OPJ_dic
    opp_cnt = 0
    while FOP[-1]:
        # 增加长度为length的FOP结果集
        new_FOP = list()
        # 清空OPJ_dic
        OPJ_dic.clear()

        # 先形成前后缀的OPJ_dic，即opp-mlp表
        for p in FOP[-1]:
            OPJ_dic[p[0]] = list()
        for p in FOP[-1]:
            # 将mlp插入到opp键对应集合
            OPJ_dic[p[0]].append(p[1])

        # print(OPJ_dic)
        # 对前缀opp-mlp字典遍历其中的opp
        opp_cnt += len(OPJ_dic)
        for opp in OPJ_dic:
            enum_and_check_opp(opp, new_FOP)

        print(new_FOP)
        # print(new_occ_dic)
        FOP.append(new_FOP)
        # current, peak = tracemalloc.get_traced_memory()
        # print(f"Current memory usage is {current / 10 ** 6:.2f} MB; Peak was {peak / 10 ** 6:.2f} MB")
    print(opp_cnt)
    # print(fusion_time)
    # print(cal_time)


def FOP_miner():
    global trans_T
    find_2()
    trans_T = transform(T)
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
trans_T = list()
# 存放相邻两点的level列表，便于从opp出现过滤出opj的出现
level_seq = ""
syb_list = ["L", "M", "H"]
FOP = list()
# 保存频繁OPJ，不区分前后缀，OP对应的ALP{(1,2):{(L),(M),(H)}, (2,1):{(L),(M),(H)},...}
OPJ_dic = dict()

ratio_l = 0.01
ratio_m = 0.30
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

    # tracemalloc.start()
    starttime = time.time()
    # FOP_miner()
    endtime = time.time()
    for l in FOP:
        fre_cnt += len(l)
    print("候选数量：", cand_cnt, "频繁模式数量", fre_cnt)
    print("Running time: " + str(round(endtime * 1000 - starttime * 1000, 2)) + "ms")
    # current, peak = tracemalloc.get_traced_memory()
    # print(f"Current memory usage is {current / 10 ** 6:.3f} MB; Peak was {peak / 10 ** 6:.3f} MB")
