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
    list3 = [[] for k in range(SeqNum)]
    count = 0
    for i in range(SeqNum):
        list3[i] = sorted(list(set(list1[i]) & set(list2[i])))
        count += len(list3[i])
    # print(list3)
    # print(count)
    return count, list3


def Matching_S(list1, list2):
    list3 = [[] for k in range(SeqNum)]
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


def Mine_ItemS(UBP, ItemS):  # UBP:频繁模式集(size=1)  ItemS:频繁单项集的出现位置字典
    global CanNum
    for i in sort_item:  # a b c d e f
        CanNum += 1
        count = 0
        for j in range(SeqNum):
            count += len(S[i][j])
        # print(i + ':' + str(count))
        p = []
        p.append(i)
        if count == 0:
            continue

        if compute_utility([p], count):
            UBP.append([p])
            ItemS[str([p])] = [[] for k in range(SeqNum)]
            ItemS[str([p])] = S[i]
            # print(str(p) + ":" + str(ItemS[str(p)]) + ': ' + str(count))
            # print(str(p) + ":" + str(count))
    # print(UBP)
    # del S


def Miner():
    global CanNum
    UBP = []
    ItemS = {}
    Mine_ItemS(UBP, ItemS)
    twoLenPattern = two_len(UBP, ItemS)
    #print(len(twoLenPattern))
    more_len(UBP, ItemS, twoLenPattern)
    # print("Frequent patterns with size=1:" + str(UBP))
    # print("Number of frequent patterns with size=1:" + str(len(UBP)))
    # print("Number of candidate patterns with size=1:" + str(CanNum))
    # # print(ItemS)
    #print("AUNP:" + str(AUNP))

    n = 0
    for i in range(len(maxUtility)):
        if len(MUP[str(i+1)])!=0:
            n += len(MUP[str(i + 1)])
            print(str(MUP[str(i+1)])+":"+str(maxUtility[i]))
    print("Number of MUP:" + str(n))
        #print(i)

    #print("Frequent patterns:" + str(UBP))
    print("Number of UBP:" + str(len(UBP)))
    print("Number of candidate patterns:" + str(CanNum))
    CanNum = 0
    # count(UBP, ItemS)


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
    while ExpSet != []:
        temp = ExpSet[:]
        ExpSet = []

        for m in temp:
            suf = copy.deepcopy(m)
            suf[0].pop(0)
            # print(str(suf))
            # print(m)
            if suf[0] == []:
                sufstr = str(suf[1:])

            else:
                sufstr = str(suf)
            for n in temp:

                pre = copy.deepcopy(n)
                # print(pre)
                pre[-1].pop(-1)
                # print(pre)

                if pre[-1] == []:
                    prestr = str(pre[:-1])
                else:
                    prestr = str(pre)
                if sufstr == prestr:

                    if len(n[-1]) == 1:
                        #if str(m[0][0]) in SItems.keys():  # 剪枝1
                            #if str(n[-1][0]) in SItems[str(m[0][0])].keys():  # 剪枝2
                                pattern = copy.deepcopy(m)
                                pattern.append(n[-1])
                                CanNum += 1
                                # print(pattern)

                                count, ItemS[str(pattern)] = Matching_S(ItemS[str(pattern[:-1])],
                                                                        ItemS[str([pattern[-1]])])
                                if count == 0:
                                    continue

                                if compute_utility(pattern, count):
                                    UBP.append(pattern)
                                    ExpSet.append(pattern)
                                else:
                                    del ItemS[str(pattern)]

                    else:
                        pattern = copy.deepcopy(m)
                        # (pattern)
                        # print(pattern)
                        pattern[-1].append(n[-1][-1])
                        # count = 0
                        # print(pattern)
                        # print("@@@@@")
                        if len(pattern) > 1:
                           # if str(pattern[-1][-1]) in SItems[str(pattern[0][0])].keys():  # 剪枝4
                                CanNum += 1
                                count, ItemS[str(pattern)] = Matching_S(ItemS[str(pattern[:-1])],
                                                                        ItemS[str([pattern[-1]])])
                                if count == 0:
                                    continue

                                if compute_utility(pattern, count):
                                    UBP.append(pattern)
                                    ExpSet.append(pattern)

                                else:
                                    del ItemS[str(pattern)]
                        else:
                            # print(m,n[-1])
                            #if str(pattern[-1][-1]) in SItem[str(pattern[0][0])].keys():  # 剪枝3
                                CanNum += 1
                                count, ItemS[str(pattern)] = Matching_I(ItemS[str(m)], S[str(n[-1][-1])])
                                if count == 0:
                                    continue

                                if compute_utility(pattern, count):
                                    UBP.append(pattern)
                                    ExpSet.append(pattern)

                                else:
                                    del ItemS[str(pattern)]


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
    global minsup,maxau
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
        elif MUP[str(count)] != [] and au == maxUtility[count - 1]: #这是存下了呀MUP  是什么 max utility pattern
            MUP[str(count)].append(pattern)
            return True
        elif au == maxUtility[count - 1]:#
            return True
        elif au + (4-Plen) * maxau * count >= maxUtility[count - 1]:
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
    # readFileName ="./data/SDB1.txt"
    readFileName = sys.argv[1]
    minsup = 0
    maxau = 0
    # minau = 50000
    AUNP = []
    S = {}

    last_index = readFileName.rindex(".")

    dataFileName = readFileName[0:last_index]
    last_index = dataFileName.rindex("/")
    utilityFileName = dataFileName[0:last_index] + "/utility" + dataFileName[last_index:] + "_utility" + ".txt"
    # print(utilityFileName)
    # getUtility(utilityFileName)
    SeqNum, S, sort_item = pdata.datap(readFileName, S)

    del pdata


    getUtility(utilityFileName)
    #print('AUNP-Miner:', readFileName, 'minau=', minau, ':')
    print('CSC-NSP:', readFileName, ':')
    starttime = time.time()
    # Miner()
    a = memory_usage((Miner))
    endtime = time.time()
    print('Memory usage: ', max(a) - min(a))
    print("Running time: " + str(int(round(endtime * 1000)) - int(round(starttime * 1000))) + "ms")
    # print('AUNP-Miner:', readFileName, 'minau=', minau, ':')
    # starttime = time.time()
    # # Miner()
    # a = memory_usage((Miner))
    # endtime = time.time()
    # print('Memory usage: ', max(a) - min(a))
    # print("Running time: " + str(int(round(endtime * 1000)) - int(round(starttime * 1000))) + "ms")
