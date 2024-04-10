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
minsup=400
'''各序列的Next数组集合'''
Nextlist=[]
'''存放Next数组结构,用于支持度计算(字典)每条序列的'''
Next={}
'''序列'''
seqs=[]
'''弱字符集'''
weak=[]
'''弱字符阈值'''
weaknum=0
weakrate=0.1
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
                if seqs[i][j].data[k] not in Next.keys():#每条序列创建一个Next数组
                    Next[seqs[i][j].data[k]] = [j]
                else:
                     Next[seqs[i][j].data[k]].append(j)
                k+=1
            j+=1
        Nextlist.append(copy.deepcopy(Next))
        Next.clear()
        i+=1
    '''将频繁模式顺序排放，放入候选集合和频繁集合'''
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
            i=0
            while i<len(Nextlist):
                if key in Nextlist[i].keys():
                    del Nextlist[i][key]
                i+=1
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
def isweak(s,beg,end):
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

'''计算支持度算法'''
def newsup(s,n,p):
    flag = 0
    out = 0
    que = []  # 存放Next数组
    count = 0  # 记存储Next顺序
    MaxIndex = -1
    useflag = {}  # 使用过的位置存放进来，保证多项集的一次性条件
    usearray=[]
    i=0
    while i<len(p.data):#创建抽出的Next数组
        j=0
        while j<len(p.data[i]):
            if p.data[i][j] in Nextlist[n].keys():
                temp = copy.deepcopy(Nextlist[n].get(p.data[i][j]))
                temp.insert(0, 1)  # 插入0为指针位置
                que.append(temp)
            else:
                return
            j+=1
        i+=1
    while flag==0:
        i=0
        max = MaxIndex
        while i<len(p.data):
            while que[count][0]<len(que[count]) and que[count][que[count][0]] <= max:# 第一个位置就要大于上一个元素的索引
                que[count][0] += 1
            if p.data[i][0] in useflag.keys():
                temp = useflag.get(p.data[i][0])
                while que[count][0] < len(que[count]) and temp.count(que[count][que[count][0]]):
                    que[count][0] += 1
            if que[count][0] >= len(que[count]):
                flag = 1
                break
            if len(p.data[i])==1 and flag==0:#若为单项集
                if i!=0:
                    if not isweak(s,max,que[count][que[count][0]]):
                        que[count-1][0]+=1
                        if que[count-1][0] >= len(que[count-1]):
                            flag = 1
                        #MaxIndex+=1
                        i=0#p从头开始重新匹配
                        usearray.clear()
                        break
                max = que[count][que[count][0]]
                usearray.append(max)
                if i==len(p.data)-1:
                    a = 0
                    k = 0
                    while a < len(p.data):
                        b = 0
                        while b < len(p.data[a]):
                            if p.data[a][b] not in useflag.keys():
                                useflag[p.data[a][b]] = [usearray[k]]  # 标记该项为使用过
                            else:
                                useflag[p.data[a][b]].append(usearray[k])
                            k += 1
                            b += 1
                        a += 1
                    p.sup+=1
                    usearray.clear()
                if i==0:
                    MaxIndex=max
                count+=1
            else:
                j = 1#最后一项不为单项集时，走这个，单项集时不走
                while j<len(p.data[i]) and flag==0:#指针移动=?
                    if not que[count+j][1:].count(que[count][que[count][0]]):#不存在这个位置索引,第一元素指针后移，从头再来
                        j=1
                        que[count][0]+=1
                        if que[count][0] >= len(que[count]):
                            flag = 1
                            out=1
                            break
                        continue
                    elif p.data[i][j] in useflag.keys() and useflag.get(p.data[i][j]).count(que[count][que[count][0]])!=0:
                        j = 1
                        que[count][0] += 1
                        if que[count][0] >= len(que[count]):
                            flag = 1
                            out=1
                            break
                        continue
                    else:
                        if i != 0:
                            if not isweak(s, max, que[count][que[count][0]]):
                                que[count - 1][0] += 1
                                if que[count - 1][0] >= len(que[count - 1]):
                                    flag = 1
                                #MaxIndex += 1
                                i = 0  # p从头开始重新匹配
                                out=1
                                usearray.clear()
                                break
                        que[count+j][0]=que[count+j][1:].index(que[count][que[count][0]])
                        que[count+j][0]+=1
                    j+=1
                if que[count][0] < len(que[count]):
                    max = que[count][que[count][0]]
                k = 0
                while k < len(p.data[i]) and j == len(p.data[i]):
                    usearray.append(max)
                    k += 1
                if i == len(p.data) - 1 and j == len(p.data[i]):
                    a = 0
                    k = 0
                    while a < len(p.data):
                        b = 0
                        while b < len(p.data[a]):
                            if p.data[a][b] not in useflag.keys():
                                useflag[p.data[a][b]] = [usearray[k]]  # 标记该项为使用过
                            else:
                                useflag[p.data[a][b]].append(usearray[k])
                            k += 1
                            b += 1
                        a += 1
                    p.sup += 1
                    usearray.clear()
                if out==1:
                    usearray.clear()
                    out=0
                    break
                if i == 0:
                    MaxIndex = max
                count+=len(p.data[i])
            i+=1
        count=0


'''读取数据'''

def mainfun():
    conseqs()
    candinum=[]#候选模式不同长度起始位置
    starttime=time.time()
    onepattern(seqs)
    candinum.append(len(candi))
    one_to_two()#从FP中生成存到candi
    candinum.append(len(candi))
    FP.clear()
    while 1:
        cannum = candinum.pop(0)
        i = cannum
        while i < len(candi):
            j = 0
            while j < len(seqs):
                p = candi[i].data
                newsup(seqs[j], j, candi[i])
                j += 1
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
    print("endtime:"+str(endtime-starttime))
    print("频繁模式结果集："+str(len(FPItem)))
    print("候选模式集："+str(len(candi)))
    '''i = 0
    while i < len(FPItem):
        print(str(FPItem[i].data) + ":" + str(FPItem[i].sup))
        i += 1
        '''


if __name__ == '__main__':
    maxusage = memory_usage((mainfun),max_usage=True)
    print(str(maxusage) + "Mb")

