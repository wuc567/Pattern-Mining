import copy
import time
import tracemalloc

import numpy as np
from memory_profiler import memory_usage


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


def JPFusion(p, q):
    p_opp = p[0]
    p_mlp = p[1]
    q_opp = q[0]
    q_mlp = q[1]

    # p join
    sup_mlp = list(p_mlp)
    sup_mlp.append(q_mlp[-1])
    sup_mlp = tuple(sup_mlp)

    # p fusion
    p_len = len(p_opp)
    r_opp = [0] * (p_len + 1)
    h_opp = list()
    # 如果p1 = qm，r中p1<qm，h中p1>qm
    if p_opp[0] == q_opp[-1]:
        r_opp[0] = p_opp[0]
        r_opp[-1] = p_opp[0] + 1
        for i in range(1, p_len):
            if p_opp[i] > p_opp[0]:
                r_opp[i] = p_opp[i] + 1
            else:
                r_opp[i] = p_opp[i]
        h_opp = list(r_opp)
        h_opp[0] += 1
        h_opp[-1] -= 1
    else:
        if p_opp[0] < q_opp[-1]:
            r_opp[-1] = q_opp[-1] + 1
        else:
            r_opp[-1] = q_opp[-1]

        for i in range(0, p_len):
            if p_opp[i] >= r_opp[-1]:
                r_opp[i] = p_opp[i] + 1
            else:
                r_opp[i] = p_opp[i]
    r_opp = tuple(r_opp)
    h_opp = tuple(h_opp)
    if h_opp:
        return (r_opp, sup_mlp), (h_opp, sup_mlp)
    else:
        return (r_opp, sup_mlp), ()


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

    FOP.append(list())
    # 为长度为2的模式开辟空间
    for syb in syb_list:
        occ_dic[((1, 2), (syb,))] = list()
        occ_dic[((2, 1), (syb,))] = list()
    # 计算长度为2的出现位置
    for i in range(T_size - 1):
        delta = T[i + 1] - T[i]
        level_i = encode(delta / max_diff)

        if level_i == 'L':
            L_cnt += 1
        elif level_i == 'M':
            M_cnt += 1
        else:
            H_cnt += 1

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
    global occ_dic, cand_cnt
    while FOP[-1]:
        # 增加长度为length的FOP结果集
        new_FOP = list()
        new_occ_dic = dict()

        # 用来存放p作为前缀和作为后缀的出现
        prefix_occ.clear()
        suffix_occ.clear()

        for p in FOP[-1]:
            # 值传递
            prefix_occ[p] = copy.copy(occ_dic[p])
            # 引用传递
            suffix_occ[p] = occ_dic[p]

        # 对前缀opp-mlp字典遍历其中的opp
        for p in FOP[-1]:
            # p的opp后缀
            op_suf = list(p[0][1:])
            for i in range(len(op_suf)):
                if op_suf[i] > p[0][0]:
                    op_suf[i] -= 1
            op_suf = tuple(op_suf)
            # p的mlp后缀
            mlp_suf = p[1][1:]
            for q in FOP[-1]:
                # 前缀集合大小小于minsup则break
                if len(prefix_occ[p]) < min_sup:
                    break
                # q的mlp前缀
                mlp_pre = q[1][:-1]
                # q的opp前缀
                op_pre = list(q[0][:-1])
                for i in range(len(op_pre)):
                    if op_pre[i] > q[0][-1]:
                        op_pre[i] -= 1
                op_pre = tuple(op_pre)
                # 检查是否可以联合融合
                if op_suf != op_pre or mlp_suf != mlp_pre:
                    continue

                # 后缀剪枝，要continue
                if len(suffix_occ[q]) < min_sup:
                    continue
                # 这里一定可以联合融合
                r, h = JPFusion(p, q)
                if h:
                    cand_cnt += 2
                    occ_r, occ_h = cal_occ_2(len(r[0]), p, q)
                    if len(occ_r) >= min_sup:
                        new_FOP.append(r)
                        new_occ_dic[r] = occ_r
                    if len(occ_h) >= min_sup:
                        new_FOP.append(h)
                        new_occ_dic[h] = occ_h
                else:
                    cand_cnt += 1
                    occ_r = cal_occ_1(p, q)
                    if len(occ_r) >= min_sup:
                        new_FOP.append(r)
                        new_occ_dic[r] = occ_r

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
    # return np.percentile(flc, q=33), np.percentile(flc, q=66)
    # return np.percentile(flc, q=70), np.percentile(flc, q=90)
    # return np.percentile(flc, q=20), np.percentile(flc, q=80)
    return np.percentile(flc, q=10), np.percentile(flc, q=30)


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

    ratio_l, ratio_m = ratio_cal()
    # tracemalloc.start()

    starttime = time.time()
    FOP_miner()
    # mem = memory_usage((FOP_miner,), interval=0.001)
    # print("内存:", round(max(mem) - min(mem), 3), "MB")
    endtime = time.time()

    # current, peak = tracemalloc.get_traced_memory()
    # print(f"Current memory usage is {current / 10 ** 6:.3f} MB; Peak was {peak / 10 ** 6:.3f} MB")

    count1 = 0
    for l in FOP:
        # print(len(l), l)
        for p in l:
            count1 += 1
    print("候选数量：", cand_cnt, "频繁模式数量", count1)
    print("Running time: " + str(round(endtime * 1000 - starttime * 1000, 2)) + "ms")
