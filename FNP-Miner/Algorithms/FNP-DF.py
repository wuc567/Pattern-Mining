import copy
import time
import gc
import sys
from multiprocessing import Process

import PdataFubp
from memory_profiler import memory_usage


class Logger(object):
    def __init__(self, filename="FNP-DF实验结果.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass


CanNum = 0
original_sequences = []
CanFNP1 = []
omv_values_strong_dict = {}
preS_w = []
preS_c = []
SeqNum = 0
S = {}
sm_item = []
char_membership = {}
char_category = {}
jz_m = 0
minsup = 0
weights = []


def has_fuzzy_strong_between(seq_idx, start_pos, end_pos, original_sequences):
    for pos in range(start_pos + 1, end_pos):
        for char in original_sequences[seq_idx][pos]:
            if char_category.get(char, 'Medium') == 'Strong':
                return True
    return False


def prefixSum_weak(preS_w, preS_c, SeqNum):
    for i in range(SeqNum):
        for pos in range(len(original_sequences[i])):
            w_avg = 0
            l = len(original_sequences[i][pos])
            if l != 0:
                for char in original_sequences[i][pos]:
                    w_avg += char_membership.get(char, {}).get('Weak', 0)
            preS_w[i][pos + 1] = preS_w[i][pos] + w_avg
            preS_c[i][pos + 1] = preS_c[i][pos] + l


def calculate_omv_weak_2d(start, end, seq_idx):
    if end == start + 1:
        return 0, 0
    return preS_w[seq_idx][end] - preS_w[seq_idx][start + 1], preS_c[seq_idx][end] - preS_c[seq_idx][start + 1]


def Matching_I(list1, list2, SeqNum, strong_num):
    list3 = [[] for _ in range(SeqNum)]
    count = 0
    fsup = 0
    for i in range(SeqNum):
        common = sorted(list(set(list1[i]) & set(list2[i])))
        list3[i] = common
        l = len(common)
        count += l
        fsup += strong_num * l
    return count, list3, fsup


def Matching_S(list1, list2, SeqNum, strong_num):
    list3 = [[] for _ in range(SeqNum)]
    flag = 0
    fsup = 0
    count = 0
    for i in range(SeqNum):
        for j in range(len(list1[i])):
            if flag >= len(list2[i]):
                break
            for k in range(flag, len(list2[i])):
                if list2[i][k] > list1[i][j]:
                    weak_sum, cnt = calculate_omv_weak_2d(list1[i][j], list2[i][k], i)
                    if cnt == 0:
                        fsup += strong_num
                    else:
                        fsup += (weak_sum / cnt + strong_num) / 2
                    list3[i].append([list2[i][k], cnt, weak_sum])
                    count += 1
                    flag = k + 1
                    break
                if k == len(list2[i]) - 1:
                    flag = len(list2[i])
        flag = 0
    return count, list3, fsup


def Matching_JS(list1, list2, SeqNum, strong_num):
    list3 = [[] for _ in range(SeqNum)]
    flag = 0
    count = 0
    fsup = 0
    for i in range(SeqNum):
        for j in range(len(list1[i])):
            if flag >= len(list2[i]):
                break
            for k in range(flag, len(list2[i])):
                if list2[i][k] > list1[i][j][0]:
                    weak_sum, cnt = calculate_omv_weak_2d(list1[i][j][0], list2[i][k], i)
                    cnt += list1[i][j][1]
                    if cnt == 0:
                        weak_sum = 0
                        fsup += strong_num
                    else:
                        weak_sum = list1[i][j][2] + weak_sum
                        fsup += (weak_sum / cnt + strong_num) / 2
                    list3[i].append([list2[i][k], cnt, weak_sum])
                    count += 1
                    flag = k + 1
                    break
                if k == len(list2[i]) - 1:
                    flag = len(list2[i])
        flag = 0
    return count, list3, fsup


def Mine_ItemS(FNP, ItemS, sm_item, SeqNum, minsup):
    global CanNum
    CanFNP = []
    for i in sm_item:
        CanNum += 1
        count = 0
        for j in range(SeqNum):
            count += len(S[i][j])
        if count * jz_m >= minsup:
            p = []
            p.append(i)
            CanFNP1.append(p[0])
            CanFNP.append([p])
            ItemS[str([p])] = [[] for k in range(SeqNum)]
            ItemS[str([p])] = S[i]
            fsup = 0
            for seq_idx in range(SeqNum):
                if ItemS[str([p])][seq_idx]:
                    omv_sg = char_membership.get(i, {}).get('Strong', 0)
                    omv_values_strong_dict[str([p])] = omv_sg
                    omv = omv_sg * len(ItemS[str([p])][seq_idx])
                    fsup += omv
            if fsup >= minsup:
                FNP.append([p])
    return FNP, ItemS, CanFNP


def DeepMiner(FNP, pattern, ItemS, cnt):
    global CanNum
    Item = copy.deepcopy(CanFNP1)
    for m in Item:
        pre = copy.deepcopy(pattern)
        suf = m
        if m not in pre[-1] and str(m) > str(pre[-1][-1]):
            p = copy.deepcopy(pre)
            p[-1].append(suf)
            CanNum += 1
            omv_values_strong_dict[str(p)] = omv_values_strong_dict[str(pre)] + omv_values_strong_dict[str([[m]])]
            strong_num = omv_values_strong_dict[str(p)] / cnt
            if len(pre) == 1:
                count, ItemS[str(p)], fsup = Matching_I(ItemS[str(pre)], ItemS[str([[m]])], SeqNum, strong_num)
                if count * jz_m >= minsup:
                    if fsup >= minsup:
                        FNP.append(p)
                    DeepMiner(FNP, p, ItemS, cnt + 1)
                else:
                    del ItemS[str(p)]
            else:
                count, ItemS[str([p[-1]])], fsup = Matching_I(ItemS[str([p[-1][:-1]])], ItemS[str([[m]])], SeqNum,
                                                              strong_num)
                if len(p[:-1]) == 1:
                    count, ItemS[str(p)], fsup = Matching_S(ItemS[str(p[:-1])], ItemS[str([p[-1]])], SeqNum, strong_num)
                else:
                    count, ItemS[str(p)], fsup = Matching_JS(ItemS[str(p[:-1])], ItemS[str([p[-1]])], SeqNum,
                                                             strong_num)
                if count * jz_m >= minsup:
                    if fsup >= minsup:
                        FNP.append(p)
                    DeepMiner(FNP, p, ItemS, cnt + 1)
                else:
                    del ItemS[str(p)]
        p = copy.deepcopy(pre)
        p.append([suf])
        CanNum += 1
        omv_values_strong_dict[str(p)] = omv_values_strong_dict[str(p[:-1])] + omv_values_strong_dict[str([p[-1]])]
        strong_num = omv_values_strong_dict[str(p)] / cnt
        if len(p[:-1]) == 1:
            count, ItemS[str(p)], fsup = Matching_S(ItemS[str(p[:-1])], ItemS[str([p[-1]])], SeqNum, strong_num)
        else:
            count, ItemS[str(p)], fsup = Matching_JS(ItemS[str(p[:-1])], ItemS[str([p[-1]])], SeqNum, strong_num)
        if count * jz_m >= minsup:
            if fsup >= minsup:
                FNP.append(p)
            DeepMiner(FNP, p, ItemS, cnt + 1)
        else:
            del ItemS[str(p)]


def Miner():
    global omv_values_strong_dict, preS_w, preS_c
    FNP = []
    ItemS = {}
    omv_values_strong_dict = {}
    preS_w = [[0] * (len(original_sequences[i]) + 1) for i in range(SeqNum)]
    preS_c = [[0] * (len(original_sequences[i]) + 1) for i in range(SeqNum)]
    prefixSum_weak(preS_w, preS_c, SeqNum)

    print(f"\n开始挖掘频繁模式 (最小支持度: {minsup})...")
    FNP, ItemS, CanFNP = Mine_ItemS(FNP, ItemS, sm_item, SeqNum, minsup)
    Item = copy.deepcopy(CanFNP)
    cnt = 2
    for i in Item:
        DeepMiner(FNP, i, ItemS, cnt)

    print("\n统计信息:")
    print("频繁模式数量:", len(FNP))
    for c in FNP:
        print(str(c), end=',')
    print("\n候选模式数量:", CanNum)


def run_task(readFileName, minsup_val, interest_file):
    sys.stdout = Logger("FNP-DF实验结果.txt")

    global CanNum, CanFNP1, SeqNum, S, sm_item, original_sequences
    global char_membership, char_category, jz_m, weights, minsup

    CanNum = 0
    CanFNP1 = []
    gc.collect()

    print("\n" + "=" * 90)
    print(f" 正在运行 → 数据集：{readFileName}")
    print(f"           最小支持度：{minsup_val}")
    print(f"           兴趣度文件：{interest_file}")
    print("=" * 90)

    starttime = time.time()
    S = {}
    minsup = minsup_val

    mem_pdata, ret = memory_usage(
        (PdataFubp.processingData().datap, (readFileName, S, interest_file)),
        max_iterations=1, retval=True
    )
    SeqNum, S, sm_item, original_sequences, char_membership, char_category, jz_m, weights = ret

    mem_miner = memory_usage((Miner,), max_iterations=1)
    total_mem = mem_pdata + mem_miner
    endtime = time.time()

    print(f"\n 运行完成：")
    print(f" 数据集：{readFileName}")
    print(f" 支持度：{minsup_val}")
    print(f" 运行时间：{int(round(endtime * 1000)) - int(round(starttime * 1000))} ms")
    print(f" 总内存消耗：{max(total_mem) - min(total_mem)} MB")
    print("=" * 90 + "\n\n")


if __name__ == '__main__':
    dataset_config = [
        ("../../datasets/SDB1.txt", 300, "../../datasets/SDB1_interest.txt")
    ]

    print("=" * 80)
    print("           开始执行模糊序列模式挖掘算法")
    print("=" * 80)

    for args in dataset_config:
        p = Process(target=run_task, args=args)
        p.start()
        p.join()