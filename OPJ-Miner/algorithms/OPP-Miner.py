import ctypes
import time
import tracemalloc

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
    p_opp = p
    q_opp = q

    # p fusion
    p_len = len(p_opp)
    # pq都是保序模式(1,2,3,4...), 用元组保存
    r = list()
    h = list()
    # 如果p1 = qm，r中p1<qm，h中p1>qm
    if p_opp[0] == q_opp[-1]:
        r = list(p_opp)
        r.append(q_opp[-1])
        h = list(p_opp)
        h.append(q_opp[-1])
        for i in range(1, p_len + 1):
            if r[i] > r[0]:
                r[i] += 1
            if h[i] > h[0]:
                h[i] += 1
        r[len(r) - 1] += 1
        h[0] += 1
    else:
        if p_opp[0] < q_opp[-1]:
            r.append(p_opp[0])
        else:
            r.append(p_opp[0] + 1)
        r.extend(list(q_opp))
        for i in range(1, p_len + 1):
            if r[i] >= r[0]:
                r[i] += 1
    r = tuple(r)
    h = tuple(h)
    if h:
        return r, h
    else:
        return r, ()


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
    aux_arr = gen_aux(pattern, sorted_pat, pattern_size)
    trans_pattern = transform(pattern)
    return SBNDM(trans_pattern, aux_arr)


def gen_aux(pattern, sorted_pat, length):
    aux = [0] * length
    for i in range(length):
        for j in range(length):
            if sorted_pat[i] == pattern[j]:
                aux[i] = j + 1
    return aux


# pat为转换后的pattern, 大小比原来少1, aux_arr为辅助数组，用来快速验证OPP出现
def SBNDM(pat, aux_arr):
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
                    if T[j - 1 + aux_arr[k]] >= T[j - 1 + aux_arr[k + 1]]:
                        f = 0
                        break
                if f:  # f>0等价于f为1
                    occ_cnt += 1
                    # occ_list.append(pos + pat_length)
                pos += 1  # 简化自增
        pos += pat_length - 1

    return occ_cnt


def find_2():
    occ_cnt_dic = dict()
    FOP.append(list())
    # 为长度为2的模式开辟空间
    occ_cnt_dic[(1, 2)] = 0
    occ_cnt_dic[(2, 1)] = 0
    # 计算长度为2的出现位置
    for i in range(T_size - 1):
        delta = T[i + 1] - T[i]

        # delta为差值, =0 不是出现; <0是(2,1); >0是(1,2)
        if delta == 0:
            continue
        elif delta > 0:
            occ_cnt_dic[(1, 2)] += 1
        else:
            occ_cnt_dic[(2, 1)] += 1

    # 函数查找长度为2的频繁模式，并加入结果集
    for p in occ_cnt_dic:
        # print(p, occ_dic[p])
        if occ_cnt_dic[p] >= min_sup:
            FOP[-1].append(p)


def find_m():
    global cand_cnt
    while FOP[-1]:
        # 增加长度为length的FOP结果集
        new_FOP = list()
        # 对前缀opp字典遍历其中的opp
        for p in FOP[-1]:
            # p的opp后缀
            op_suf = list(p[1:])
            for i in range(len(op_suf)):
                if op_suf[i] > p[0]:
                    op_suf[i] -= 1
            op_suf = tuple(op_suf)
            for q in FOP[-1]:
                # q的opp前缀
                op_pre = list(q[:-1])
                for i in range(len(op_pre)):
                    if op_pre[i] > q[-1]:
                        op_pre[i] -= 1
                op_pre = tuple(op_pre)
                # 检查是否可以融合
                if op_suf != op_pre:
                    continue
                # 这里一定可以融合
                r, h = JPFusion(p, q)
                if h:
                    cand_cnt += 2
                    occ_r = matching_opj(r, len(r))
                    occ_h = matching_opj(h, len(h))
                    if occ_r >= min_sup:
                        new_FOP.append(r)
                    if occ_h >= min_sup:
                        new_FOP.append(h)
                else:
                    cand_cnt += 1
                    occ_r = matching_opj(r, len(r))
                    if occ_r >= min_sup:
                        new_FOP.append(r)

        # print(new_FOP)
        FOP.append(new_FOP)
        # current, peak = tracemalloc.get_traced_memory()
        # print(f"Current memory usage is {current / 10 ** 6:.2f} MB; Peak was {peak / 10 ** 6:.2f} MB")

    # print(fusion_time)
    # print(cal_time)


def FOP_miner():
    global trans_T
    find_2()
    trans_T = transform(T)
    find_m()


# 时间序列
T = list()
trans_T = list()

T_size = 0
FOP = list()

min_sup = 10

cand_cnt = 2

if __name__ == '__main__':

    # read_file("../datasets/Plant_1_Weather_Sensor_Data.txt")
    # read_file("../datasets/New_York_Air_Quality.txt")
    # read_file("../datasets/KURIAS-ECG_HeartRate.txt")
    # read_file("../datasets/Metro_Interstate_Traffic_Volume.txt")
    # read_file("../datasets/股票Russell2000（1987.9.10~2019.12.27）.txt")
    # read_file("../datasets/Nasdaq.txt")
    read_file("../datasets/S&P500.txt")
    # read_file("../datasets/NYSE.txt")

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
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage is {current / 10 ** 6:.3f} MB; Peak was {peak / 10 ** 6:.3f} MB")
    count1 = 0
    for l in FOP:
        # print(len(l), l)
        for p in l:
            count1 += 1
    print("候选数量：", cand_cnt, "频繁模式数量", count1)
    print("Running time: " + str(round(endtime * 1000 - starttime * 1000, 2)) + "ms")
