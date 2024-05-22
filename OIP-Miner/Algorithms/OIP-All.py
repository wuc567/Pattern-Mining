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
SList={}
IList={}
orgdataTable=[]
orgdataTable1=[]
num=0
finaldict={}
orgdict={}
fl=[]
ms=[]
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
                    # orgoneitem.pop(item)
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
                        p = CanPattern(tmp)
                        longcandi.append(p)
                        finaldict[tp[0]][(ad[0],'i')]=support
                        if tmp[0][0] not in IList.keys():
                            IList[tmp[0][0]]=[tmp[0][1]]
                        else:
                            IList[tmp[0][0]].append(tmp[0][1])
            tmp = []
            tmp.append(tp)
            tmp.append(ad)
            cannum += 1
            support = singleposition(tmp,dataTable,dataTable1)
            if support>=minsup:
                support = sumsupport(tp[0], ad[0], tmp, 's', support)
                if support >= minsupsum:
                    p = CanPattern(tmp)
                    longcandi.append(p)
                    finaldict[tp[0]][(ad[0],'s')]=support
                    if tmp[0][0] not in SList.keys():
                        SList[tmp[0][0]] = [tmp[1][0]]
                    else:
                        SList[tmp[0][0]].append(tmp[1][0])
            j += 1
        i += 1
        if finaldict[tp[0]]=={}:
            finaldict.pop(tp[0])
    candi.clear()

# 获取候选模式前后缀（深拷贝）
def preandsuf(p):
    if len(p.data)!=1:
        tp = copy.deepcopy(p.data)
        p.prefix=copy.deepcopy(p.data[0:-1])
        p.suffer=copy.deepcopy(p.data[1:])
        tp[0].pop(0)
        if len(tp[0])!=0:
            p.suffer.insert(0,tp[0])
        tp[-1].pop(-1)
        if len(tp[-1]) != 0:
            p.prefix.append(tp[-1])
    else:
        p.prefix.append(copy.deepcopy(p.data[0][0:-1]))
        p.suffer.append(copy.deepcopy(p.data[0][1:]))

# S/I连接生成候选模式,长度大于2
def sorilink():
    global cannum,f
    while len(longcandi) != 0:
        i = 0  # 开始位置需要设置
        while i<len(longcandi):
            preandsuf(longcandi[i])
            i+=1
        for j in range(len(longcandi)):
            key_tuple=tuple(map(tuple, longcandi[j].data))
            finaldict[key_tuple]={}
            for i in range(len(longcandi)):
                if operator.eq(longcandi[i].prefix,longcandi[j].suffer):
                    tmp = copy.deepcopy(longcandi[j].data)
                    key_tuple2=tuple(map(tuple, longcandi[i].data))
                    if len(longcandi[i].data[-1]) == 1: # S扩展
                        if tmp[0][0] not in SList.keys():
                            continue
                        elif longcandi[i].data[-1][0] not in SList[tmp[0][0]]:
                            continue
                        tmp.append(longcandi[i].data[-1])
                        cannum += 1
                        support=singleposition(tmp,dataTable,dataTable1)
                        if support>=minsup:
                            support=sumsupport(key_tuple,longcandi[i].data[-1][-1],tmp,'s',support)
                            if support >= minsupsum:
                                p = CanPattern(tmp)
                                candi.append(p)
                                finaldict[key_tuple][(longcandi[i].data[-1][-1],'s')]=support
                    else:                       # I扩展
                        if len(tmp)==1:
                            flag=True
                            if longcandi[i].data[-1][-1] not in IList[tmp[0][0]]:
                                continue
                        else:
                            flag=False
                            if longcandi[i].data[-1][-1] not in SList[tmp[0][0]]:
                                continue
                        tmp[-1].append(longcandi[i].data[-1][-1])
                        key_tuple1 = tuple(map(tuple, tmp))
                        cannum += 1
                        if flag==True:
                            support = 0
                            seq=inter(dataTable1[key_tuple[0]].keys(),dataTable1[key_tuple2[0]].keys())
                            for s in seq:
                                support+=len(inter(dataTable1[key_tuple[0]][s],dataTable1[key_tuple2[0]][s]))
                            if support>=minsup:
                                support = sumsupport(key_tuple, longcandi[i].data[-1][-1], tmp, 'i', support)
                                if support >= minsupsum:
                                    for s in seq:
                                        if key_tuple1[0] not in dataTable1.keys():
                                            dataTable1[key_tuple1[0]] = {}
                                            dataTable1[key_tuple1[0]][s] = inter(dataTable1[key_tuple[0]][s],dataTable1[key_tuple2[0]][s])
                                        else:
                                            dataTable1[key_tuple1[0]][s] = inter(dataTable1[key_tuple[0]][s],dataTable1[key_tuple2[0]][s])
                                    p = CanPattern(tmp)
                                    candi.append(p)
                                    finaldict[key_tuple][(longcandi[i].data[-1][-1], 'i')] = support
                        else:
                            support=singleposition(tmp,dataTable,dataTable1)
                            if support>=minsup:
                                support = sumsupport(key_tuple, longcandi[i].data[-1][-1], tmp, 'i', support)
                                if support >= minsupsum:
                                    p = CanPattern(tmp)
                                    candi.append(p)
                                    finaldict[key_tuple][(longcandi[i].data[-1][-1],'i')]=support
            if finaldict[key_tuple]=={}:
                finaldict.pop(key_tuple)
        longcandi.clear()
        longcandi.extend(candi)
        candi.clear()

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
    # print(minsup)

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

# 增量挖掘
def OFIPdelminer():
    global num,cannum,itemsetnumsum,minsupsum,bufsupsum,orgdict,f,itemsetnum,minsup,orgminsup
    cannum=0
    finaldict.clear()
    itemsetnumsum += itemsetnum
    minsupsum = itemsetnumsum * supthreshold
    for key in orgdict.keys():
        for pattern in orgdict[key]:
            orgdict[key][pattern]= orgdict[key][pattern] * k
    onepattern()
    one_to_two()
    sorilink()
    if num>=1:
        orgdicttree()
    orgdataTable.append(dataTable)
    orgdataTable1.append(copy.deepcopy(dataTable1))
    dataTable1.clear()
    num += 1
    SList.clear()
    IList.clear()
    orgdict = copy.deepcopy(finaldict)

# 增量挖掘
def delminer():
    global itemsetnumsum,num
    a=0
    start = time.time()
    for fi in fl:
        readfile(fi)
        # OFIPdelminer()
        a=memory_usage(OFIPdelminer,max_usage=True)
    end=time.time()
    print('整体支持度：', minsupsum)
    # print('原始支持度：', orgminsup)
    n = 0
    for key in finaldict.keys():
        for pattern in finaldict[key]:
            # print(key,pattern, finaldict[key][pattern])
            n += 1
    print('增量频繁模式的数量：',n)
    print('候选模式的数量：', cannum)
    print('运行时间：', end - start, 's')
    print('内存使用：', a, 'Mb')
    itemsetnumsum=0
    orgdataTable.clear()
    orgdataTable1.clear()
    orgdict.clear()
    num=0

if __name__ == '__main__':
    listdel = ['../SDBdata/E-Shop1k.txt',
               '../SDBdata/E-Shop4k.txt',
               '../SDBdata/E-Shop7k.txt',
               '../SDBdata/E-Shop10k.txt',
               '../SDBdata/E-Shop13k.txt',
               '../SDBdata/E-Shop16k.txt',
               '../SDBdata/E-Shop19k.txt',
               '../SDBdata/E-Shop22k.txt']
    for file in listdel:
        fl.append(file)
        delminer()
        print('**********************************************************************************')