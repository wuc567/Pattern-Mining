import sys
import time
# from memory_profiler import memory_usage

class ntnode():
    def __int__(self, position=0):
        self.position = position
        self.snode = []
        self.pnode = []
a = ntnode()
a.__int__(0)
print(a.position)

def NetGap(pattern):
    print(pattern)
    # pattern_len = len(pattern)
    count = 0
    for i in range(SeqNum):
        Nettree = [[] for k in range(len(pattern))]
        CreatNettree(Nettree, pattern, sdb[i])
        UpdateNettree(Nettree)
        print(Nettree)
        while Nettree[0] != []:
            ShowNettree(Nettree)
            count += 1
            cuttree(Nettree[0][0],Nettree,0)
            UpdateNettree(Nettree)
    return count

def cuttree(node,nettree,levl):
    for i in node.snode:
        i.pnode.remove(node)
    for i in node.pnode:
        i.snode.remove(node)
    if node.snode != []:
        cuttree(node.snode[0],nettree,levl+1)
    print(str(levl) + '：' + str(nettree[levl][0].position))
    nettree[levl].remove(node)
    # nettree[levl].pop(0)

def IfExist(list1, list2):#判断list1是否存在于list2
    for i in list1:
        if i not in list2:
            return 0
    return 1

def CreatNettree(Nettree, pattern, seq):
    for j in range(len(pattern)):
        for i in range(len(seq)):
            if IfExist(pattern[j], seq[i]):
                node = ntnode()
                node.position = i
                node.snode = []
                node.pnode = []
                Nettree[j].append(node)
    for i in range(len(Nettree)-1):
        for j in Nettree[i]:
            k = 0
            while k < len(Nettree[i+1]):
            # for k in range(len(Nettree[i+1])):
                if j.position < Nettree[i + 1][k].position:
                    j.snode.append(Nettree[i + 1][k])
                    Nettree[i + 1][k].pnode.append(j)
                else:
                    if Nettree[i + 1][k].pnode == []:
                        Nettree[i + 1].remove(Nettree[i + 1][k])
                        k = k - 1
                k = k + 1
    # for i in Nettree:
    #     for j in i:
    #         print(str(j.position) + str(j.snode))
    # return Nettree

def UpdateNettree(Nettree):
    i = len(Nettree) - 2
    while i >= 0:
        j = 0
        while j < len(Nettree[i]):
            j += 1
            if Nettree[i][j-1].snode == []:
                if Nettree[i][j-1].pnode != []:
                    for k in Nettree[i][j-1].pnode:
                        k.snode.remove(Nettree[i][j-1])
                print('update:' + str(i) + ':' + str(Nettree[i][j-1].position))
                Nettree[i].pop(j-1)
                j -= 1
        i -= 1



def ShowNettree(Nettree):
    print('%%%%%%%')
    for i in Nettree:
        for j in i:
            print(j.position, end=' ')
        print('\n')
    print('%%%%%%%%%%%%%%%%%')

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
                    count = NetGap(pattern)
                    # count, ItemS[str(pattern)] = ProMatching(ItemS[str(p)], q[-1])
                    # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': ' + str(count))
                    if count >= int(minsup):
                        FP.append(pattern)
                        Temp.append(pattern)
                        # print(str(pattern) + ': ' + str(count))
                        # print(str(pattern) + ': ' + str(ItemS[str(pattern)]) + ': ' + str(count))
                    # else:
                    #     del ItemS[str(pattern)]
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
            # count, ItemS[str(pattern)] = ProMatching(ItemS[str(pre)], suf)
            count = NetGap(pattern)
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
    Mine_ItemS(FP, ItemS)
    # print("Frequent patterns with size=1:" + str(FP))
    # print("Number of frequent patterns with size=1:" + str(len(FP)))
    # print("Number of candidate patterns with size=1:" + str(CanNum))
    # # print(ItemS)
    Mine_Pattern(FP, ItemS)
    # print("Frequent patterns:" + str(FP))
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


# @ti.kernel
if __name__ == '__main__':
    try:
        readFileName = sys.argv[1]
        # minsup = int(sys.argv[2])
    except Exception as e:
        print(e)
    SeqNum, sdb, sort_item = ReadFile(readFileName)
    for minsup in sys.argv[2:]:
        print('SNP-Miner:', readFileName, 'minsup=', minsup, ':')
        starttime = time.time()
        Miner()
        # a = memory_usage((Miner, (int(SeqNum), S, sort_item, int(minsup))))
        endtime = time.time()
        # print('Memory usage: ', max(a) - min(a))
        print("Running time: " + str(int(round(endtime * 1000)) - int(round(starttime * 1000))) + "ms")