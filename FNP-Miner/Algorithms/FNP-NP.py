import copy
import time

import PdataFubp

pdata = PdataFubp.processingData()
from memory_profiler import memory_usage


CanNum = 0  # 候选模式数量

original_sequences = []


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
        if count >= minsup:
            p = []
            p.append(i)
            CanFNP.append([p])
            ItemS[str([p])] = [[] for k in range(SeqNum)]
            ItemS[str([p])] = S[i]
            # 计算OMV值
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


def two_len(FNP, CanFNP, ItemS):
    global CanNum
    dicTwoLenPattern = {}

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
            if count >= minsup:
                CanFNP.append(p)

                if dicTwoLenPattern.get(str([Item[pre][0]])) is None:
                    dicTwoLenPattern[str([Item[pre][0]])] = []
                dicTwoLenPattern[str([Item[pre][0]])].append(p)

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
            omv_values_strong_dict[str(p)] = omv_values_strong_dict[str(pre)] + \
                                             omv_values_strong_dict[str(suf)]
            strong_num = omv_values_strong_dict[str(p)] / 2
            count, ItemS[str(p)], fsup = Matching_S(ItemS[str(pre)], ItemS[str(suf)], SeqNum, strong_num)
            if count >= minsup:
                CanFNP.append(p)
                if dicTwoLenPattern.get(str([pre[0]])) is None:
                    dicTwoLenPattern[str([pre[0]])] = []

                dicTwoLenPattern[str([pre[0]])].append(p)

                if fsup >= minsup:
                    FNP.append(p)

            else:
                del ItemS[str(p)]

    return CanFNP, dicTwoLenPattern


def more_len(FNP, ItemS, ExpSet, ExpSetDict):
    global CanNum
    cnt = 3
    while ExpSet != []:
        temp = ExpSet[:]
        ExpSet = []
        dictmp = copy.deepcopy(ExpSetDict)
        ExpSetDict = {}
        for m in temp:
            suf = copy.deepcopy(m)
            suf[0].pop(0)
            if suf[0] == []:
                sufstr = str(suf[1:])

            else:
                sufstr = str(suf)
            if dictmp.get(sufstr) is None:
                continue
            temp1 = dictmp[sufstr]
            for n in temp1:
                if len(n[-1]) == 1:
                    pattern = copy.deepcopy(m)
                    pattern.append(n[-1])
                    CanNum += 1
                    omv_values_strong_dict[str(pattern)] = omv_values_strong_dict[str(pattern[:-1])] + \
                                                           omv_values_strong_dict[str([pattern[-1]])]
                    strong_num = omv_values_strong_dict[str(pattern)] / cnt
                    if len(pattern[:-1]) == 1:
                        count, ItemS[str(pattern)], fsup = Matching_S(ItemS[str(pattern[:-1])],
                                                                      ItemS[str([pattern[-1]])], SeqNum, strong_num)
                    else:
                        count, ItemS[str(pattern)], fsup = Matching_JS(ItemS[str(pattern[:-1])],
                                                                       ItemS[str([pattern[-1]])], SeqNum, strong_num)

                    if count >= minsup:
                        ExpSet.append(pattern)
                        if ExpSetDict.get(str(m)) is None:
                            ExpSetDict[str(m)] = []
                        ExpSetDict[str(m)].append(pattern)

                        if fsup >= minsup:
                            FNP.append(pattern)

                    else:
                        del ItemS[str(pattern)]

                else:
                    pattern = copy.deepcopy(m)
                    pattern[-1].append(n[-1][-1])
                    if len(pattern) > 1:
                        CanNum += 1
                        omv_values_strong_dict[str(pattern)] = omv_values_strong_dict[str(pattern[:-1])] + \
                                                               omv_values_strong_dict[str([pattern[-1]])]
                        strong_num = omv_values_strong_dict[str(pattern)] / cnt
                        if len(pattern[:-1]) == 1:
                            count, ItemS[str(pattern)], fsup = Matching_S(ItemS[str(pattern[:-1])],
                                                                          ItemS[str([pattern[-1]])], SeqNum, strong_num)
                        else:
                            count, ItemS[str(pattern)], fsup = Matching_JS(ItemS[str(pattern[:-1])],
                                                                           ItemS[str([pattern[-1]])], SeqNum,
                                                                           strong_num)

                        if count >= minsup:
                            ExpSet.append(pattern)
                            if ExpSetDict.get(str(m)) is None:
                                ExpSetDict[str(m)] = []
                            ExpSetDict[str(m)].append(pattern)

                            if fsup >= minsup:
                                FNP.append(pattern)

                        else:
                            del ItemS[str(pattern)]
                    else:
                        CanNum += 1

                        omv_sg = omv_values_strong_dict[str(m)] + omv_values_strong_dict[str([[n[-1][-1]]])]
                        omv_values_strong_dict[str(pattern)] = omv_sg

                        strong_num = omv_values_strong_dict[str(pattern)] / cnt
                        count, ItemS[str(pattern)], fsup = Matching_I(ItemS[str(m)], ItemS[str([[n[-1][-1]]])], SeqNum,
                                                                      strong_num)
                        if count >= minsup:
                            ExpSet.append(pattern)

                            if ExpSetDict.get(str(m)) is None:
                                ExpSetDict[str(m)] = []
                            ExpSetDict[str(m)].append(pattern)

                            if fsup >= minsup:
                                FNP.append(pattern)

                        else:
                            del ItemS[str(pattern)]
        cnt += 1
    return FNP



def Miner(SeqNum, S, sm_item, minsup, original_sequences):

    FNP = []
    ItemS = {}

    global omv_values_strong_dict
    omv_values_strong_dict = {}

    global preS_w, preS_c
    preS_w = [[0] * (len(original_sequences[i]) + 1) for i in range(SeqNum)]
    preS_c = [[0] * (len(original_sequences[i]) + 1) for i in range(SeqNum)]

    prefixSum_weak(preS_w, preS_c, SeqNum)

    print(f"\n开始挖掘频繁模式 (最小支持度: {minsup})...")

    FNP, ItemS, CanFNP = Mine_ItemS(FNP, ItemS, sm_item, SeqNum, minsup)
    twoLenPattern, dictTwoLen = two_len(FNP, CanFNP, ItemS)
    # print(len(twoLenPattern))
    FNP = more_len(FNP, ItemS, twoLenPattern, dictTwoLen)

    print("\n频繁模式及其OMV值:")

    print("\n统计信息:")
    print("频繁模式数量:", len(FNP))
    for c in FNP:
        print(str(c), end=',')
    print("\n候选模式数量:", CanNum)


if __name__ == '__main__':
    readFileName = "../datasets/SDB1.txt"

    minsup = 300

    print("开始执行模糊序列模式挖掘算法...")
    S = {}
    SeqNum, S, sm_item, original_sequences, char_membership, char_category, jz_m, weights = pdata.datap(
        readFileName, S)
    del pdata

    starttime = time.time()
    # Miner(SeqNum, S, sm_item, minsup, original_sequences)
    a = memory_usage(
        (Miner,
         (SeqNum, S, sm_item, minsup, original_sequences) 
         ), max_iterations=1
    )
    endtime = time.time()
    print("运行时间:", int(round(endtime * 1000)) - int(round(starttime * 1000)), "ms")

    print('Memory usage: ', max(a) - min(a))
