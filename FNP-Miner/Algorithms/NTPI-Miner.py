import copy
import sys
import time
import os
import gc

import PdataFtnpstr

pdata = PdataFtnpstr.processingData()
from memory_profiler import memory_usage

CanNum = 0

original_sequences = []


def compute_support(pl_map, pattern):
    result = []
    n = len(pattern)
    if n == 0:
        return result  


    first_char = str([pattern[0]])
    if first_char not in pl_map:
        return result  
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
        first_nodes = current_pl[first_char]
        if not first_nodes:
            continue  

        current_level = 1
        pre_pos, pre_strong = first_nodes[ptr[0]]
        current_char = str([pattern[current_level]])
        current_nodes = current_pl[current_char]

        while current_nodes and ptr[current_level] < len(current_nodes):
            curr_pos, curr_strong = current_nodes[ptr[current_level]]

            if curr_pos <= pre_pos:
                ptr[current_level] += 1
                continue

            if pre_strong is not None and curr_pos > pre_strong:
                current_level -= 1
                ptr[current_level] += 1

                if current_level == 0 and ptr[0] >= len(first_nodes):
                    break
                if current_level == 0:
                    pre_pos, pre_strong = first_nodes[ptr[0]]
                    current_level = 1
                else:
                    pre_char = str([pattern[current_level - 1]])
                    pre_nodes = current_pl[pre_char]
                    pre_pos, pre_strong = pre_nodes[ptr[current_level - 1]]

                current_char = str([pattern[current_level]])
                current_nodes = current_pl[current_char]
                continue

            if current_level == n - 1:
                occ = tuple(current_pl[str([pattern[i]])][ptr[i]][0] for i in range(n))
                result[seq_num].append(occ)  

                for i in range(n):
                    ptr[i] += 1

                if ptr[0] >= len(first_nodes):
                    break

                pre_pos, pre_strong = first_nodes[ptr[0]]
                current_level = 1
                current_char = str([pattern[current_level]])
                current_nodes = current_pl[current_char]
                continue

            pre_pos, pre_strong = curr_pos, curr_strong
            current_level += 1
            current_char = str([pattern[current_level]])
            current_nodes = current_pl[current_char]
    total_count = 0

    for i, seq_matches in enumerate(result):
        total_count+=len(seq_matches)
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


def Mine_ItemS(NTPI, ItemS, sm_item, SeqNum, minsup):
    global CanNum
    CanNTPI = []


    for i in sm_item: 
        CanNum += 1
        count = 0
        for j in range(SeqNum):
            count += len(S[i][j])
        if count >= minsup:
            p = []
            p.append(i)
            CanNTPI.append([p])
            ItemS[str([p])] = [[] for k in range(SeqNum)]
            ItemS[str([p])] = S[i]

            NTPI.append([p])

    return NTPI, ItemS, CanNTPI


def two_len(NTPI, CanNTPI, ItemS):
    global CanNum
    global GIL
    dicTwoLenPattern = {}

    Item = copy.deepcopy(CanNTPI)
    CanNTPI = []
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

            count, ItemS[str(p)], fsup = Matching_I(ItemS[str(Item[pre])], ItemS[str(Item[suf])], SeqNum,
                                                                strong_num)

            if count >= minsup:
                CanNTPI.append(p)

                if dicTwoLenPattern.get(str([Item[pre][0]])) is None:
                    dicTwoLenPattern[str([Item[pre][0]])] = []
                dicTwoLenPattern[str([Item[pre][0]])].append(p)

                NTPI.append(p)


            else:
                del ItemS[str(p)]
    for m in Item:
        pre = copy.deepcopy(m)
        for n in Item:
            suf = copy.deepcopy(n)
            p = [pre[0], suf[0]]

            CanNum += 1
            count, all_occ = compute_support(ItemS, p)

            if count >= minsup:
                CanNTPI.append(p)
                if dicTwoLenPattern.get(str([pre[0]])) is None:
                    dicTwoLenPattern[str([pre[0]])] = []

                dicTwoLenPattern[str([pre[0]])].append(p)


                NTPI.append(p)

    return CanNTPI, dicTwoLenPattern


def more_len(NTPI, ItemS, ExpSet, ExpSetDict):
    global CanNum
    global flag_p
    global GIL
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
                    if flag_p is True:
                        flag_p = False
                    if pattern == [['c'], ['d'], ['d']]:
                        flag_p = True

                    count, all_occ = compute_support(ItemS, pattern)

                    if count >= minsup:
                        ExpSet.append(pattern)

                        if ExpSetDict.get(str(m)) is None:
                            ExpSetDict[str(m)] = []
                        ExpSetDict[str(m)].append(pattern)

                        NTPI.append(pattern)


                else:
                    pattern = copy.deepcopy(m)
                    pattern[-1].append(n[-1][-1])
                    CanNum += 1

                    if len(pattern) > 1:
                        count, all_occ = compute_support(ItemS, pattern)

                        if count >= minsup:
                            ExpSet.append(pattern)
                            if ExpSetDict.get(str(m)) is None:
                                ExpSetDict[str(m)] = []
                            ExpSetDict[str(m)].append(pattern)


                            NTPI.append(pattern)
                    else:
                        strong_num = 0
                        for item in pattern:
                            for char in item:
                                strong_num += char_membership.get(char, {}).get('Strong', 0)
                        strong_num /= cnt

                        count, ItemS[str(pattern)], fsup = Matching_I(ItemS[str(m)], ItemS[str([[n[-1][-1]]])], SeqNum,
                                                                      strong_num)

                        if count >= minsup:
                            ExpSet.append(pattern)

                            if ExpSetDict.get(str(m)) is None:
                                ExpSetDict[str(m)] = []
                            ExpSetDict[str(m)].append(pattern)

                            NTPI.append(pattern)

                        else:
                            del ItemS[str(pattern)]
        cnt += 1
    return NTPI


def Miner():

    NTPI = []
    ItemS = {}
    global GIL
    GIL = 0


    print(f"\n开始挖掘频繁模式 (最小支持度: {minsup})...")

    NTPI, ItemS, CanNTPI = Mine_ItemS(NTPI, ItemS, sm_item, SeqNum, minsup)


    twoLenPattern, dictTwoLen = two_len(NTPI, CanNTPI, ItemS)

    NTPI = more_len(NTPI, ItemS, twoLenPattern, dictTwoLen)




if __name__ == '__main__':

    dataset_config = [
        ("../../datasets/SDB1.txt", 1233, "../../datasets/SDB1_interest.txt")
    ]

    class Logger(object):
        def __init__(self, filename="运行结果.txt"):
            self.terminal = sys.stdout
            self.log = open(filename, "w", encoding="utf-8")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            pass


    sys.stdout = Logger("NTPI实验结果.txt")

    print("=" * 80)
    print("           开始执行模糊序列模式挖掘算法")
    print("=" * 80)

    for readFileName, minsup, interest_file in dataset_config:
        gc.collect()  

        CanNum = 0

        dataset_name = os.path.basename(readFileName).split(".")[0]

        for var in ['SeqNum', 'S', 'sm_item', 'original_sequences',
                    'char_membership', 'char_category', 'jz_m', 'weights']:
            if var in globals():
                del globals()[var]
        gc.collect()

        print("\n" + "=" * 90)
        print(f" 正在运行 → 数据集：{readFileName}")
        print(f"           最小支持度：{minsup}")
        print(f"           兴趣度文件：{interest_file}")
        print("=" * 90)

        starttime = time.time()
        S = {}

        mem_pdata, (original_sequences, SeqNum, S, sm_item, char_membership, char_category, jz_m, weights) = memory_usage(
            (pdata.datap, (readFileName, S, interest_file)),
            max_iterations=1,
            retval=True
        )

        flag_p = False

        mem_miner = memory_usage((Miner,), max_iterations=1)
        total_mem = mem_pdata + mem_miner
        endtime = time.time()

        print(f" 运行完成：")
        print(f" 数据集：{readFileName}")
        print(f" 支持度：{minsup}")
        print(f" 运行时间：{int(round(endtime * 1000)) - int(round(starttime * 1000))} ms")
        print(f" 总内存消耗：{max(total_mem) - min(total_mem)} MB")
        print("=" * 90 + "\n\n")
