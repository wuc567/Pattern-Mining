import operator
import sys
sys.setrecursionlimit(1000000)
import time
import copy
from memory_profiler import memory_usage


'''序列结构'''
class Item():
    def __init__(self,dataitems):
        self.data=dataitems
        self.len=len(dataitems)
        self.flag=[]
        i=1
        for i in range(self.len):
            self.flag.append(0)
        self.use=0

'''候选模式结构'''
class Candilist():
    def __init__(self,dataitems):
        self.data=dataitems
        self.sup =0
        self.prefix=[]
        self.suffer=[]

'''候选模式列表（字典）'''
candione={}
'''候选模式集合（列表）'''
candi=[]
'''频繁模式集合'''
FPItem=[]
'''频繁模式过渡集合'''
FP=[]
'''最小支持度'''
minsup=450
'''序列'''
seqs=[]
'''弱字符集'''
weak=[]
'''弱字符阈值'''
weaknum=0
weakrate=0.1

'''读取数据'''
'''
将读取出来的数据转成字符串，存入结构体列表中
temp暂时存储字符串
把文件中读取出来的数据，存入节点结构体、序列、多序列
f用于标记去除-后的空格
'''
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
'''s[i],p.data[j]'''
def isinuse(s,p):
    i=0
    while i<len(p):
        idx=s.data.index(p[i])
        if s.flag[idx]==1:
            return True
        i+=1
    return False

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
    candiones={}
    i=0
    while i<len(seqs):
        j=0
        while j<len(seqs[i]):
            k=0
            while k<len(seqs[i][j].data):
                if seqs[i][j].data[k] not in candiones.keys():
                    candiones[seqs[i][j].data[k]] = 1
                    candi.append(Candilist([seqs[i][j].data[k]]))
                else:
                    candiones[seqs[i][j].data[k]] = candiones.get(seqs[i][j].data[k]) + 1
                k+=1
            j+=1
        i+=1
    '''将频繁模式顺序排放，放入候选集合和频繁集合'''
    print(len(candiones))
    candione=dict(sorted(candiones.items(),key=lambda x:x[1]))
    weaknum=len(candiones)*weakrate
    for key in sorted(candione.keys()):
        if len(weak)<=weaknum:
            weak.append(key)
        if candione.get(key) >= minsup and key not in weak :
            temp = Candilist(key.split(","))
            temp.sup = candione.get(key)
            FPItem.append(temp)
        else:
            candione.pop(key)
    '''数字型字符串使用
    sort_item = sortitem(candione.keys())'''
    '''字符型数据使用'''
    sort_item=list(candione.keys())
    sort_item.sort()
    i = 0
    while i < len(sort_item):
        temp = Candilist([str(sort_item[i])])
        temp.sup = candione.get(str(sort_item[i]))
        FP.append(temp)
        i += 1

'''sort_item排序'''
def sortitem(items):
    sort_item=[]
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

'''判断是否两个结点之间存在强字符,beg,end是这两个字符在s中的序号'''
def isweak(weak,s,beg,end):
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

'''判断模式每一个项集是否在序列项集中，即（bc）是否在（abc）中,s是item，p是列表;
如果p=(bc)(c),s中有（bc）,其中的c被先用了，则再次使用的时候这个s中的bc就不满足一次性条件了'''
def isinitem(s,p):
    i = 0
    while i < len(p):
        if p[i] not in s.data:
            return False
        i += 1
    if i >= len(p):
        return True


'''创建m层队列'''
def createqueue(p):
    plen=len(p)
    i=0
    queue=[]
    while i<plen:
        q=[]
        queue.append(q)
        i+=1
    return queue

'''输入为项集，如果项集中每一个元素都被使用，则返回true'''
def isuseall(item):
    i=0
    while i<item.len:
        if item.flag[i]==0:
            return False
        i+=1
    return True

'''将使用的序列中元素标记flag'''
def labflag(s,p):
    i=0
    j=0
    while i<len(p) and j<len(s.data):
        if p[i]==s.data[j]:
            s.flag[j]=1
            i += 1
            j += 1
        else:
            j+=1
    if isuseall(s):
        s.use=1

'''创建结点前，是否删除队列中多余结点'''
def isdel(queue,k):
    if len(queue[k - 1]) - len(queue[k]) > 1:
        end = len(queue[k - 1]) - len(queue[k])
        i = k - 1
        while i >= 0:
            start = 1
            while start < end:
                del queue[i][0]
                start += 1
            i -= 1

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



'''one scan算法'''
def one_scan(s,p,weak):
    lastpos = 0
    pos=[]
    first=0
    while 1:
        sup=p.sup
        i=0
        j=0
        while i<len(s):
            if s[i].use==0:
                if isinitem(s[i],p.data[j]) and not isinuse(s[i],p.data[j]):
                    if j==0:
                        first = i
                    if j!=0 and not isweak(weak,s,lastpos,i):
                        i=first+1
                        j = 0
                        pos.clear()
                        continue
                    lastpos = i
                    pos.append(i)
                    j += 1
                if j>=len(p.data) :
                    k=0
                    while k<len(p.data):
                        labflag(s[pos[k]], p.data[k])
                        k+=1
                    pos.clear()
                    j=0
                    i=first
                    p.sup+=1
            i+=1
        if sup==p.sup:
            break

def mainfun():
    conseqs()
    candinum = []  # 候选模式不同长度起始位置
    starttime = time.time()
    onepattern(seqs)
    candinum.append(len(candi))
    one_to_two()  # 从FP中生成存到candi
    candinum.append(len(candi))
    FP.clear()
    while 1:
        cannum = candinum.pop(0)
        i = cannum
        while i < len(candi):
            p = candi[i]
            j = 0
            while j < len(seqs):
                one_scan(seqs[j], p, weak)
                j += 1
            useto0(seqs)
            if candi[i].sup >= minsup:
                FP.append(candi[i])
                FPItem.append(candi[i])
            i += 1
        sorilink()
        FP.clear()
        if cannum == len(candi):
            break
        else:
            candinum.append(len(candi))
    endtime = time.time()
    print("endtime:" + str(endtime - starttime))
    print("频繁模式结果集：" + str(len(FPItem)))
    print("候选模式集：" + str(len(candi)))
    '''j = 0
    while j < len(FPItem):
        print(str(j) + " " + str(FPItem[j].data) + ":" + str(FPItem[j].sup))
        j += 1'''

if __name__ == '__main__':
    maxusage = memory_usage((mainfun),max_usage=True)
    print(str(maxusage) + "Mb")
