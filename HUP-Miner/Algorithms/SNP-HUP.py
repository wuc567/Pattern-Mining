import copy
import math
import sys
import time
import json
from collections import defaultdict, OrderedDict

import pandas as pd

import Pdata
# from memory_profiler import memory_usage
pdata = Pdata.processingData()
from memory_profiler import memory_usage
CanNum = 0  #候选模式数量

def GetUnit(itemsets):
    count = 0
    unit = GetIndex(itemsets[0])[:]
    for i in range(1, len(itemsets)):
        index_i = GetIndex(itemsets[i])
        for j in range(SeqNum):
            unit[j] = sorted(list(set(unit[j]) & set(index_i[j])))
    for i in range(SeqNum):
        count += len(unit[i])
    return count, unit

def ProMatching(list1, itemsets):
    a, list2 = GetUnit(itemsets)
    list3 = [[] for k in range (SeqNum)]
    flag = 0
    count = 0
    for i in range(SeqNum):
        for j in range(len(list1[i])):
            if flag == len(list2[i]):
                break
            for k in range(flag, len(list2[i])):
                if list2[i][k] > list1[i][j]:
                    list3[i].append(list2[i][k])
                    count += 1
                    flag = k + 1
                    break
                if k == len(list2[i]) - 1:
                    flag = len(list2[i])
        flag = 0
    return count, list3

def Join_I(FP, ExpSet, ItemS):
    global CanNum
    while ExpSet != []:
        Temp = []
        for p in ExpSet:
            sufP = p[1:]
            for q in ExpSet:
                preQ = q[:len(q)-1]
                if sufP == preQ:
                    pattern = p[:]
                    pattern.append(q[-1])
                    CanNum += 1
                    qq = []
                    qq.append(q[-1])
                    count, ItemS[str(pattern)] = GetUnit(pattern)
                    if count >= int(minsup):
                        FP.append(pattern)
                        compute_utility(pattern, count)
                        Temp.append(pattern)
                        # print(str(pattern) + ":" + str(count))
                        # print(ItemS[str(pattern)])
                    else:
                        del ItemS[str(pattern)]
        ExpSet = Temp[:]

def Gen_I(FP, ItemS):
    global CanNum
    Item = FP[:]
    ExpSet = []   #可扩展集
    for i in range (len(Item)):
        for j in range (i+1, len(Item)):
            pre = Item[i]
            suf = Item[j]
            p = []
            p.append(pre[0])
            p.append(suf[0])
            # print(p)
            # ItemS[str(p)] = [[] for k in range(SeqNum)]
            CanNum += 1
            count, ItemS[str(p)] = GetUnit(p)
            if count >= int(minsup):
                FP.append(p)
                ExpSet.append(p)
                compute_utility(p, count)
                # print(p)
                # print(ItemS[str(p)])
                # print(str(p) + ":" + str(ItemS[str(p)]) + ': ' + str(count))
                # print(str(p) + ":" + str(count))
            else:
                del ItemS[str(p)]
    # print(FP)
    # print(ExpSet)
    # print(ItemS)
    Join_I(FP, ExpSet, ItemS)

def Mine_ItemS(FP, ItemS): #FP:频繁模式集(size=1)  ItemS:频繁单项集的出现位置字典
    global CanNum
    for i in sort_item:  # a b c d e f
        CanNum += 1
        count = 0
        index_i = GetIndex(i)
        for j in range(SeqNum):
            count += len(index_i[j])
        # print(i + ':' + str(count))
        if count >= int(minsup):
            p = []
            p.append(i)
            FP.append(p)
            compute_utility(p, count)
            ItemS[str(p)] = [[] for k in range(SeqNum)]
            ItemS[str(p)] = index_i
            # print(str(p) + ":" + str(index_i) + ': ' + str(count))
            # print(str(p) + ":" + str(count))
    # print(FP)
    # del S
    Gen_I(FP, ItemS)

def Join_S(FP, ExpSet, ItemS):
    global CanNum
    while ExpSet != []:
        Temp = []
        for p in ExpSet:
            for q in ExpSet:
                sufP = p[1:]
                preQ = q[:len(q)-1]
                if sufP == preQ:
                    pattern = p[:]
                    pattern.append(q[-1])
                    CanNum += 1
                    count, ItemS[str(pattern)] = ProMatching(ItemS[str(p)], q[-1])
                    # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': ' + str(count))
                    if count >= int(minsup):
                        FP.append(pattern)
                        Temp.append(pattern)
                        compute_utility(pattern, count)
                        # print(str(pattern) + ': ' + str(count))
                        # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': ' + str(count))
                    else:
                        del ItemS[str(pattern)]
        ExpSet = Temp[:]

def Mine_Pattern(FP, ItemS):
    global CanNum
    ExpSet = []
    temp = FP[:]
    for pre in temp:
        for suf in temp:
            # pattern = []
            # pattern.append(pre)
            # pattern.append(suf)
            pattern = [pre, suf]
            CanNum += 1
            count, ItemS[str(pattern)] = ProMatching(ItemS[str(pre)], suf)
            if count >= int(minsup):
                FP.append(pattern)
                compute_utility(pattern, count)
                ExpSet.append(pattern)
                # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': '+ str(count))
                # print(str(pattern) + ': ' + str(count))
            else:
                del ItemS[str(pattern)]
    # print(FP)
    # print(ExpSet)
    Join_S(FP, ExpSet, ItemS)


def Miner():
    FP = []
    ItemS = {}
    Mine_ItemS(FP, ItemS)
    # print("Frequent patterns with size=1:" + str(FP))
    # print("Number of frequent patterns with size=1:" + str(len(FP)))
    # print("Number of candidate patterns with size=1:" + str(CanNum))
    # # print(ItemS)
    Mine_Pattern(FP, ItemS)
    # print("Frequent patterns:" + str(FP))
    print ("Number of AUNP patterns: " + str(len(AUNP)))
    print("Number of frequent patterns:" + str(len(FP)))
    print("Number of candidate patterns:" + str(CanNum))

def GetIndex(item):
    index2 = []
    for seq in sdb:
        index = []
        for i in range(len(seq)):
            if item in seq[i]:
                index.append(i)
        index2.append(index)
    return index2

def ReadFile(readFileName):
    SeqNum = 0
    sdb = []
    sort_item = []
    itemset = []
    seq = []
    with open(readFileName, 'r') as f:
        lines = f.readlines()
        for line in lines:
            SeqNum += 1
            items_array = line.strip().split(' ')
            for item in items_array:
                if item != '-1':
                    itemset.append(item)
                    if item not in sort_item:
                        sort_item.append(item)
                else:
                    seq.append(itemset)
                    itemset = []
            seq.append(itemset)
            itemset = []
            sdb.append(seq)
            seq = []
        sort_item.sort()
    return SeqNum, sdb, sort_item

def getUtility(utilityFileName):
    global Utility
    global minsup
    maxau = 0
    pdata = Pdata.processingData()
    lines = pdata.read_file(utilityFileName)
    for line in lines:
        str = line.split(' ')
        Utility[str[0]] = int(str[1])
        if int(str[1]) > maxau:
            maxau = int(str[1])
    # 向上取整
    minsup = math.ceil(int(minau) / maxau)

    # print(Utility)


# @ti.kernel

def compute_utility(pattern, count):
    global AUNP
    au = 0
    len = 0
    for i in pattern:

        for j in i:
            len += 1
            au += Utility[str(j)]
    au = au * count / len
    if au >= int(minau):
        AUNP.append(pattern)
# @ti.kernel
if __name__ == '__main__':
    try:
        readFileName = sys.argv[1]
        # minsup = int(sys.argv[2])
    except Exception as e:
        print(e)
        exit(0)
        # readFileName = "../data/SDB2.txt"
    minsup = 0
    # minau = 50000
    AUNP = []
    Utility = {}
    last_index = readFileName.rindex(".")

    dataFileName = readFileName[0:last_index]
    last_index = dataFileName.rindex("/")
    utilityFileName = dataFileName[0:last_index] + "/utility" + dataFileName[last_index:] + "_utility" + ".txt"
    SeqNum, sdb, sort_item = ReadFile(readFileName)
    for minau in sys.argv[2:]:
        getUtility(utilityFileName)
        print('SNP-AUNP:', readFileName, 'minau=', minau, ':')

        starttime = time.time()
        # Miner()
        a = memory_usage((Miner))
        endtime = time.time()
        print('Memory usage: ', max(a) - min(a))
        print("Running time: " + str(int(round(endtime * 1000)) - int(round(starttime * 1000))) + "ms")