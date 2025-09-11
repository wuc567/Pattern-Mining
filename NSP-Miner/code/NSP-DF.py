import copy
import sys
import time

import pandas as pd

from datap import Pdata
pdata = Pdata.processingData()
from memory_profiler import memory_usage

# import taichi as ti
# ti.init()

# @ti.kernel
CanNum = 0  # 候选模式数量
SItem = {}  # Size=1的频繁模式剪枝字典
SItems = {}  # Size=2的频繁模式剪枝字典
maxUtility = []
MUP = {}


def campute_PreSuf(pattern):
    global SItem, SItems
    if len(pattern[0]) > 1:
        if str(pattern[0][0]) not in SItem:
            SItem[str(pattern[0][0])] = {}
        SItem[str(pattern[0][0])][str(pattern[0][1])] = ''
    else:
        if str(pattern[0][0]) not in SItems:
            SItems[str(pattern[0][0])] = {}
        SItems[str(pattern[0][0])][str(pattern[1][0])] = ''


# @ti.func
def Matching_I(list1, list2):
    list3 = [0 for i in range(SeqNum)]
    count = 0
    for i in range(SeqNum):
        list3[i] = list1[i] & list2[i]
        count += list3[i].bit_count()
    # print(list3)
    # print(count)
    return count, list3


def Matching_S(list1, list2):
    list3 = [0 for i in range(SeqNum)]
    flag = 0
    count = 0
    for i in range(SeqNum):
        site = 0
        tmp1 = list1[i] >> 1
        tmp2 = list2[i]
        while tmp1 > 0 and tmp2 > 0:
            tmp = tmp1 & tmp2
            if tmp != 0:
                tmp1 ^= tmp
                tmp2 ^= tmp
                site |= tmp
                #tmp1 ^= 1
                if tmp1.bit_length() < (tmp2 & -tmp2).bit_length():
                    break
            tmp1 >>= 1

        count += site.bit_count()
        list3[i] = site

    return count, list3


def Mine_ItemS(UBP, ItemS):  # UBP:频繁模式集(size=1)  ItemS:频繁单项集的出现位置字典
    global CanNum
    for i in sort_item:  # a b c d e f
        CanNum += 1
        count = 0
        for j in range(SeqNum):
            count += S[i][j].bit_count()
        # print(i + ':' + str(count))
        p = []
        p.append(i)
        if count == 0:
            continue

        if compute_utility([p], count):
            UBP1.append(p[0])
            UBP.append([p])
            ItemS[str([p])] = S[i].copy()
            # print(str(p) + ":" + str(ItemS[str(p)]) + ': ' + str(count))
            # print(str(p) + ":" + str(count))
    # print(UBP)
    # del S


def Miner():
    global CanNum, UBP, CandiNum

    ItemS = {}
    Mine_ItemS(UBP, ItemS)
    Item = copy.deepcopy(UBP)
    for i in Item:
        DeepMiner(UBP, i, ItemS)
    #twoLenPattern = two_len(UBP, ItemS)
    #print(len(twoLenPattern))
    #more_len(UBP, ItemS, twoLenPattern)
    # print("Frequent patterns with size=1:" + str(UBP))
    # print("Number of frequent patterns with size=1:" + str(len(UBP)))
    # print("Number of candidate patterns with size=1:" + str(CanNum))
    # # print(ItemS)
    #print("AUNP:" + str(AUNP))

    CandiNum = CanNum
    CanNum = 0
    # count(UBP, ItemS)


def DeepMiner(UBP, pattern, ItemS):
    global CanNum
    Item = copy.deepcopy(UBP1)
    for m in Item:
        pre = copy.deepcopy(pattern)
        suf = m
        if m not in pre[-1] and str(m) > str(pre[-1][-1]):
            p = copy.deepcopy(pre)
            p[-1].append(suf)
            if len(pre) == 1:
                CanNum += 1
                count, ItemS[str(p)] = Matching_I(ItemS[str(pre)], S[str(suf)])
                if count != 0 and compute_utility(p, count):
                    UBP.append(p)
                    DeepMiner(UBP, p, ItemS)
            else:
                CanNum += 1
                count, ItemS[str([p[-1]])] = Matching_I(ItemS[str([p[-1][:-1]])],
                                                               S[str(p[-1][-1])])
                count, ItemS[str(p)] = Matching_S(ItemS[str(p[:-1])], ItemS[str([p[-1]])])
                if count != 0 and compute_utility(p, count):
                    UBP.append(p)
                    DeepMiner(UBP, p, ItemS)
        p = copy.deepcopy(pre)
        p.append([suf])
        CanNum += 1
        count, ItemS[str(p)] = Matching_S(ItemS[str(p[:-1])], ItemS[str([p[-1]])])
        if count != 0 and compute_utility(p, count):
            UBP.append(p)
            DeepMiner(UBP, p, ItemS)


def two_len(UBP, ItemS):
    '''
    生成频繁模式集size=2,[ab],[a][b]
    :return:
    '''
    global CanNum
    twoLenPattern = []
    Item = copy.deepcopy(UBP)
    for pre in range(len(Item)):
        for suf in range(pre + 1, len(Item)):
            t = copy.deepcopy(Item[pre][0])
            t.append(Item[suf][0][0])
            p = [t]
            CanNum += 1
            count, ItemS[str(p)] = Matching_I(ItemS[str(Item[pre])], ItemS[str(Item[suf])])
            if count == 0:
                continue

            if compute_utility(p, count):
                UBP.append(p)
                campute_PreSuf(p)
                twoLenPattern.append(p)

            else:
                del ItemS[str(p)]
    for m in Item:
        pre = copy.deepcopy(m)
        for n in Item:
            suf = copy.deepcopy(n)
            p = [pre[0], suf[0]]
            CanNum += 1
            count, ItemS[str(p)] = Matching_S(ItemS[str(pre)], ItemS[str(suf)])
            if count == 0:
                continue

            if compute_utility(p, count):
                UBP.append(p)
                campute_PreSuf(p)
                twoLenPattern.append(p)

            else:
                del ItemS[str(p)]

    return twoLenPattern


def more_len(UBP, ItemS, ExpSet):
    '''
    生成频繁模式集size>2
    :return:
    '''
    # ExpSet = Exppattern[:]
    global CanNum
    Item = copy.deepcopy(UBP1)
    while ExpSet != []:
        temp = ExpSet[:]
        ExpSet = []

        for m in temp:
            for n in Item:

                # print(pre)
                pattern = copy.deepcopy(m)
                pattern1 = copy.deepcopy(m)
                pattern.append([n])
                CanNum += 1
                # print(pattern)
                count, ItemS[str(pattern)] = Matching_S(ItemS[str(pattern[:-1])],
                                                        ItemS[str([pattern[-1]])])
                if count != 0 and compute_utility(pattern, count):
                    UBP.append(pattern)
                    ExpSet.append(pattern)
                elif count != 0:
                    del ItemS[str(pattern)]

                if n not in m[-1] and str(n) > str(m[-1][-1]):

                    pattern1[-1].append(n)
                    if len(pattern1) == 1:
                        count, ItemS[str(pattern1)] = Matching_I(ItemS[str(m)], S[str(n)])
                    else:
                        count, ItemS[str([pattern1[-1]])] = Matching_I(ItemS[str([pattern1[-1][:-1]])],
                                                                       S[str(pattern1[-1][-1])])
                        count, ItemS[str(pattern1)] = Matching_S(ItemS[str(pattern1[:-1])], ItemS[str([pattern1[-1]])])
                    if count != 0 and compute_utility(pattern1, count):
                        UBP.append(pattern1)
                        ExpSet.append(pattern1)

                    elif count != 0:
                        del ItemS[str(pattern1)]


def count(UBP, ItemS):
    SeqSup = {}
    for i in UBP:
        SeqSup[str(i)] = []
        for j in ItemS[str(i)]:
            SeqSup[str(i)].append(len(j))
    # 将字典写入excel
    # import pandas as pd
    df = pd.DataFrame(SeqSup)
    strlist = readFileName.split('/')
    while strlist != []:
        str1 = strlist.pop(0)
    str1 = str1.split('.')[0]

    df.to_excel(str1 + 'SeqSup.xlsx', sheet_name='sheet1')


Utility = {}


def getUtility(utilityFileName):
    global Utility
    global minsup, maxau
    pdata = Pdata.processingData()
    lines = pdata.read_file(utilityFileName)
    for line in lines:
        str = line.split(' ')
        Utility[str[0]] = int(str[1])
        if int(str[1]) > maxau:
            maxau = int(str[1])
    # 向上取整
    #minsup = math.ceil(int(minau) / maxau)

    # print(Utility)


# @ti.kernel

def compute_utility(pattern, count):
    global MUP, maxUtility
    Plen = 0
    au = 0
    l = 0
    for i in pattern:
        Plen += len(i)
        for j in i:
            l += 1
            au += Utility[str(j)]
    au = au * count
    if Plen > 4:
        return False
    if len(maxUtility) == 0:
        for i in range(count):
            maxUtility.append(au)
            MUP[str(i + 1)] = []
        MUP[str(count)] = [pattern]
        return True
    elif count <= len(maxUtility):
        if au > maxUtility[count - 1]:
            MUP[str(count)] = [pattern]
            maxUtility[count - 1] = au
            count -= 1
            while au >= maxUtility[count - 1] and count > 0:
                maxUtility[count - 1] = au
                MUP[str(count)] = []
                count -= 1

            return True
        elif MUP[str(count)] != [] and au == maxUtility[count - 1]:  # 这是存下了呀MUP  是什么 max utility pattern
            MUP[str(count)].append(pattern)
            return True
        elif au == maxUtility[count - 1]:  #
            return True
        elif au + (4 - Plen) * maxau * count >= maxUtility[count - 1]:
            return True
        else:
            return False


    else:
        start = 0
        while start < len(maxUtility):
            if au > maxUtility[start]:
                maxUtility[start] = au
                MUP[str(start + 1)] = []
            start += 1

        for i in range(start, count):
            maxUtility.append(au)
            MUP[str(i + 1)] = []
        MUP[str(count)] = [pattern]
        return True
        # print(pattern)
        # print(au)


if __name__ == '__main__':
    # try:
    #     readFileName = sys.argv[1]
    #     # minsup = int(sys.argv[2])
    # except Exception as e:
    #     print(e)
    #     exit(0)
    # readFileName = "../data/SDB2.txt"
    # readFileName = "./data/SDB1.txt"

    readFileName = sys.argv[1]
    minsup = 0
    maxau = 0
    UBP1 = []
    # minau = 50000
    AUNP = []
    S = {}
    UBP = []
    last_index = readFileName.rindex(".")
    CandiNum = 0
    dataFileName = readFileName[0:last_index]
    last_index = dataFileName.rindex("/")
    utilityFileName = dataFileName[0:last_index] + "/utility" + dataFileName[last_index:] + "_utility" + ".txt"
    # print(utilityFileName)
    # getUtility(utilityFileName)
    SeqNum, S, sort_item = pdata.dataBin(readFileName, S)

    del pdata

    getUtility(utilityFileName)
    #print('AUNP-Miner:', readFileName, 'minau=', minau, ':')
    print('NSP-DF:', readFileName, ':')
    starttime = time.time()
    # Miner()
    a = memory_usage((Miner))
    endtime = time.time()
    print('Memory usage: ', max(a) - min(a))
    n = 0
    for i in range(len(maxUtility)):
        if len(MUP[str(i + 1)]) != 0:
            n += len(MUP[str(i + 1)])
            print(str(MUP[str(i + 1)]) + "支持度为" + ":" + str(i + 1) + "效用为：" + str(maxUtility[i]))
    print("Number of MUP:" + str(n))
    # print(i)

    # print("Frequent patterns:" + str(UBP))
    print("Number of UBP:" + str(len(UBP)))
    # print(UBP)
    print("Number of candidate patterns:" + str(CandiNum))
    print("Running time: " + str(int(round(endtime * 1000)) - int(round(starttime * 1000))) + "ms")
    # print('AUNP-Miner:', readFileName, 'minau=', minau, ':')
    # starttime = time.time()
    # # Miner()
    # a = memory_usage((Miner))
    # endtime = time.time()
    # print('Memory usage: ', max(a) - min(a))
    # print("Running time: " + str(int(round(endtime * 1000)) - int(round(starttime * 1000))) + "ms")
