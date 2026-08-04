import copy
import time
import gc
import sys
from multiprocessing import Process

import PdataFubp
from memory_profiler import memory_usage


def has_fuzzy_strong_between(seq_idx, start_pos, end_pos, original_sequences, char_category):
    for pos in range(start_pos + 1, end_pos):
        for char in original_sequences[seq_idx][pos]:
            if char_category.get(char, 'Medium') == 'Strong':
                return True
    return False


def prefixSum_weak(preS_w, preS_c, SeqNum, original_sequences, char_membership):
    for i in range(SeqNum):
        for pos in range(len(original_sequences[i])):
            w_avg = 0
            l = len(original_sequences[i][pos])
            if l != 0:
                for char in original_sequences[i][pos]:
                    w_avg += char_membership.get(char, {}).get('Weak', 0)
            preS_w[i][pos + 1] = preS_w[i][pos] + w_avg
            preS_c[i][pos + 1] = preS_c[i][pos] + l


def calculate_omv_weak_2d(start, end, seq_idx, preS_w, preS_c):
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


def Matching_S(list1, list2, SeqNum, strong_num, preS_w, preS_c):
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
                    weak_sum, cnt = calculate_omv_weak_2d(list1[i][j], list2[i][k], i, preS_w, preS_c)
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


def Matching_JS(list1, list2, SeqNum, strong_num, preS_w, preS_c):
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
                    weak_sum, cnt = calculate_omv_weak_2d(list1[i][j][0], list2[i][k], i, preS_w, preS_c)
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


def Mine_ItemS(FNP, ItemS, sm_item, SeqNum, minsup, S, jz_m, char_membership, omv_values_strong_dict, CanFNP1):
    CanNum = 0
    CanFNP = []
    for i in sm_item:
        CanNum += 1
        count = 0
        for j in range(SeqNum):
            count += len(S[i][j])
        if count * jz_m >= minsup:
            p = []
            p.append(i)
            CanFNP.append([p])
            CanFNP1.append(p[0])
            ItemS[str([p])] = S[i].copy()
            fsup = 0
            for seq_idx in range(SeqNum):
                if ItemS[str([p])][seq_idx]:
                    omv_sg = char_membership.get(i, {}).get('Strong', 0)
                    omv_values_strong_dict[str([p])] = omv_sg
                    fsup += omv_sg * len(ItemS[str([p])][seq_idx])
            if fsup >= minsup:
                FNP.append([p])
    return FNP, ItemS, CanFNP, CanNum


def two_len(FNP, CanFNP, ItemS, SeqNum, jz_m, minsup, omv_values_strong_dict, preS_w, preS_c):
    CanNum = 0
    Item = copy.deepcopy(CanFNP)
    CanFNP = []
    for pre in range(len(Item)):
        for suf in range(pre + 1, len(Item)):
            t = copy.deepcopy(Item[pre][0])
            t.append(Item[suf][0][0])
            p = [t]
            CanNum += 1
            omv_sg = omv_values_strong_dict[str(Item[pre])] + omv_values_strong_dict[str(Item[suf])]
            omv_values_strong_dict[str(p)] = omv_sg
            strong_num = omv_sg / 2
            count, ItemS[str(p)], fsup = Matching_I(ItemS[str(Item[pre])], ItemS[str(Item[suf])], SeqNum, strong_num)
            if count * jz_m >= minsup:
                CanFNP.append(p)
                if fsup >= minsup:
                    FNP.append(p)
            else:
                del ItemS[str(p)]
    for m in Item:
        pre = copy.deepcopy(m)
        for n in Item:
            suf = copy.deepcopy(n)
            p = [pre[0], suf[0]]
            CanNum += 1
            omv_values_strong_dict[str(p)] = omv_values_strong_dict[str(pre)] + omv_values_strong_dict[str(suf)]
            strong_num = omv_values_strong_dict[str(p)] / 2
            count, ItemS[str(p)], fsup = Matching_S(ItemS[str(pre)], ItemS[str(suf)], SeqNum, strong_num, preS_w,
                                                    preS_c)
            if count * jz_m >= minsup:
                CanFNP.append(p)
                if fsup >= minsup:
                    FNP.append(p)
            else:
                del ItemS[str(p)]
    return CanFNP, CanNum


def more_len(FNP, ItemS, ExpSet, SeqNum, jz_m, minsup, omv_values_strong_dict, CanFNP1, preS_w, preS_c):
    CanNum = 0
    cnt = 3
    Item = copy.deepcopy(CanFNP1)
    while ExpSet != []:
        temp = ExpSet[:]
        ExpSet = []
        for m in temp:
            for n in Item:
                pattern = copy.deepcopy(m)
                pattern1 = copy.deepcopy(m)
                pattern.append([n])
                CanNum += 1
                omv_values_strong_dict[str(pattern)] = omv_values_strong_dict[str(pattern[:-1])] + \
                                                       omv_values_strong_dict[str([pattern[-1]])]
                strong_num = omv_values_strong_dict[str(pattern)] / cnt
                if len(pattern[:-1]) == 1:
                    count, ItemS[str(pattern)], fsup = Matching_S(ItemS[str(pattern[:-1])], ItemS[str([pattern[-1]])],
                                                                  SeqNum, strong_num, preS_w, preS_c)
                else:
                    count, ItemS[str(pattern)], fsup = Matching_JS(ItemS[str(pattern[:-1])], ItemS[str([pattern[-1]])],
                                                                   SeqNum, strong_num, preS_w, preS_c)
                if count * jz_m >= minsup:
                    ExpSet.append(pattern)
                    if fsup >= minsup:
                        FNP.append(pattern)
                else:
                    del ItemS[str(pattern)]
                if n not in m[-1] and str(n) > str(m[-1][-1]):
                    pattern1[-1].append(n)
                    CanNum += 1
                    omv_values_strong_dict[str(pattern1)] = omv_values_strong_dict[str(m)] + omv_values_strong_dict[
                        str([[n]])]
                    strong_num = omv_values_strong_dict[str(pattern1)] / cnt
                    if len(pattern1) == 1:
                        count, ItemS[str(pattern1)], fsup = Matching_I(ItemS[str(m)], ItemS[str([[n]])], SeqNum,
                                                                       strong_num)
                        if count * jz_m >= minsup:
                            ExpSet.append(pattern1)
                            if fsup >= minsup:
                                FNP.append(pattern1)
                        else:
                            del ItemS[str(pattern1)]
                    else:
                        count, ItemS[str([pattern1[-1]])], fsup = Matching_I(ItemS[str([pattern1[-1][:-1]])],
                                                                             ItemS[str([[n]])], SeqNum, strong_num)
                        if len(pattern1[:-1]) == 1:
                            count, ItemS[str(pattern1)], fsup = Matching_S(ItemS[str(pattern1[:-1])],
                                                                           ItemS[str([pattern1[-1]])], SeqNum,
                                                                           strong_num, preS_w, preS_c)
                        else:
                            count, ItemS[str(pattern1)], fsup = Matching_JS(ItemS[str(pattern1[:-1])],
                                                                            ItemS[str([pattern1[-1]])], SeqNum,
                                                                            strong_num, preS_w, preS_c)
                        if count * jz_m >= minsup:
                            ExpSet.append(pattern1)
                            if fsup >= minsup:
                                FNP.append(pattern1)
                        else:
                            del ItemS[str(pattern1)]
        cnt += 1
    return FNP, CanNum


def Miner(SeqNum, S, sm_item, original_sequences, char_membership, char_category, jz_m, minsup):
    FNP = []
    ItemS = {}
    omv_values_strong_dict = {}
    CanFNP1 = []

    preS_w = [[0] * (len(original_sequences[i]) + 1) for i in range(SeqNum)]
    preS_c = [[0] * (len(original_sequences[i]) + 1) for i in range(SeqNum)]
    prefixSum_weak(preS_w, preS_c, SeqNum, original_sequences, char_membership)

    print(f"\n开始挖掘频繁模式 (最小支持度: {minsup})...")
    FNP, ItemS, CanFNP, CanNum1 = Mine_ItemS(FNP, ItemS, sm_item, SeqNum, minsup, S, jz_m, char_membership,
                                             omv_values_strong_dict, CanFNP1)
    twoLenPattern, CanNum2 = two_len(FNP, CanFNP, ItemS, SeqNum, jz_m, minsup, omv_values_strong_dict, preS_w, preS_c)
    FNP, CanNum3 = more_len(FNP, ItemS, twoLenPattern, SeqNum, jz_m, minsup, omv_values_strong_dict, CanFNP1, preS_w,
                            preS_c)

    total_can_num = CanNum1 + CanNum2 + CanNum3
    print("\n统计信息:")
    print("频繁模式数量:", len(FNP))
    print("候选模式数量:", total_can_num)
    return len(FNP), total_can_num


def run_single_dataset(readFileName, minsup, interest_file, log_filename):
    # 子进程独立日志
    class Logger(object):
        def __init__(self, filename):
            self.terminal = sys.stdout
            self.log = open(filename, "a", encoding="utf-8")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass

        def close(self):
            self.log.close()

    sys.stdout = Logger(log_filename)

    pdata = PdataFubp.processingData()
    gc.collect()

    print("\n" + "=" * 90)
    print(f" 正在运行 → 数据集：{readFileName}")
    print(f"           最小支持度：{minsup}")
    print(f"           兴趣度文件：{interest_file}")
    print("=" * 90)

    starttime = time.time()
    S = {}

    mem_pdata, ret_val = memory_usage(
        (pdata.datap, (readFileName, S, interest_file)), max_iterations=1, retval=True
    )
    SeqNum, S, sm_item, original_sequences, char_membership, char_category, jz_m, weights = ret_val

    mem_miner = memory_usage(
        (Miner, (SeqNum, S, sm_item, original_sequences, char_membership, char_category, jz_m, minsup)), max_iterations=1)
    total_mem = mem_pdata + mem_miner
    endtime = time.time()

    print(f"\n 运行完成：")
    print(f"数据集：{readFileName}")
    print(f"支持度：{minsup}")
    print(f"运行时间：{int(round(endtime * 1000)) - int(round(starttime * 1000))} ms")
    print(f"总内存消耗：{max(total_mem) - min(total_mem)} MB")
    print("=" * 90 + "\n\n")

    sys.stdout.close()
    gc.collect()


if __name__ == '__main__':
    dataset_config = [
        ("../../datasets/SDB1.txt", 300, "../../datasets/SDB1_interest.txt")
    ]

    log_file = "FNP-BF实验结果.txt"
    open(log_file, "w", encoding="utf-8").close()

    print("=" * 80)
    print("           开始执行模糊序列模式挖掘算法")
    print("=" * 80)

    for args in dataset_config:
        readFileName, minsup, interest_file = args
        p = Process(target=run_single_dataset, args=(readFileName, minsup, interest_file, log_file))
        p.start()
        p.join()
