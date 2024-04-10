import operator
import sys
sys.setrecursionlimit(1000000)
import time
import copy
from memory_profiler import memory_usage

'''
多项集结构体
dataitems直接为一个列表，存储一个多项集
标记每个项集中的元素为未使用 o未使用，1为使用
use标记当前项集是否使用完毕，全部使用完时或者扫描到最后一个元素都不可用时标记为1，未使用完标记0
'''
class Item():
    def __init__(self,dataitems):
        self.data=dataitems
        self.len=len(dataitems)
        self.flag=[]
        i=1
        for i in range(self.len):
            self.flag.append(0)
        self.use=0

class Candilist():
    def __init__(self,dataitems):
        self.data=dataitems
        self.sup =0
        self.prefix=[]
        self.suffer=[]


seqs=[]
'''频繁项集集合'''
FP=[]
'''候选模式集合'''
candi=[]
'''设置最小支持度'''
minsup=550
'''候选模式列表（字典）'''
candione={}
'''频繁模式集合'''
FPItem=[]
'''弱字符集'''
weak=[]
'''弱字符阈值'''
weaknum=0
weakrate=0.1

def conseqs():
    with open("SDB1.txt", "r") as f:  # 打开文件
        data = f.read()  # 读取文件
        f=0
        temp=''
        tempitem = []
        seq = []
        for c in data:
            if f==1 :
                f=0
            elif c ==' ':
                tempitem.append(temp)
                temp=''
            elif c=='-':
                f=1
                item = Item(tempitem)
                seq.append(item)
                tempitem=[]
            else:
                temp+=c
            if c=='\n':
                seqs.append(seq)
                seq=[]

'''获取候选模式前后缀（深拷贝）'''
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

'''遍历序列，生成一长度候选模式,并且将频繁模式放入候选集合和频繁集合
   给每条序列创建一个Next数组，且只保存频繁项集的Next数组
'''
def onepattern(seqs):
        candiones = {}
        i = 0
        while i < len(seqs):
            j = 0
            while j < len(seqs[i]):
                k = 0
                while k < len(seqs[i][j].data):
                    if seqs[i][j].data[k] not in candiones.keys():
                        candiones[seqs[i][j].data[k]] = 1
                        candi.append(Candilist([seqs[i][j].data[k]]))
                    else:
                        candiones[seqs[i][j].data[k]] = candiones.get(seqs[i][j].data[k]) + 1
                    k += 1
                j += 1
            i += 1
        '''将频繁模式顺序排放，放入候选集合和频繁集合'''
        candione = dict(sorted(candiones.items(), key=lambda x: x[1]))
        weaknum = len(candiones) * weakrate
        for key in sorted(candione.keys()):
            if len(weak) <= weaknum:
                weak.append(key)
            if candione.get(key) >= minsup and key not in weak:
                temp = Candilist(key.split(","))
                temp.sup = candione.get(key)
                FPItem.append(temp)
            else:
                candione.pop(key)
        '''数字型字符串使用
        sort_item = sortitem(candione.keys())'''
        '''字符型数据使用'''
        sort_item = list(candione.keys())
        sort_item.sort()
        i = 0
        while i < len(sort_item):
            temp = Candilist([str(sort_item[i])])
            temp.sup = candione.get(str(sort_item[i]))
            FP.append(temp)
            i += 1

'''sort_item排序'''
def sortitem(items):
    sort_item = []
    for x in items:
        sort_item.append(int(x))
    sort_item.sort()
    return sort_item

'''一项集变成二项集'''
def one_to_two():
    i=0
    while i<len(FP):
        tp=copy.deepcopy(FP[i].data)
        j=0
        while j<len(FP):
            ad=copy.deepcopy(FP[j].data)
            tmp=[]
            if i<j:
                tmp.append(tp+ad)
                candi.append(Candilist(tmp))
                tmp=[]
            tmp.append(tp)
            tmp.append(ad)
            candi.append(Candilist(tmp))
            j+=1
        i+=1

'''S/I连接生成候选模式,需要先求一下FP中模式的前后缀'''
def sorilink():
    i=0#开始位置需要设置
    while i<len(FP):
        preandsuf(FP[i])
        i+=1
    for i in range(len(FP)):
        for j in range(len(FP)):
            if operator.eq(FP[i].prefix,FP[j].suffer):
                tmp = copy.deepcopy(FP[j].data)
                if len(FP[i].data[-1]) == 1: # S扩展
                    tmp.append(FP[i].data[-1])
                else:                       # I扩展
                    tmp[-1].append(FP[i].data[-1][-1])
                candi.append(Candilist(tmp))
    FP.clear()#每次生成完候选模式清空频繁项集

'''候选模式为频繁的放入频繁项集'''
def candiinFP(begin,end):
    i=begin
    while i<end:
        if candi[i].sup>=minsup:
            preandsuf(candi[i])
            FP.append(candi[i])
        i+=1

'''是否是弱间隙'''
def isweak(weak,s,beg,end):
    if beg==end:
        i=beg
    else:
        i=beg+1
    while i<end:
        j=0
        while j<len(s[i].data):
            if s[i].data[j] not in weak:
                return False
            j+=1
        i+=1
    if i==end:
        return True

def isinitem(s,p):
    i = 0
    j = 0
    while i < len(s.data) and j<len(p):
        if operator.eq(s.data[i], p[j]):
            j += 1
            if s.flag[i]!=0:
                return False
        i += 1
    if j >= len(p):
        return True
    else:
        return False

'''将序列标记归零use和flag'''
def useto0(seqs):
    i=0
    while i<len(seqs):
        j=0
        while j<len(seqs[i]):
            seqs[i][j].use=0
            k=0
            while k<seqs[i][j].len:
                seqs[i][j].flag[k]=0
                k+=1
            j+=1
        i+=1

'''computesupport算法'''
def computesupport(s,ssta,p,psta,weak,uppos):
        if not isinitem(s[ssta],p.data[psta]):
            return 0
        if psta>=len(p.data)-1:
            p.sup+=1
            return 1
        j=ssta+1
        while j<len(s):
            if j+len(p.data)-1-psta>len(s):
                break
            if isweak(weak,s,uppos,j):
                computesupport(s,j,p,psta+1,weak,j)
                uppos=ssta
            else:
                break
            j+=1
        return 0


def PWM(s,p,weak):
    i=0
    while i<len(s):
        if isinitem(s[i],p.data[0]):
            computesupport(s,i,p,0,weak,i)
        i+=1

'''读取文件中的数据，并构建数据结构'''
def mainfun():
    conseqs()
    candinum=[]#候选模式不同长度起始位置
    starttime=time.time()
    onepattern(seqs)
    candinum.append(len(candi))
    '''模式拼接并且计算候选模式的支持度，每个序列计算完，清空队列,放入频繁项集'''
    one_to_two()#从FP中生成存到candi
    candinum.append(len(candi))
    FP.clear()
    while 1:
        cannum = candinum.pop(0)
        i = cannum
        while i<len(candi):
            p=candi[i]
            j=0
            while j<len(seqs):
                PWM(seqs[j],p,weak)
                j+=1
            useto0(seqs)
            if p.sup >= minsup:
                FP.append(p)
                FPItem.append(p)
            i+=1
        sorilink()
        FP.clear()
        if cannum == len(candi):
            break
        else:
            candinum.append(len(candi))
    endtime=time.time()
    '''i = 0
    while i < len(FPItem):
        print(str(FPItem[i].data) + ":" + str(FPItem[i].sup))
        i += 1'''
    print("endtime:"+str(endtime-starttime))
    print("频繁模式结果集："+str(len(FPItem)))
    print("候选模式集："+str(len(candi)))

if __name__ == '__main__':
    maxusage = memory_usage((mainfun),max_usage=True)
    print(str(maxusage) + "Mb")

