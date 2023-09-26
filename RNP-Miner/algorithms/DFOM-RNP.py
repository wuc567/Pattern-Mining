import sys
import time
import json
from collections import defaultdict, OrderedDict
import Pdata
pdata = Pdata.processingData()
# from memory_profiler import memory_usage

CanNum = 0  #候选模式数量

#计算单项集模式的支持度
def Matching_I(list1, list2):
    list3 = [[] for k in range (SeqNum)]
    count = 0
    for i in range (SeqNum):
        list3[i] = sorted(list(set(list1[i]) & set(list2[i])))
        count += len(list3[i])
    # print(list3)
    # print(count)
    return count, list3

#计算多项集模式的支持度
def DFOM(pattern, ItemS):
    # print(str(pattern))
    count = 0
    Nettree = [[[] for i in range(SeqNum)] for k in range(len(pattern))]
    unit = [[] for k in range(len(pattern))]
    for i in range(len(pattern)):
        unit[i] = ItemS[str(pattern[i])]
    # print(unit)
    for i in range(SeqNum):
        for m in range(len(unit[0][i])):
            bbb = 0
            Nettree[0][i].append(unit[0][i][m])
            for j in range(1, len(unit)):
                n = 1
                if unit[j][i] == []:
                    bbb = 1
                    break
                else:
                    for k in range(len(unit[j][i])):
                        if Nettree[j][i] == []:
                            aaa = -1
                        else:
                            aaa = Nettree[j][i][-1]
                        if unit[j][i][k] > Nettree[j - 1][i][-1] and unit[j][i][k] > aaa:
                            Nettree[j][i].append(unit[j][i][k])
                            if j == len(unit) - 1:
                                count += 1
                            n = 0
                            break
                    if n:
                        bbb = 1
                        break
            if bbb:
                break
    # print(str(count))
    return count


#挖掘频繁单项集模式（m长度 m>1，1大小）例如：[abc]
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

#挖掘频繁单项集模式（2长度。1大小）例如：[ab]
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

# 挖掘频繁单项（1长度，1大小）例如：[a]
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

## 挖掘size>2的多项集模式（通过模式连接得到）
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
                    # count, ItemS[str(pattern)] = Matching_S(ItemS[str(p)], ItemS[str(q[-1])])
                    count = DFOM(pattern, ItemS)
                    # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': ' + str(count))
                    if count >= int(minsup):
                        FP.append(pattern)
                        Temp.append(pattern)
                        # print(str(pattern) + ': ' + str(count))
                        # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': ' + str(count))
                    # else:
                    #     del ItemS[str(pattern)]
        ExpSet = Temp[:]

# 挖掘size=2的多项集模式（通过两两拼接枚举得到）
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
            # count, ItemS[str(pattern)] = Matching_S(ItemS[str(pre)], ItemS[str(suf)])
            count = DFOM(pattern, ItemS)
            if count >= int(minsup):
                FP.append(pattern)
                ExpSet.append(pattern)
                # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': '+ str(count))
                # print(str(pattern) + ': ' + str(count))
            # else:
            #     del ItemS[str(pattern)]
    # print(FP)
    # print(ExpSet)
    Join_S(FP, ExpSet, ItemS)


def Miner():
    FP = []
    ItemS = {}
    Mine_ItemS(FP, ItemS) #挖掘频繁单项集模式，例如：[a], [ab], [abc]... 出现位置存储在ItemS[str(itemset)]
    # print("Frequent patterns with size=1:" + str(FP))
    # print("Number of frequent patterns with size=1:" + str(len(FP)))
    # print("Number of candidate patterns with size=1:" + str(CanNum))
    # # print(ItemS)
    Mine_Pattern(FP, ItemS) #挖掘频繁多项集模式, (size>=2). 例如：[a][ab], [a][a][ab]... 无需存储位置
    # print("Frequent patterns:" + str(FP))
    print("Number of frequent patterns:" + str(len(FP)))
    print("Number of candidate patterns:" + str(CanNum))

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
        print('DFOM-M:', readFileName, 'minsup=', minsup, ':')
        starttime = time.time()
        Miner()
        # a = memory_usage((Miner, (int(SeqNum), S, sort_item, int(minsup))))
        endtime = time.time()
        # print('Memory usage: ', max(a) - min(a))
        print ("Running time: " + str(int(round(endtime * 1000)) - int(round(starttime * 1000))) + "ms")