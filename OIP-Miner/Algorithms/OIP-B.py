import dataprocess as dp
import time
import copy
import operator
from memory_profiler import memory_usage

supthreshold=0.3
k=1  #遗忘因子
candi=[]
longcandi=[]
minsup=0
minsupsum=0
orgminsup=0
itemsetnum=0
itemsetnumsum=0
dataTable={}
dataTable1={}
orgdataTable=[]
orgdataTable1=[]
num=0
finaldict={}
orgdict={}
oneitem=[]
cannum=0
f=0
g=0

class CanPattern():
    def __init__(self,data):
        self.data=data
        self.prefix=[]
        self.suffer=[]

class FrePattern():
    def __init__(self,data,sup,t):
        self.data=data
        self.sup =sup
        self.tag=t

# 计算支持度
def sc(pp):
    """
    计算支持度

    :param pp: 模式pattern的出现位置纪录
    :return: 返回该模式的支持度
    """
    sv = 0
    for si in pp.keys():
        sv += len(pp[si])
    return sv

# 求两个列表的交集
def inter(a, b):
    res=[item for item in a if item in b]
    return res

# 计算项数
def lenPattern(p):
    """
    计算模式pattern长度 ：pattern中项的个数

    :param pattern: 模式pattern
    :return: 模式pattern的长度：各项集中项数之和
    """
    l = 0
    for i in p:
        l += len(i)
    return l

# 一次性判断
def oneOff(itemset, pos, itempos):
    for item in itemset:
        if itempos[item][pos]:
            return False
    return True

# 计算单个模式在数据库中的出现位置
def singleposition(pattern,dataTable,dataTable1):
    a=0
    patternAllPosition = []
    itempos = {}
    lst = list(set(sum(pattern, [])))
    p_t=tuple(map(tuple, pattern))
    for ps in dataTable[lst[0]].keys():
        point = []
        for i in range(len(p_t)):
            point.append(0)
            if p_t[i] in dataTable1.keys():
                if ps in dataTable1[p_t[i]].keys():
                    pos=dataTable1[p_t[i]][ps][:]
                else:
                    patternAllPosition.clear()
                    break
            else:
                if ps in dataTable[p_t[i][0]].keys():
                    pos=dataTable[p_t[i][0]][ps][:]
                else:
                    patternAllPosition.clear()
                    break
                for item in p_t[i][1:]:
                    if ps in dataTable[item].keys():
                        pos=inter(pos,dataTable[item][ps][:])
                    else:
                        pos=[]
                        break
            if pos:
                patternAllPosition.append(pos)
            else:
                patternAllPosition.clear()
                break
        # print(patternAllPosition)
        if patternAllPosition != []:
            for item in lst:
                itempos[item]= {i: 0 for i in dataTable[item][ps][:]}
            # print(itempos)
            flag = 1
            while point[0]<len(patternAllPosition[0]):
                # 对每个序列的第一个项集进行查找可以使用的位置
                while a!=0 and not oneOff(pattern[0],patternAllPosition[0][point[0]],itempos):
                    point[0]+=1
                    if point[0]==len(patternAllPosition[0]):
                        # 若第一个项集没有可扩展的位置时，flagWhile = 0
                        flag = 0
                        break
                if flag:
                    for item in pattern[0]:
                        itempos[item][patternAllPosition[0][point[0]]]=1
                    temp=patternAllPosition[0][point[0]]
                    # occurrencePosition.append([patternAllPosition[0][point[0]]])
                    point[0]+=1
                else:
                    break
                i = 1
                # 对第二个项集及以后的项集进行选择 满足一次性的位置
                while i < len(pattern):
                    if point[i]<len(patternAllPosition[i]):
                        if a!=0:
                            while patternAllPosition[i][point[i]] <= temp or not oneOff(pattern[i], patternAllPosition[i][point[i]], itempos):
                                point[i]+=1
                                if point[i]==len(patternAllPosition[i]):
                                    # 若第i+1个项集没有可扩展的位置时，flagWhile = 0
                                    flag = 0
                                    break
                        else:
                            while patternAllPosition[i][point[i]] <= temp:
                                point[i]+=1
                                if point[i]==len(patternAllPosition[i]):
                                    # 若第i+1个项集没有可扩展的位置时，flagWhile = 0
                                    flag = 0
                                    break
                    else:
                        # 若第i+1个项集没有可扩展的位置时，flagWhile = 0
                        flag = 0
                        break
                    if flag:
                        # flagWhile=1，本次循环产生完整的模式出现位置，将其记录在occurrencePosition中
                        for item in pattern[i]:
                            itempos[item][patternAllPosition[i][point[i]]] = 1
                        temp=patternAllPosition[i][point[i]]
                        # occurrencePosition.append([patternAllPosition[i][point[i]]])
                        point[i]+=1
                        i += 1
                if flag:
                    a+=1
                else:
                    break
            patternAllPosition.clear()
    return a

# 在整体的支持度
def sumsupport(key,item,pattern,t,support):
    tag=0
    if key in orgdict.keys():
        if (item,t) in orgdict[key].keys():
            tag = 1
            support+=orgdict[key][(item,t)]
            if support>=minsupsum:
                orgdict[key][(item,t)]=0
            else:
                orgdict[key].pop((item,t))
    if tag==0:
        lst = list(set(sum(pattern, [])))
        for n in range(len(orgdataTable)):
            lst1 = inter(lst, orgdataTable[n].keys())
            if len(lst) == len(lst1):
                support += singleposition(pattern, orgdataTable[n],orgdataTable1[n]) * k**(num - n)
    return support

# 生成一长度频繁模式
def onepattern():
    global cannum,f,dataTable1
    finaldict[()]={}
    for item in dataTable.keys():
        cannum+=1
        # print(item)
        support=sc(dataTable[item])
        if support>=minsup:
            tag=0
            if () in orgdict.keys():
                if (item,'s') in orgdict[()]:
                    tag=1
                    support += orgdict[()][(item,'s')]
                    if support>=minsupsum:
                        orgdict[()][(item,'s')]=0
                    else:
                        orgdict[()].pop((item,'s'))
            if tag==0:
                for i in range(len(orgdataTable)):
                    if item in orgdataTable[i]:
                        support += sc(orgdataTable[i][item]) * k**(num - i)
            if support >= minsupsum:
                dataTable1[tuple([item])]=dataTable[item]
                finaldict[()][(item,'s')]=support
                candi.append([item])
                oneitem.append(item)

# 生成2长度的模式
def one_to_two():
    global cannum,a,f
    i = 0
    while i < len(candi):
        tp = candi[i][:]
        finaldict[tp[0]]={}
        j = 0
        while j < len(candi):
            ad = candi[j][:]
            tmp = []
            if i < j:
                tmp.append(tp + ad)
                key_tuple = tuple(map(tuple, tmp))
                cannum+=1
                support=0
                seq=inter(dataTable[tmp[0][0]].keys(),dataTable[tmp[0][1]].keys())
                for s in seq:
                    support+=len(inter(dataTable[tmp[0][0]][s],dataTable[tmp[0][1]][s]))
                if support>=minsup:
                    support=sumsupport(tp[0],ad[0],tmp,'i',support)
                    if support >= minsupsum:
                        for s in seq:
                            if key_tuple[0] not in dataTable1.keys():
                                dataTable1[key_tuple[0]]={}
                                dataTable1[key_tuple[0]][s]=inter(dataTable[tmp[0][0]][s],dataTable[tmp[0][1]][s])
                            else:
                                dataTable1[key_tuple[0]][s]=inter(dataTable[tmp[0][0]][s],dataTable[tmp[0][1]][s])
                        longcandi.append(tmp)
                        finaldict[tp[0]][(ad[0],'i')]=support
            tmp = []
            tmp.append(tp)
            tmp.append(ad)
            cannum += 1
            support = singleposition(tmp,dataTable,dataTable1)
            if support>=minsup:
                support = sumsupport(tp[0], ad[0], tmp, 's', support)
                if support >= minsupsum:
                    longcandi.append(tmp)
                    finaldict[tp[0]][(ad[0],'s')]=support
            j += 1
        i += 1
        if finaldict[tp[0]]=={}:
            finaldict.pop(tp[0])
    candi.clear()

# 广度优先方式生成候选模式
def breadthfirst():
    global cannum
    while longcandi:
        if lenPattern(longcandi[0])==1:
            key_tuple=longcandi[0][0][0]
            if key_tuple not in finaldict:
                finaldict[key_tuple]={}
        else:
            key_tuple=tuple(map(tuple,longcandi[0]))
            if key_tuple not in finaldict:
                finaldict[key_tuple]={}
        pa=longcandi[0]
        for item in oneitem:
            flag=True
            tmp=copy.deepcopy(pa)
            if flag==True:
                tmp.append([item])
                cannum+=1
                support=singleposition(tmp,dataTable,dataTable1)
                if support>=minsup:
                    support=sumsupport(key_tuple,item,tmp,'s',support)
                    if support>=minsupsum:
                        longcandi.append(tmp)
                        finaldict[key_tuple][(item,'s')]=support
                if item>pa[-1][-1]:
                    tmp=copy.deepcopy(pa)
                    if len(tmp)==1:
                        flag1=True
                    else:
                        flag1=False
                    tmp[-1].append(item)
                    cannum += 1
                    if flag1==True:
                        pre=tuple(tmp[0][:-1])
                        suf=tuple(tmp[0][1:])
                        support = 0
                        seq=[]
                        if pre in dataTable1 and suf in dataTable1:
                            seq = inter(dataTable1[pre].keys(), dataTable1[suf].keys())
                            for s in seq:
                                support += len(inter(dataTable1[pre][s], dataTable1[suf][s]))
                        else:
                            support = singleposition(tmp, dataTable, dataTable1)
                        if support >= minsup:
                            support = sumsupport(key_tuple, item, tmp, 'i', support)
                            if support >= minsupsum:
                                key_tuple1=tuple(map(tuple,tmp))
                                for s in seq:
                                    if key_tuple1[0] not in dataTable1.keys():
                                        dataTable1[key_tuple1[0]] = {}
                                        dataTable1[key_tuple1[0]][s] = inter(dataTable1[pre][s],dataTable1[suf][s])
                                    else:
                                        dataTable1[key_tuple1[0]][s] = inter(dataTable1[pre][s],dataTable1[suf][s])
                                longcandi.append(tmp)
                                finaldict[key_tuple][(item,'i')] = support
                    else:
                        support=singleposition(tmp,dataTable,dataTable1)
                        if support>=minsup:
                            support=sumsupport(key_tuple,item,tmp,'i',support)
                            if support>=minsupsum:
                                longcandi.append(tmp)
                                finaldict[key_tuple][(item,'i')]=support
        longcandi.pop(0)

# 读文件
def readfile(file):
    global minsup,dataTable,itemsetnum,bufsup
    fileresult = dp.operateDataFile2(file)
    itemsetnum = fileresult[1]
    dataTable={}
    keys=[]
    for item in fileresult[0]:
        keys.append(item)
    keys.sort()
    for key in keys:
        dataTable[key] = fileresult[0][key]
    minsup = itemsetnum * supthreshold

# 深度处理原始字典树
def orgdicttree():
    global f
    for elem in orgdict[()]:
        if orgdict[()][elem]!=0:
            if orgdict[()][elem]>=orgminsup:
                support=orgdict[()][elem]
                if elem[0] in dataTable:
                    support += sc(dataTable[elem[0]])
                if support>=minsupsum:
                    finaldict[()][elem]=support
                    orgdfsdict(elem[0])
        else:
            orgdfsdict(elem[0])

# 深度处理原始字典树
def orgdfsdict(key):
    global f
    if key not in orgdict.keys():
        return
    if key not in finaldict.keys():
        finaldict[key] = {}
    for pa in orgdict[key]:
        if isinstance(key,str):
            pattern=[[key]]
        else:
            pattern = list(map(list, key))
        if pa[1] == 'i':
            pattern[-1].append(pa[0])
        else:
            pattern.append([pa[0]])
        key_tuple = tuple(map(tuple, pattern))
        if orgdict[key][pa]!=0:
            if orgdict[key][pa]>=orgminsup:
                support=orgdict[key][pa]
                lst = list(set(sum(pattern, [])))
                lst1 = inter(lst, dataTable.keys())
                if len(lst) == len(lst1):
                    support += singleposition(pattern, dataTable,dataTable1)
                if support >= minsupsum:
                    finaldict[key][pa]=support
                    if key_tuple not in finaldict.keys():
                        finaldict[key_tuple] = {}
                    orgdfsdict(key_tuple)
        else:
            if key_tuple not in finaldict.keys():
                finaldict[key_tuple] = {}
            orgdfsdict(key_tuple)

# 原始挖掘
def OFIPorgminer():
    global minsupsum,itemsetnumsum
    minsupsum = minsup
    onepattern()
    one_to_two()
    breadthfirst()
    orgdataTable.append(dataTable)
    orgdataTable1.append(copy.deepcopy(dataTable1))
    dataTable1.clear()
    itemsetnumsum = itemsetnum

# 增量挖掘
def OFIPdelminer():
    global num,cannum,itemsetnumsum,minsupsum,bufsupsum,orgdict,f,itemsetnum,minsup,orgminsup
    num += 1
    orgdict = copy.deepcopy(finaldict)
    finaldict.clear()
    oneitem.clear()
    cannum = 0
    f = 0
    orgminsup=minsupsum
    itemsetnumsum += itemsetnum
    minsupsum = itemsetnumsum * supthreshold
    for key in orgdict.keys():
        for pattern in orgdict[key]:
            orgdict[key][pattern]= orgdict[key][pattern] * k
    onepattern()
    one_to_two()
    breadthfirst()
    orgdicttree()
    orgdataTable.append(dataTable)
    orgdataTable1.append(copy.deepcopy(dataTable1))
    dataTable1.clear()

# 原始挖掘
def orgminer():
    global cannum
    org = '../SDBdata/E-Shop1k.txt'
    start = time.time()
    readfile(org)
    # OFIPorgminer()
    a=memory_usage(OFIPorgminer,max_usage=True)
    end=time.time()
    print('支持度：', minsup)
    n=0
    for key in finaldict.keys():
        tmp = []
        if key != ():
            if isinstance(key, tuple):
                key_tuple = list(map(list, key))
                tmp = key_tuple
            else:
                tmp = [[key]]
        for pattern in finaldict[key]:
            tmp1 = copy.deepcopy(tmp)
            if pattern[1] == 's':
                tmp1.append([pattern[0]])
            else:
                tmp1[-1].append(pattern[0])
            # print(tmp1, finaldict[key][pattern])
            n += 1
    print('原始频繁模式的数量：',n)
    print('候选模式的数量：',cannum)
    print('运行时间：', end - start, 's')
    print('内存使用：', a, 'Mb')
    print('----------------------------------------------')

# 增量挖掘
def delminer():
    start = time.time()
    readfile(file)
    # OFIPdelminer()
    a=memory_usage(OFIPdelminer,max_usage=True)
    end=time.time()
    print('整体支持度：', minsupsum)
    print('原始支持度：', orgminsup)
    n = 0
    for key in finaldict.keys():
        for pattern in finaldict[key]:
            # print(key,pattern, finaldict[key][pattern])
            n += 1
    print('增量频繁模式的数量：',n)
    print('候选模式的数量：', cannum)
    print('运行时间：', end - start, 's')
    print('内存使用：', a, 'Mb')

if __name__ == '__main__':
    orgminer()
    print('**********************************************************************************')
    listdel = ['../SDBdata/E-Shop4k.txt',
               '../SDBdata/E-Shop7k.txt',
               '../SDBdata/E-Shop10k.txt',
               '../SDBdata/E-Shop13k.txt',
               '../SDBdata/E-Shop16k.txt',
               '../SDBdata/E-Shop19k.txt',
               '../SDBdata/E-Shop22k.txt']
    for file in listdel:
        delminer()
        print('**********************************************************************************')