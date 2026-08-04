import copy
import time
import sys
from multiprocessing import Process

# import pandas as pd
import PdataFubp

pdata = PdataFubp.processingData()
from memory_profiler import memory_usage


class Logger(object):
    def __init__(self, filename="NTP-FNP实验结果.txt"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

CanNum = 0
original_sequences = []
flag_p = False
SeqNum = 0
S = {}
sm_item = []
char_membership = {}
char_category = {}
jz_m = 0
minsup = 0
weights = []


def compute_support(pl_map, pattern):
    result = []
    n = len(pattern)
    if n == 0:
        return 0, result
    first_char = str([pattern[0]])
    if first_char not in pl_map:
        return 0, result
    seq_count = len(pl_map[first_char])
    result = [[] for _ in range(seq_count)]
    for seq_num in range(seq_count):
        current_pl = {}
        valid = True
        for char in pattern:
            char = str([char])
            if char not in pl_map or seq_num >= len(pl_map[char]):
                valid = False
                break
            current_pl[char] = pl_map[char][seq_num]
            if not current_pl[char]:
                valid = False
                break
        if not valid:
            continue
        ptr = [0] * n
        first_pos_list = current_pl[str([pattern[0]])]
        if not first_pos_list:
            continue
        current_level = 1
        pre_pos = first_pos_list[ptr[0]]
        current_char = str([pattern[current_level]])
        current_pos_list = current_pl[current_char]
        while current_pos_list and ptr[current_level] < len(current_pos_list):
            curr_pos = current_pos_list[ptr[current_level]]
            if curr_pos <= pre_pos:
                ptr[current_level] += 1
                continue
            if current_level == n - 1:
                occ = tuple(current_pl[str([pattern[i]])][ptr[i]] for i in range(n))
                result[seq_num].append(occ)
                for i in range(n):
                    ptr[i] += 1
                if ptr[0] >= len(first_pos_list):
                    break
                pre_pos = first_pos_list[ptr[0]]
                current_level = 1
                current_char = str([pattern[current_level]])
                current_pos_list = current_pl[current_char]
                continue
            pre_pos = curr_pos
            current_level += 1
            current_char = str([pattern[current_level]])
            current_pos_list = current_pl[current_char]
    total_count = sum(len(seq_matches) for seq_matches in result)
    return total_count, result


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
            CanFNP.append([p])
            ItemS[str([p])] = [[] for k in range(SeqNum)]
            ItemS[str([p])] = S[i]
            fsup = 0
            for seq_idx in range(SeqNum):
                if ItemS[str([p])][seq_idx]:
                    fsup += char_membership.get(i, {}).get('Strong', 0) * len(ItemS[str([p])][seq_idx])
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
            strong_num = 0
            for char in t:
                strong_num += char_membership.get(char, {}).get('Strong', 0)
            strong_num /= 2
            count, ItemS[str(p)], fsup = Matching_I(ItemS[str(Item[pre])], ItemS[str(Item[suf])], SeqNum, strong_num)
            if count * jz_m >= minsup:
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
            count, all_occ = compute_support(ItemS, p)
            if count * jz_m >= minsup:
                CanFNP.append(p)
                if dicTwoLenPattern.get(str([pre[0]])) is None:
                    dicTwoLenPattern[str([pre[0]])] = []
                dicTwoLenPattern[str([pre[0]])].append(p)
                fsup = 0
                strong_num = 0
                cnt = 0
                for item in p:
                    for char in item:
                        strong_num += char_membership.get(char, {}).get('Strong', 0)
                        cnt += 1
                strong_num /= cnt
                for i in range(SeqNum):
                    occ_s = all_occ[i]
                    for j in range(len(occ_s)):
                        occ = occ_s[j]
                        weakm = 0.0
                        gap = 0
                        for k in range(len(occ) - 1):
                            for po in range(occ[k] + 1, occ[k + 1]):
                                for char in original_sequences[i][po]:
                                    weakm += char_membership.get(char, {}).get('Weak', 0)
                                    gap += 1
                        if gap == 0:
                            fsup += strong_num
                        else:
                            weakm /= gap
                            fsup += (strong_num + weakm) / 2.0
                if fsup >= minsup:
                    FNP.append(p)
    return CanFNP, dicTwoLenPattern


def more_len(FNP, ItemS, ExpSet, ExpSetDict):
    global CanNum
    global flag_p
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
                    count, all_occ = compute_support(ItemS, pattern)
                    if count * jz_m >= minsup:
                        ExpSet.append(pattern)
                        if ExpSetDict.get(str(m)) is None:
                            ExpSetDict[str(m)] = []
                        ExpSetDict[str(m)].append(pattern)
                        fsup = 0
                        strong_num = 0
                        for item in pattern:
                            for char in item:
                                strong_num += char_membership.get(char, {}).get('Strong', 0)
                        strong_num /= cnt
                        for i in range(SeqNum):
                            occ_s = all_occ[i]
                            for j in range(len(occ_s)):
                                occ = occ_s[j]
                                weakm = 0.0
                                gap = 0
                                for k in range(len(occ) - 1):
                                    for po in range(occ[k] + 1, occ[k + 1]):
                                        for char in original_sequences[i][po]:
                                            weakm += char_membership.get(char, {}).get('Weak', 0)
                                            gap += 1
                                if gap == 0:
                                    fsup += strong_num
                                else:
                                    weakm /= gap
                                    fsup += (strong_num + weakm) / 2.0
                        if fsup >= minsup:
                            FNP.append(pattern)
                else:
                    pattern = copy.deepcopy(m)
                    pattern[-1].append(n[-1][-1])
                    CanNum += 1
                    if len(pattern) > 1:
                        count, all_occ = compute_support(ItemS, pattern)
                        if count * jz_m >= minsup:
                            ExpSet.append(pattern)
                            if ExpSetDict.get(str(m)) is None:
                                ExpSetDict[str(m)] = []
                            ExpSetDict[str(m)].append(pattern)
                            fsup = 0
                            strong_num = 0
                            for item in pattern:
                                for char in item:
                                    strong_num += char_membership.get(char, {}).get('Strong', 0)
                            strong_num /= cnt
                            for i in range(SeqNum):
                                occ_s = all_occ[i]
                                for j in range(len(occ_s)):
                                    occ = occ_s[j]
                                    weakm = 0.0
                                    gap = 0
                                    for k in range(len(occ) - 1):
                                        for po in range(occ[k] + 1, occ[k + 1]):
                                            for char in original_sequences[i][po]:
                                                weakm += char_membership.get(char, {}).get('Weak', 0)
                                                gap += 1
                                    if gap == 0:
                                        fsup += strong_num
                                    else:
                                        weakm /= gap
                                        fsup += (strong_num + weakm) / 2.0
                            if fsup >= minsup:
                                FNP.append(pattern)
                    else:
                        strong_num = 0
                        for item in pattern:
                            for char in item:
                                strong_num += char_membership.get(char, {}).get('Strong', 0)
                        strong_num /= cnt
                        count, ItemS[str(pattern)], fsup = Matching_I(ItemS[str(m)], ItemS[str([[n[-1][-1]]])], SeqNum,
                                                                      strong_num)
                        if count * jz_m >= minsup:
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


def Miner():
    FNP = []
    ItemS = {}
    print(f"\n开始挖掘频繁模式 (最小支持度: {minsup})...")
    FNP, ItemS, CanFNP = Mine_ItemS(FNP, ItemS, sm_item, SeqNum, minsup)
    twoLenPattern, dictTwoLen = two_len(FNP, CanFNP, ItemS)
    FNP = more_len(FNP, ItemS, twoLenPattern, dictTwoLen)
    print("\n频繁模式及其OMV值:")
    print("\n统计信息:")
    print("频繁模式数量:", len(FNP))
    for c in FNP:
        print(str(c), end=',')
    print("\n候选模式数量:", CanNum)


def run_single_dataset(readFileName, minsup_val, interest_file):
    sys.stdout = Logger("NTP-FNP实验结果.txt")

    global CanNum, minsup, SeqNum, S, sm_item, original_sequences, char_membership, char_category, jz_m, weights
    CanNum = 0
    minsup = minsup_val
    S = {}

    print("\n" + "=" * 90)
    print(f" 正在运行 → 数据集：{readFileName}")
    print(f"           最小支持度：{minsup_val}")
    print(f"           兴趣度文件：{interest_file}")
    print("=" * 90)

    starttime = time.time()
    mem_pdata, (SeqNum, S, sm_item, original_sequences,
                char_membership, char_category, jz_m, weights) = memory_usage(
        (pdata.datap, (readFileName, S, interest_file)),
        max_iterations=1,
        retval=True
    )

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
    print("           开始执行模糊序列模式挖掘算法（结果已保存到文件）")
    print("=" * 80)

    for args in dataset_config:
        p = Process(target=run_single_dataset, args=args)
        p.start()
        p.join()