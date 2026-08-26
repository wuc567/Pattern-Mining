import time
import tracemalloc

from memory_profiler import memory_usage


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
    global cand_cnt
    op_len = len(opp)
    # 枚举保序的最后一个位置，从1开始
    last_rank = 1
    # 最后一位从i=1开始枚举
    while last_rank <= op_len + 1:
        # 前缀剪枝
        if len(prefix_occ[opp]) < min_sup:
            return
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
        
        # 判断后缀保序是不是频繁的，即在不在集合中，并且后缀的出现位置是否大于最小支持度
        if s_opp_suf in OPJ_dic and len(suffix_occ[s_opp_suf]) >= min_sup:
            # 判断保序生成rh还是r，枚举从1开始枚举，优先产生h，实际上r在下一次枚举产生，直接跳过即可
            r_opp = ()
            h_opp = ()
            if last_rank == opp[0]:
                # 1开始枚举优先h
                h_opp = s_opp
                r_opp = list(h_opp)
                r_opp[0], r_opp[-1] = r_opp[-1], r_opp[0]
                r_opp = tuple(r_opp)
                
                cand_cnt += 2
                occ_r, occ_h = cal_occ_2(len(r_opp), opp, s_opp_suf)
                if len(occ_r) >= min_sup:
                    new_FOP.append(r_opp)
                    new_occ_dic[r_opp] = occ_r
                    # print(r_opp, len(occ_r))
                if len(occ_h) >= min_sup:
                    new_FOP.append(h_opp)
                    new_occ_dic[h_opp] = occ_h

            else:
                # 如果不产生两个opp，r_opp就是s_opp
                r_opp = s_opp
                cand_cnt += 1
                
                occ_r = cal_occ_1(opp, s_opp_suf)
                # print("r")

                if len(occ_r) >= min_sup:
                    new_FOP.append(r_opp)
                    new_occ_dic[r_opp] = occ_r
                    # print(r_opp, len(occ_r))

            # opp_fusion(r_opp, h_opp, opp, s_opp_suf, new_FOP, new_occ_dic)

        if last_rank == opp[0]:
            last_rank += 2
        else:
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
    FOP.append(list())
    # 为长度为2的模式开辟空间
    occ_dic[(1, 2)] = set()
    occ_dic[(2, 1)] = set()
    a = time.time()
    # 计算长度为2的出现位置
    for i in range(T_size - 1):
        delta = T[i + 1] - T[i]

        # delta为差值, =0 不是出现; <0是(2,1); >0是(1,2)
        if delta == 0:
            continue
        elif delta > 0:
            occ_dic[(1, 2)].add(i + 1)
        else:
            occ_dic[(2, 1)].add(i + 1)

    print(time.time() - a)
    # print(occ_dic.keys())
    # 函数查找长度为2的频繁模式，并加入结果集
    for p in occ_dic:
        # print(p, occ_dic[p])
        if len(occ_dic[p]) >= min_sup:
            FOP[-1].append(p)


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
        # 将当前层频繁OPP存入集合，用于EAC哈希查询
        OPJ_dic.update(FOP[-1])
        for p in FOP[-1]:
            # 前后缀出现，前缀提前+1
            prefix_occ[p] = {occ + 1 for occ in occ_dic[p]}
            suffix_occ[p] = occ_dic[p]

        # 对当前层频繁opp进行遍历
        # opp_cnt += len(OPJ_dic)
        # for opp in OPJ_dic:
        #     if len(opp) >= 5:
        #         print(opp)
        # key = (1, 3, 2, 5, 4)
        # if key in OPJ_dic:
        #     print(key)

        for opp in FOP[-1]:
            enum_and_check_opp(opp, new_FOP, new_occ_dic)
            # 释放opp内存
            del occ_dic[opp]

        occ_dic = new_occ_dic
        FOP.append(new_FOP)
        # current, peak = tracemalloc.get_traced_memory()
        # print(f"Current memory usage is {current / 10 ** 6:.2f} MB; Peak was {peak / 10 ** 6:.2f} MB")
    # print(fusion_time)
    # print(cal_time)


def FOP_miner():
    find_2()
    find_m()


# 时间序列
T = list()
T_size = 0
FOP = list()
# 保存当前层的频繁OPP，用于EAC哈希查询
OPJ_dic = set()
# 模式出现字典{(1,2):{2, 4, 6, 7}, (2,1):{....}...}
occ_dic = dict()
# 模式作为前缀的出现，已经加1
prefix_occ = dict()
# 模式作为后缀的出现
suffix_occ = dict()

min_sup = 10

# 候选模式计数
cand_cnt = 2
# 频繁模式计数
fre_cnt = 0

if __name__ == '__main__':
    read_file("../datasets/Plant_1_Weather_Sensor_Data.txt")
    # read_file("../datasets/New_York_Air_Quality.txt")
    # read_file("../datasets/KURIAS-ECG_HeartRate.txt")
    # read_file("../datasets/Metro_Interstate_Traffic_Volume.txt")
    # read_file("../datasets/股票Russell2000（1987.9.10~2019.12.27）.txt")
    # read_file("../datasets/Nasdaq.txt")
    # read_file("../datasets/S&P500.txt")
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

    # tracemalloc.start()
    starttime = time.time()
    FOP_miner()
    # mem = memory_usage((FOP_miner,), interval=0.001)
    # print("内存:", round(max(mem) - min(mem), 3), "MB")
    endtime = time.time()
    # current, peak = tracemalloc.get_traced_memory()
    # print(f"Current memory usage is {current / 10 ** 6:.3f} MB; Peak was {peak / 10 ** 6:.3f} MB")

    print(len(FOP))
    for l in FOP:
        fre_cnt += len(l)
    print("候选数量：", cand_cnt, "频繁模式数量", fre_cnt)
    print("Running time: " + str(round(endtime * 1000 - starttime * 1000, 2)) + "ms")
