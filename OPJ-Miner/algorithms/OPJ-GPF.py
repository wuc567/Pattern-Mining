import copy
import os
import time
import tracemalloc

import numpy as np
from scipy.stats import laplace, norm


def read_file(file_name):
    global T, T_size
    with open(file_name, 'r') as file:
        # T.append(0)  # 确保出现位置与列表下标一致
        for line in file:
            if line.strip() == "":
                break
            T.extend([float(x) for x in line.split(" ") if x])
        # T_size = len(T) - 1
        T_size = len(T)


def PFusion(p, q):
    p_len = len(p)
    # pq都是保序模式(1,2,3,4...), 用元组保存
    r = [0] * (p_len + 1)
    h = list()
    # 如果p1 = qm，r中p1<qm，h中p1>qm
    if p[0] == q[-1]:
        r[0] = p[0]
        r[-1] = p[0] + 1
        for i in range(1, p_len):
            if p[i] > p[0]:
                r[i] = p[i] + 1
            else:
                r[i] = p[i]
        h = list(r)
        h[0] += 1
        h[-1] -= 1
    else:
        if p[0] < q[-1]:
            r[-1] = q[-1] + 1
        else:
            r[-1] = q[-1]

        for i in range(0, p_len):
            if p[i] >= r[-1]:
                r[i] = p[i] + 1
            else:
                r[i] = p[i]

    r = tuple(r)
    h = tuple(h)
    if h == ():
        # print(p, q, r, h)
        if len(set(r)) < len(r):
            print("error:")
            print(p, q, r, h)
    return r, h


# 若传入h_opp为空，则代表只生成一个super-OPP r
def mlp_join(r_opp, h_opp, s_opp_prf, s_opp_suf, new_FOP, new_occ_dic):
    global cand_cnt
    # 拿到超模式opp的前缀opp_prf对应的频繁mlp集合
    mlp_prf_list = OPJ_dic[s_opp_prf]
    # 拿到超模式opp的后缀opp_suf对应的频繁mlp集合
    mlp_suf_list = OPJ_dic[s_opp_suf]
    # 检查所有可能
    for mlp_prf in mlp_prf_list:
        for mlp_suf in mlp_suf_list:
            # print(r_opp, (s_opp_prf, mlp_prf), (s_opp_suf, mlp_suf))
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
    cand_occ = prefix_occ[prefix] & suffix_occ[suffix]
    prefix_occ[prefix] -= cand_occ
    suffix_occ[suffix] -= cand_occ
    return cand_occ


'''
同时计算生成r和h的出现
'''


def cal_occ_2(r_len, prefix, suffix):
    global prefix_occ, suffix_occ
    occ_r = set()
    occ_h = set()
    cand_occ = prefix_occ[prefix] & suffix_occ[suffix]

    for occ in cand_occ:
        t_begin = T[occ - r_len + 1]
        t_end = T[occ]
        if t_begin == t_end:
            continue
        if t_begin < t_end:
            occ_r.add(occ)
        else:
            occ_h.add(occ)

    prefix_occ[prefix] -= cand_occ
    suffix_occ[suffix] -= cand_occ
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
        occ_dic[((1, 2), (syb,))] = set()
        occ_dic[((2, 1), (syb,))] = set()
    # 计算长度为2的出现位置
    for i in range(T_size - 1):
        delta = T[i + 1] - T[i]
        level_i = encode(delta / max_diff)
        # level_i = encode(delta / T[i])

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


def find_3():
    global occ_dic, OPJ_dic, cand_cnt, cal_cnt

    # 增加长度为length的FOP结果集
    new_FOP = list()
    new_occ_dic = dict()
    # 先形成前后缀的OPJ_dic，即opp-mlp表
    for p in FOP[-1]:
        OPJ_dic[p[0]] = list()
    for p in FOP[-1]:
        # 将mlp插入到opp键对应集合
        OPJ_dic[p[0]].append(p[1])
        # 前后缀出现，前缀提前+1
        prefix_occ[p] = {occ + 1 for occ in occ_dic[p]}
        suffix_occ[p] = occ_dic[p]
    # 对前缀opp-mlp字典遍历其中的opp
    for p in OPJ_dic:
        for q in OPJ_dic:
            # pq都是长度为2的模式，一定可以融合
            r_opp, h_opp = PFusion(p, q)
            if p == (1, 2) and q == (1, 2):
                group_dic[r_opp] = 1
            elif p == (1, 2) and q == (2, 1):
                group_dic[r_opp] = 2
                group_dic[h_opp] = 2
            elif p == (2, 1) and q == (1, 2):
                group_dic[r_opp] = 3
                group_dic[h_opp] = 3
            else:
                group_dic[r_opp] = 4

            # print(r_opp, h_opp)
            mlp_join(r_opp, h_opp, p, q, new_FOP, new_occ_dic)
    occ_dic = new_occ_dic
    # print(new_occ_dic)
    FOP.append(new_FOP)
    # current, peak = tracemalloc.get_traced_memory()
    # print(f"Current memory usage is {current / 10 ** 6:.2f} MB; Peak was {peak / 10 ** 6:.2f} MB")

    # print(fusion_time)
    # print(cal_time)


def find_m():
    global occ_dic, group_dic, OPJ_dic, cand_cnt, cal_cnt
    while FOP[-1]:
        # 增加长度为length的FOP结果集
        new_FOP = list()
        new_occ_dic = dict()
        new_group_dic = dict()
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
            # 前后缀出现，前缀提前+1
            prefix_occ[p] = {occ + 1 for occ in occ_dic[p]}
            suffix_occ[p] = occ_dic[p]

        # group 12放在一起，group34放在一起
        G1 = []
        G2 = []
        for p in OPJ_dic:
            if group_dic[p] == 1 or group_dic[p] == 2:
                G1.append(p)
            else:
                G2.append(p)

        # 对前缀opp-mlp字典遍历其中的opp
        for p in OPJ_dic:
            # 取前缀
            op_suf = list(p[1:])
            for i in range(len(op_suf)):
                if op_suf[i] > p[0]:
                    op_suf[i] -= 1
            op_suf = tuple(op_suf)
            # 13只能和G1融合，24只能和G2融合
            if group_dic[p] == 1 or group_dic[p] == 3:
                suffix_list = G1
            else:
                suffix_list = G2
            for q in suffix_list:
                # q的opp前缀
                op_pre = list(q[:-1])
                for i in range(len(op_pre)):
                    if op_pre[i] > q[-1]:
                        op_pre[i] -= 1
                op_pre = tuple(op_pre)
                if op_suf != op_pre:
                    continue
                # 这里一定可以融合
                r_opp, h_opp = PFusion(p, q)
                new_group_dic[r_opp] = group_dic[p]
                if h_opp:
                    new_group_dic[h_opp] = group_dic[p]
                mlp_join(r_opp, h_opp, p, q, new_FOP, new_occ_dic)

        occ_dic = new_occ_dic
        group_dic = new_group_dic
        # print(new_FOP)
        FOP.append(new_FOP)
        # current, peak = tracemalloc.get_traced_memory()
        # print(f"Current memory usage is {current / 10 ** 6:.2f} MB; Peak was {peak / 10 ** 6:.2f} MB")

    # print(fusion_time)
    # print(cal_time)


def FOP_miner():
    find_2()
    find_3()
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
# 保存频繁OPJ，不区分前后缀，OP对应的ALP{(1,2):[(L),(M),(H)], (2,1):[(L),(M),(H)],...}
OPJ_dic = dict()
# 模式出现字典{(1,2):{2, 4, 6, 7}, (2,1):{....}...}
occ_dic = dict()
# 存放opp模式对应的分组
group_dic = dict()
# 模式作为前缀的出现，已经加1
prefix_occ = dict()
# 模式作为后缀的出现
suffix_occ = dict()

ratio_l = 0.01
ratio_m = 0.30
min_sup = 100

cand_cnt = 6

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
    endtime = time.time()
    count1 = 0
    for l in FOP:
        # print(len(l), l)
        for p in l:
            count1 += 1
    print("候选数量：", cand_cnt, "频繁模式数量", count1)
    print("Running time: " + str(round(endtime * 1000 - starttime * 1000, 2)) + "ms")
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6:.3f} MB; Peak was {peak / 10 ** 6:.3f} MB")
