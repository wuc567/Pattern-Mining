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

        # 判断后缀保序是不是频繁的，即在不在字典中
        if s_opp_suf in OPJ_dic:
            # 进入mlp枚举，比如前缀(1,2):{L,M,H},last_rank=1,超模式为(2,3,1),后缀为(2,1)
            # 由于(2,1):{L,M},此时开始检查(2,3,1):{LL,LM,ML,...}

            # 判断保序生成rh还是r，枚举从1开始枚举，优先产生h，实际上r在下一次枚举产生，直接跳过即可
            r_opp = ()
            h_opp = ()
            if last_rank == opp[0]:
                # 1开始枚举优先h
                h_opp = s_opp
                r_opp = list(h_opp)
                r_opp[0], r_opp[-1] = r_opp[-1], r_opp[0]
                r_opp = tuple(r_opp)
            else:
                # 如果不产生两个opp，r_opp就是s_opp
                r_opp = s_opp

            mlp_join(r_opp, h_opp, opp, s_opp_suf, new_FOP, new_occ_dic)

        if last_rank == opp[0]:
            last_rank += 2
        else:
            last_rank += 1


# 若传入h_opp为空，则代表只生成一个super-OPP r
def mlp_join(r_opp, h_opp, s_opp_prf, s_opp_suf, new_FOP, new_occ_dic):
    global cand_cnt
    # 拿到超模式opp的前缀opp_prf对应的频繁mlp集合
    mlp_prf_list = OPJ_dic[s_opp_prf]
    # 拿到超模式opp的后缀opp_suf对应的频繁mlp集合
    mlp_suf_list = OPJ_dic[s_opp_suf]
    # 检查所有可能
    for mlp_prf in mlp_prf_list:
        prefix_pattern = (s_opp_prf, mlp_prf)
        for mlp_suf in mlp_suf_list:
            if mlp_prf[1:] == mlp_suf[:-1]:
                suffix_pattern = (s_opp_suf, mlp_suf)
                # 前缀剪枝，跳出内循环，不再检查后面的后缀mlp
                if len(prefix_occ[prefix_pattern]) < min_sup:
                    # print("前缀prune", s_opp, (s_opp_prf, mlp_prf))
                    continue
                # 后缀剪枝，检查下一个后缀mlp
                if len(suffix_occ[suffix_pattern]) < min_sup:
                    # print("后缀prune", s_opp, (s_opp_suf, mlp_suf))
                    continue
                s_mlp = list(mlp_prf)
                s_mlp.append(mlp_suf[-1])
                s_mlp = tuple(s_mlp)
                if h_opp:
                    cand_cnt += 2
                    occ_r, occ_h = cal_occ_2(len(r_opp), prefix_pattern, suffix_pattern)
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
                        # print(r, len(occ_r))
                    if len(occ_h) >= min_sup:
                        new_FOP.append(h)
                        new_occ_dic[h] = occ_h
                        # print(h, len(occ_h))
                else:
                    cand_cnt += 1
                    r = (r_opp, s_mlp)
                    occ_r = cal_occ_1(prefix_pattern, suffix_pattern)
                    # if r == ((1,2,3),('L', 'L')):
                    #     print(len(occ_r), sorted(occ_r))
                    # print("r")

                    if len(occ_r) >= min_sup:
                        new_FOP.append(r)
                        new_occ_dic[r] = occ_r
                        # print(r, len(occ_r))


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
    level_cnt = {syb: 0 for syb in syb_list}
    # 获取t_max-t_min
    max_diff = max(T) - min(T)

    # print(max_diff)
    # max_diff = max(diff)

    # print(max_diff)

    # 波动等级映射，f是变化率
    def encode(f_r):
        f_r = abs(f_r)
        # print(f_r)
        for i, threshold in enumerate(ratio):
            if f_r <= threshold:
                return syb_list[i]
        return syb_list[-1]

    FOP.append(list())
    # 为长度为2的模式开辟空间
    for syb in syb_list:
        occ_dic[((1, 2), (syb,))] = set()
        occ_dic[((2, 1), (syb,))] = set()
    a = time.time()
    # 计算长度为2的出现位置
    for i in range(T_size - 1):
        delta = T[i + 1] - T[i]
        level_i = encode(delta / max_diff)
        # level_i = encode(delta / T[i])
        # print(delta / T[i])
        level_cnt[level_i] += 1

        # print(delta, delta / max_diff, level_i)
        # delta为差值, =0 不是出现; <0是(2,1); >0是(1,2)
        if delta == 0:
            continue
        elif delta > 0:
            occ_dic[((1, 2), (level_i,))].add(i + 1)
        else:
            occ_dic[((2, 1), (level_i,))].add(i + 1)

    # 长度为2的模式扫描与编码所用时间，该时间包含在总运行时间中
    # print(time.time() - a)
    # 输出原始强度等级序列中各等级的出现次数
    for syb in syb_list:
        print(syb + ":", level_cnt[syb])
    # print(occ_dic.keys())
    # 函数查找长度为2的频繁模式，并加入结果集
    for p in occ_dic:
        # print(p, occ_dic[p])
        if len(occ_dic[p]) >= min_sup:
            FOP[-1].append(p)
    # print(sorted(occ_dic[((1, 2), ('M',))]))
    # print(sorted(occ_dic[((2, 1), ('M',))]))


def find_m():
    global occ_dic, OPJ_dic, cand_cnt
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
            # 前后缀出现，前缀提前+1
            prefix_occ[p] = {occ + 1 for occ in occ_dic[p]}
            suffix_occ[p] = occ_dic[p]

        # 对前缀opp-mlp字典遍历其中的opp
        # opp_cnt += len(OPJ_dic)
        # for opp in OPJ_dic:
        #     if len(opp) >= 5 and len(OPJ_dic[opp]) >= 2:
        #         print(opp, OPJ_dic[opp])
        # key = (1, 3, 2, 5, 4)
        # if key in OPJ_dic.keys():
        #     for mlp in OPJ_dic[key]:
        #         print(key, mlp)

        for opp in OPJ_dic:
            enum_and_check_opp(opp, new_FOP, new_occ_dic)
            # 释放opp内存
            for mlp in OPJ_dic[opp]:
                del occ_dic[(opp, mlp)]

        occ_dic = new_occ_dic
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
    quantiles = [int(100 * i / len(syb_list)) for i in range(1, len(syb_list))]
    return np.percentile(flc, q=quantiles).tolist()
    # return np.percentile(flc, q=[70, 90]).tolist()
    # return np.percentile(flc, q=[20, 80]).tolist()
    # return np.percentile(flc, q=[10, 30]).tolist()


# 时间序列
T = list()
T_size = 0
# syb_list = ["I1", "I2"]
# syb_list = ["L", "M", "H"]
# syb_list = ["I1", "I2", "I3", "I4"]
# syb_list = ["I1", "I2", "I3", "I4", "I5"]
syb_list = ["I1", "I2", "I3", "I4", "I5", "I6"]
FOP = list()
# 保存频繁OPJ，不区分前后缀，OP对应的ALP{(1,2):{(L),(M),(H)}, (2,1):{(L),(M),(H)},...}
OPJ_dic = dict()
# 模式出现字典{(1,2):{2, 4, 6, 7}, (2,1):{....}...}
occ_dic = dict()
# 模式作为前缀的出现，已经加1
prefix_occ = dict()
# 模式作为后缀的出现
suffix_occ = dict()

ratio = [0.01, 0.30]

min_sup = 100

# 候选模式计数
cand_cnt = 2 * len(syb_list)
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

    ratio = ratio_cal()
    # 输出FIL-Table的分位数阈值
    # print(ratio)
    # tracemalloc.start()
    starttime = time.time()
    FOP_miner()
    endtime = time.time()
    # current, peak = tracemalloc.get_traced_memory()
    # 输出挖掘结束时的当前内存和挖掘过程中的峰值内存
    # print(f"Current memory usage is {current / 10 ** 6:.3f} MB; Peak was {peak / 10 ** 6:.3f} MB")

    # 输出频繁OPJ的最大模式长度
    print('最长模式长度', len(FOP))
    level_num = 0
    level_cnt = {syb: 0 for syb in syb_list}
    op_set = set()
    for l in FOP:
        fre_cnt += len(l)
        for p in l:
            op_set.add(p[0])
            level_num += len(p[1])
            for lev in p[1]:
                level_cnt[lev] += 1
    # # 输出所有频繁OPJ的ILP中包含的等级符号总数
    # print(level_num)
    # 输出各等级符号在上述等级符号总数中的占比
    # for syb in syb_list:
    #     print(level_cnt[syb]/level_num)
    # # 输出频繁OPJ对应的不同OPP数量
    print("opp数量", len(op_set))
    # 输出频繁OPJ数量与对应OPP数量之比
    print('opj/opp ratio', fre_cnt/len(op_set))
    # cand_cnt包含长度为2的2d个初始候选；fre_cnt为频繁OPJ总数
    print("候选数量：", cand_cnt, "频繁模式数量", fre_cnt)
    # 输出挖掘总时间，包括序列扫描与编码，不包括数据读取和FIL-Table构建
    print("Running time: " + str(round(endtime * 1000 - starttime * 1000, 2)) + "ms")
