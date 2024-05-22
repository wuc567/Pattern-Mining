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
SList={}
IList={}
orgdataTable=[]
num=0
finaldict={}
orgdict={}
cannum=0
f=0
g=0
seqnum=0
orgseqnum=[]

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

# 计算单个模式在数据库中的出现位置
def singleposition(pattern,dataTable):
    a=0
    dataTable1=copy.deepcopy(dataTable)
    for s in dataTable1:
        # print(s)
        position = []
        # print(pattern)
        for ks in range(0, len(pattern)):
            position.append([])
        # print(position)
        i = 0
        j = len(pattern) - 1
        while i < len(s):
            if set(pattern[j]).issubset(set(s[i])):
                if j == 0:
                    # print(1, pattern[0])
                    # print(2, s[i])
                    for k in pattern[0]:
                        if k in s[i]:
                            s[i].remove(k)
                    # print(3, s[i])
                    position[j].append(i)
                    # print(4, position)
                    j = len(pattern) - 1
                    i += 1
                elif j > 0 and (j < len(pattern) - 1):
                    if len(position[j - 1]) == len(position[j]) + 1:
                        # print(5, pattern[j])
                        # print(6, s[i])
                        for k in pattern[j]:
                            if k in s[i]:
                                s[i].remove(k)
                        # print(7, s[i])
                        position[j].append(i)
                        # print(8, position)
                        j = len(pattern) - 1
                        i += 1
                    else:
                        j -= 1
                elif j == len(pattern) - 1:
                    if len(position[j - 1]) == len(position[j]) + 1:
                        # print(9, pattern[j])
                        # print(10, s[i])
                        for k in pattern[j]:
                            if k in s[i]:
                                s[i].remove(k)
                        position[j].append(i)
                        # print(11, position)
                        i = position[0][len(position[0]) - 1] + 1
                    else:
                        j -= 1
            else:
                if j == 0:
                    i += 1
                    j = len(pattern) - 1
                elif j > 0:
                    if len(position[j - 1]) == len(position[j]) + 1:
                        i += 1
                    else:
                        j -= 1
        if i == len(s):
            a += len(position[len(pattern) - 1])
            # print(12, a)
    return a

# 在整体的支持度
def sumsupport(key,item,pattern,t,support):
    tag=0
    if key in orgdict.keys():
        if (item,t) in orgdict[key].keys():
            tag=1
            support+=orgdict[key][(item,t)]
            if support >= minsupsum:
                orgdict[key][(item, t)] = 0
            else:
                orgdict[key].pop((item, t))
    if tag==0:
        for n in range(len(orgdataTable)):
            support += singleposition(pattern, orgdataTable[n]) * k ** (num - n)
    return support

# 生成一长度频繁模式
def onepattern():
    global cannum,f
    finaldict[()]={}
    temp={}
    for s in dataTable:
        for i in range(len(s)):
            for item in s[i]:
                if item not in temp:
                    temp[item]=1
                else:
                    temp[item]+=1
    for key in sorted(temp.keys()):
        cannum+=1
        if temp[key]>=minsup:
            t = temp[key]
            tag = 0
            support=temp[key]
            if () in orgdict.keys():
                if (key, 's') in orgdict[()]:
                    tag = 1
                    support += orgdict[()][(key, 's')]
                    # orgoneitem.pop(item)
                    if support >= minsupsum:
                        orgdict[()][(key, 's')] = 0
                    else:
                        orgdict[()].pop((key, 's'))
            if tag == 0:
                for i in range(len(orgdataTable)):
                    support += singleposition([[key]],orgdataTable[i]) * k ** (num - i)
            if support>=minsupsum:
                f += t / support
                finaldict[()][(key, 's')] = support
                candi.append([key])
    # print(finaldict)

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
                cannum+=1
                # print(tmp)
                support=singleposition(tmp,dataTable)
                # print(support)
                if support>=minsup:
                    t=support
                    support=sumsupport(tp[0],ad[0],tmp,'i',support)
                    if support >= minsupsum:
                        f+=t/support
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
            # print(tmp)
            support = singleposition(tmp,dataTable)
            if support>=minsup:
                t=support
                support = sumsupport(tp[0], ad[0], tmp, 's', support)
                if support >= minsupsum:
                    f+=t/support
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
    # print(cannum)

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
                    if len(longcandi[i].data[-1]) == 1: # S扩展
                        if tmp[0][0] not in SList.keys():
                            continue
                        elif longcandi[i].data[-1][0] not in SList[tmp[0][0]]:
                            continue
                        tmp.append(longcandi[i].data[-1])
                        cannum += 1
                        # print(tmp)
                        support=singleposition(tmp,dataTable)
                        if support>=minsup:
                            t=support
                            support=sumsupport(key_tuple,longcandi[i].data[-1][-1],tmp,'s',support)
                            if support >= minsupsum:
                                f+=t/support
                                p = CanPattern(tmp)
                                candi.append(p)
                                finaldict[key_tuple][(longcandi[i].data[-1][-1],'s')]=support
                    else:                       # I扩展
                        if len(tmp)==1:
                            if longcandi[i].data[-1][-1] not in IList[tmp[0][0]]:
                                continue
                        else:
                            if longcandi[i].data[-1][-1] not in SList[tmp[0][0]]:
                                continue
                        tmp[-1].append(longcandi[i].data[-1][-1])
                        cannum += 1
                        # print(tmp)
                        support = singleposition(tmp,dataTable)
                        if support>=minsup:
                            t=support
                            support = sumsupport(key_tuple, longcandi[i].data[-1][-1], tmp, 'i', support)
                            if support >= minsupsum:
                                f+=t/support
                                p = CanPattern(tmp)
                                candi.append(p)
                                finaldict[key_tuple][(longcandi[i].data[-1][-1],'i')]=support
            if finaldict[key_tuple]=={}:
                finaldict.pop(key_tuple)
        longcandi.clear()
        longcandi.extend(candi)
        candi.clear()
    # print(cannum)

# 读文件
def readfile(file):
    global minsup,dataTable,itemsetnum,bufsup,seqnum
    fileresult = dp.operateDataFile(file)
    dataTable = fileresult[0]
    itemsetnum = fileresult[1]
    minsup = itemsetnum * supthreshold

# 深度处理原始字典树
def orgdicttree():
    global f
    for elem in orgdict[()]:
        if orgdict[()][elem]!=0:
            if orgdict[()][elem]>=orgminsup:
                support=orgdict[()][elem]
                t=support
                support += singleposition([[elem[0]]],dataTable)
                if support>=minsupsum:
                    f+=(support-t)/support
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
                t=support
                support += singleposition(pattern, dataTable)
                if support >= minsupsum:
                    f+=(support-t)/support
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
    sorilink()
    # orgdataTable.append(dataTable)
    # itemsetnumsum = itemsetnum

# 增量挖掘
def OFIPdelminer():
    global num,cannum,itemsetnumsum,minsupsum,orgdict,f,itemsetnum,orgminsup
    num += 1
    orgdict = copy.deepcopy(finaldict)
    finaldict.clear()
    SList.clear()
    IList.clear()
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
    sorilink()
    orgdicttree()
    orgdataTable.append(dataTable)

# 原始挖掘
def orgminer():
    global cannum,supthreshold
    org = '../SDBdata/E-Shop1k.txt'
    start = time.time()
    readfile(org)
    # OFIPorgminer()
    a=memory_usage(OFIPorgminer,max_usage=True)
    end=time.time()
    print('支持度：', minsup)
    n=0
    for key in finaldict.keys():
        tmp=[]
        if key!=():
            if isinstance(key,tuple):
                key_tuple=list(map(list, key))
                tmp=key_tuple
            else:
                tmp=[[key]]
        for pattern in finaldict[key]:
            tmp1=copy.deepcopy(tmp)
            if pattern[1]=='s':
                tmp1.append([pattern[0]])
            else:
                tmp1[-1].append(pattern[0])
            # print(tmp1,finaldict[key][pattern])
            n += 1
    print('原始频繁模式的数量：',n)
    print('新增数据的占比：',f/n)
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
        tmp = []
        if key != ():
            if isinstance(key,tuple):
                key_tuple = list(map(list, key))
                tmp = key_tuple
            else:
                tmp=[[key]]
        for pattern in finaldict[key]:
            tmp1 = copy.deepcopy(tmp)
            if pattern[1] == 's':
                tmp1.append([pattern[0]])
            else:
                tmp1[-1].append(pattern[0])
            result = ''.join(['(' + ''.join(item) + ')' for item in tmp1])
            # print(result,finaldict[key][pattern])
            n += 1
    print('增量频繁模式的数量：',n)
    print('新增数据的占比：', f / n)
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