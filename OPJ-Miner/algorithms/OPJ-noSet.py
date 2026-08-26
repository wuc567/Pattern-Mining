import copy
import os
import sys
import time
import tracemalloc

import numpy as np


def read_file(file_name):
    global T, T_size
    with open(file_name, 'r') as file:
        # 出现位置比列表下标大1
        content = file.read().strip()  # 去除首尾空白字符（如换行、空格）
        if not content:  # 处理空文件
            return []
        T = [float(x) for x in content.split(' ') if x]
        T_size = len(T)


def enum_and_check_opp(opp, new_FOP, new_occ_dic):
    global cand_cal_cnt
    # op是OPJ中的保序部分((1,2),(L))中的(1,2)
    op_len = len(opp)
    # 枚举保序的最后一个位置，从1开始
    last_rank = 1
    # 最后一位从i=1开始枚举
    while last_rank <= op_len + 1:
        # cand_cal_cnt += 1
        # s_op是op的超模式，其的前缀是op本身
        s_opp = list(opp)
        # 末尾添加枚举的位置
        s_opp.append(last_rank)
        # 调整末尾前面的元素秩序，让超模式满足op定义
        for j in range(op_len):
            if s_opp[j] >= last_rank:
                s_opp[j] += 1
        # print(s_opp)
        # 获取超模式的后缀，并使其满足保序定义
        s_opp_suf = s_opp[1:]
        for j in range(op_len):
            if s_opp_suf[j] > s_opp[0]:
                s_opp_suf[j] -= 1
        s_opp = tuple(s_opp)
        s_opp_suf = tuple(s_opp_suf)
        # print(s_opp_suf)
        # 无论后缀是否频繁，提前判断保序生成rh还是r，枚举从1开始枚举，优先产生h，实际上r在下一次枚举产生，直接跳过即可
        r_opp = ()
        h_opp = ()
        if opp[0] == s_opp_suf[-1]:
            last_rank += 2
            # 1开始枚举优先h
            h_opp = s_opp
            r_opp = list(h_opp)
            r_opp[0], r_opp[-1] = r_opp[-1], r_opp[0]
            r_opp = tuple(r_opp)
        else:
            # 如果不产生两个opp，r_opp就是s_opp
            last_rank += 1
            r_opp = s_opp
        # 判断后缀保序是不是频繁的，即在不在字典中
        if s_opp_suf in OPJ_dic:
            # 进入mlp枚举，比如前缀(1,2):{L,M,H},last_rank=1,超模式为(2,3,1),后缀为(2,1)
            # 由于(2,1):{L,M},此时开始检查(2,3,1):{LL,LM,ML,...}
            mlp_join(r_opp, h_opp, opp, s_opp_suf, new_FOP, new_occ_dic)


# 若传入h_opp为空，则代表只生成一个super-OPP r
def mlp_join(r_opp, h_opp, s_opp_prf, s_opp_suf, new_FOP, new_occ_dic):
    global cand_cnt
    # 拿到超模式opp的前缀opp_prf对应的频繁mlp集合
    mlp_prf_list = OPJ_dic[s_opp_prf]
    # 拿到超模式opp的后缀opp_suf对应的频繁mlp集合
    mlp_suf_list = OPJ_dic[s_opp_suf]
    # 检查所有可能
    for index, mlp_prf in enumerate(mlp_prf_list):
        for mlp_suf in mlp_suf_list:
            # 前缀剪枝，跳出内循环，不再检查后面的后缀mlp
            if len(prefix_occ[(s_opp_prf, mlp_prf)]) < min_sup:
                # print("前缀prune", s_opp, (s_opp_prf, mlp_prf))
                break
            # 后缀剪枝，检查下一个后缀mlp
            if len(suffix_occ[(s_opp_suf, mlp_suf)]) < min_sup:
                # print("后缀prune", s_opp, (s_opp_suf, mlp_suf))
                continue

            if mlp_prf[1:] == mlp_suf[:-1]:
                s_mlp = list(mlp_prf)
                s_mlp.append(mlp_suf[-1])
                s_mlp = tuple(s_mlp)
                if h_opp:
                    cand_cnt += 2
                    occ_r, occ_h = cal_occ_2(len(r_opp), (s_opp_prf, mlp_prf), (s_opp_suf, mlp_suf))
                    # 枚举先产生r
                    r = (r_opp, s_mlp)
                    h = (h_opp, s_mlp)
                    # print(r, occ_r)
                    # print(h, occ_h)
                    # print("rh")
                    # 判断rh是否频繁
                    if len(occ_r) >= min_sup:
                        new_FOP.append(r)
                        new_occ_dic[r] = occ_r
                    if len(occ_h) >= min_sup:
                        new_FOP.append(h)
                        new_occ_dic[h] = occ_h
                else:
                    cand_cnt += 1
                    r = (r_opp, s_mlp)
                    # print(r)
                    occ_r = cal_occ_1((s_opp_prf, mlp_prf), (s_opp_suf, mlp_suf))
                    # print(r, occ_r)
                    # print("r")

                    if len(occ_r) >= min_sup:
                        new_FOP.append(r)
                        new_occ_dic[r] = occ_r


'''
计算只生成r的出现
'''


def cal_occ_1(prefix, suffix):
    global prefix_occ, suffix_occ
    p_occ_list = prefix_occ[prefix]
    q_occ_list = suffix_occ[suffix]
    # 收集未匹配的元素，避免遍历过程中删除元素，列表删除元素效率极低
    unused_p_occ = []
    unused_q_occ = []
    occ_r = []
    i = 0
    j = 0
    while i < len(p_occ_list) and j < len(q_occ_list):
        p_occ = p_occ_list[i]
        q_occ = q_occ_list[j]
        if q_occ > p_occ:
            if p_occ + 1 == q_occ:
                occ_r.append(q_occ)
                i += 1
                j += 1
            else:
                unused_p_occ.append(p_occ)
                i += 1
        else:
            j += 1
            unused_q_occ.append(q_occ)

    # 处理剩余未遍历的元素（补全收集）
    # p列表剩余元素全部未匹配
    unused_p_occ.extend(p_occ_list[i:])
    # q列表剩余元素全部未匹配
    unused_q_occ.extend(q_occ_list[j:])
    prefix_occ[prefix] = unused_p_occ
    suffix_occ[suffix] = unused_q_occ
    return occ_r


'''
同时计算生成r和h的出现
'''


def cal_occ_2(r_len, prefix, suffix):
    global prefix_occ, suffix_occ
    occ_r = []
    occ_h = []
    p_occ_list = prefix_occ[prefix]
    q_occ_list = suffix_occ[suffix]
    # 收集未匹配的元素，避免遍历过程中删除元素，列表删除元素效率极低
    unused_p_occ = []
    unused_q_occ = []
    i = 0
    j = 0
    while i < len(p_occ_list) and j < len(q_occ_list):
        p_occ = p_occ_list[i]
        q_occ = q_occ_list[j]
        if q_occ > p_occ:
            if p_occ + 1 == q_occ:
                t_begin = T[q_occ - r_len + 1]
                t_end = T[q_occ]
                if t_begin < t_end:
                    occ_r.append(q_occ)
                elif t_begin > t_end:
                    occ_h.append(q_occ)
                i += 1
                j += 1
            else:
                i += 1
                unused_p_occ.append(p_occ)
        else:
            j += 1
            unused_q_occ.append(q_occ)
    # 处理剩余未遍历的元素（补全收集）
    # p列表剩余元素全部未匹配
    unused_p_occ.extend(p_occ_list[i:])
    # q列表剩余元素全部未匹配
    unused_q_occ.extend(q_occ_list[j:])
    prefix_occ[prefix] = unused_p_occ
    suffix_occ[suffix] = unused_q_occ

    return occ_r, occ_h


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
        occ_dic[((1, 2), (syb,))] = list()
        occ_dic[((2, 1), (syb,))] = list()
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
            occ_dic[((1, 2), (level_i,))].append(i + 1)
        else:
            occ_dic[((2, 1), (level_i,))].append(i + 1)

    print("L:", L_cnt)
    print("M:", M_cnt)
    print("H:", H_cnt)
    # 函数查找长度为2的频繁模式，并加入结果集
    for p in occ_dic:
        # print(p, occ_dic[p])
        if len(occ_dic[p]) >= min_sup:
            FOP[-1].append(p)


def find_m():
    global occ_dic, OPJ_dic, cand_cnt, cal_cnt
    while FOP[-1]:
        # 增加长度为length的FOP结果集
        new_FOP = list()
        new_occ_dic = dict()
        # 清空OPJ_dic
        OPJ_dic.clear()
        # 用来存放p作为前缀和作为后缀的出现
        prefix_occ.clear()
        suffix_occ.clear()
        # 先形成前后缀的OPJ_dic，即opp-mlp表
        for p in FOP[-1]:
            OPJ_dic[p[0]] = list()
        for p in FOP[-1]:
            # 将mlp插入到opp键对应集合
            OPJ_dic[p[0]].append(p[1])
            # 前后缀出现
            # 值传递
            prefix_occ[p] = copy.copy(occ_dic[p])
            # 引用传递
            suffix_occ[p] = occ_dic[p]
        # 对前缀opp-mlp字典遍历其中的opp
        for opp in OPJ_dic:
            enum_and_check_opp(opp, new_FOP, new_occ_dic)

        occ_dic = new_occ_dic

        # print(new_occ_dic)
        FOP.append(new_FOP)
        # current, peak = tracemalloc.get_traced_memory()
        # print(f"Current memory usage is {current / 10 ** 6:.2f} MB; Peak was {peak / 10 ** 6:.2f} MB")

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
# 保存频繁OPJ，不区分前后缀，OP对应的ALP{(1,2):{(L),(M),(H)}, (2,1):{(L),(M),(H)},...}
OPJ_dic = dict()
# 模式出现字典{(1,2):{2, 4, 6, 7}, (2,1):{....}...}
occ_dic = dict()
# 模式作为前缀的出现，已经加1
prefix_occ = dict()
# 模式作为后缀的出现
suffix_occ = dict()

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
    read_file("../datasets/Metro_Interstate_Traffic_Volume.txt")
    # read_file("../datasets/股票Russell2000（1987.9.10~2019.12.27）.txt")
    # read_file("../datasets/Nasdaq.txt")
    # read_file("../datasets/S&P500.txt")
    # read_file("../datasets/NYSE.txt")

    ratio_l, ratio_m = ratio_cal()

    # 不同minsup的影
    # min_sup = 70
    # min_sup = 60
    # min_sup = 50
    # min_sup = 40
    # min_sup = 30
    # min_sup = 20

    # 可扩展性实验
    T_2 = []
    min_sup = 0
    for i in range(1):
        T_2.extend(T)
        min_sup += 20
    T = T_2
    T_size = len(T)
    print(T_size)

    tracemalloc.start()
    # print(T_size)
    starttime = time.time()
    FOP_miner()
    endtime = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6:.3f} MB; Peak was {peak / 10 ** 6:.3f} MB")
    for l in FOP:
        # print(len(l), l)
        for p in l:
            fre_cnt += 1
    print("候选数量：", cand_cnt, "频繁模式数量", fre_cnt)
    print("Running time: " + str(round(endtime * 1000 - starttime * 1000, 2)) + "ms")
