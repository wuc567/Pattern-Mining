import sys
import time
import json
from collections import defaultdict, OrderedDict
import Pdata
#import xlwt
import pandas as pd
pdata = Pdata.processingData()
# from memory_profiler import memory_usage

# import taichi as ti
# ti.init()

# @ti.kernel
CanNum = 0  #候选模式数量

# @ti.func
def Matching_I(list1, list2):
    list3 = [[] for k in range (SeqNum)]
    count = 0
    for i in range (SeqNum):
        list3[i] = sorted(list(set(list1[i]) & set(list2[i])))
        count += len(list3[i])
    # print(list3)
    # print(count)
    return count, list3

def Matching_S(list1, list2):
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
                    count, ItemS[str(pattern)] = Matching_I(ItemS[str(p)], ItemS[str(qq)])
                    if count >= int(minsup):
                        FP.append(pattern)
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
            count, ItemS[str(p)] = Matching_I(ItemS[str(pre)], ItemS[str(suf)])
            if count >= int(minsup):
                FP.append(p)
                ExpSet.append(p)
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
        for j in range(SeqNum):
            count += len(S[i][j])
        # print(i + ':' + str(count))
        if count >= int(minsup):
            p = []
            p.append(i)
            FP.append(p)
            ItemS[str(p)] = [[] for k in range(SeqNum)]
            ItemS[str(p)] = S[i]
            # print(str(p) + ":" + str(ItemS[str(p)]) + ': ' + str(count))
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
                    count, ItemS[str(pattern)] = Matching_S(ItemS[str(p)], ItemS[str(q[-1])])
                    # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': ' + str(count))
                    if count >= int(minsup):
                        FP.append(pattern)
                        Temp.append(pattern)
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
            count, ItemS[str(pattern)] = Matching_S(ItemS[str(pre)], ItemS[str(suf)])
            if count >= int(minsup):
                FP.append(pattern)
                ExpSet.append(pattern)
                # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': '+ str(count))
                # print(str(pattern) + ': ' + str(count))
                # print(str(pattern) + ' ' + str(ItemS[str(pattern)]))
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
    print("Frequent patterns:" + str(FP))
    # count(FP, ItemS)
    print("Number of frequent patterns:" + str(len(FP)))
    print("Number of candidate patterns:" + str(CanNum))

# def count(FP, ItemS):
#     sum = {}
#     sum1 = {}
#     for i in FP:
#         i = str(i)
#         sum[i] = []
#         sum1[i] = []
#         for j in ItemS[i]:
#             sum[i].append(len(j))
#             if len(j)>0:
#                 sum1[i].append(1)
#             else:
#                 sum1[i].append(len(j))
#     sum = pd.DataFrame(data=sum)
#     sum1 = pd.DataFrame(data=sum1)
#     sum.to_excel('RNP-19.xlsx')
#     sum1.to_excel('FP-19.xlsx')
#     print(sum)

# @ti.kernel
if __name__ == '__main__':
    try:
        readFileName = sys.argv[1]
        # minsup = int(sys.argv[2])
    except Exception as e:
        print(e)
    # readFileName = "dataset/demo/E-Shop.txt"
    # minsup = 33333
    S = {}
    SeqNum, S, sort_item = pdata.datap(readFileName, S)
    # print(len(sort_item))
    # print(sort_item)
    del pdata
    for minsup in sys.argv[2:]:
        print('NFP-Miner:', readFileName, 'minsup=', minsup, ':')
        starttime = time.time()
        Miner()
        # a = memory_usage((Miner, (int(SeqNum), S, sort_item, int(minsup))))
        endtime = time.time()
        # print('Memory usage: ', max(a) - min(a))
        print ("Running time: " + str(int(round(endtime * 1000)) - int(round(starttime * 1000))) + "ms")
