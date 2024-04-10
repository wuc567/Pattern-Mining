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
minsup=450
'''各序列的Next数组集合'''
Nextlist=[]
'''存放Next数组结构,用于支持度计算(字典)每条序列的'''
Next={}
'''序列'''
seqs=[]
'''弱字符集'''
weak=[]
'''二项集列表集合'''
twolist=[]
'''二项集集合'''
twoitems=[]
'''弱字符阈值'''
weaknum=0
weakrate=0.1
sort_item=[]

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
    items=[]
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
    print(len(candiones))
    candione=dict(sorted(candiones.items(),key=lambda x:x[1]))
    weaknum=len(candiones)*weakrate
    for key in sorted(candione.keys()):
        if len(weak)<=weaknum:
            weak.append(key)
        if candione.get(key) >= minsup and key not in weak :
            temp = Candilist(key.split(","))
            temp.sup = candione.get(key)
            items.append(key)
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
    return sort_item

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
                twoitems.append(Candilist(tmp))
                tmp=[]
            tmp.append(tp)
            tmp.append(ad)
            candi.append(Candilist(tmp))
            twoitems.append(Candilist(tmp))
            j+=1
        i+=1

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

'''读取数据'''
'''
将读取出来的数据转成字符串，存入结构体列表中
temp暂时存储字符串
把文件中读取出来的数据，存入节点结构体、序列、多序列
f用于标记去除-后的空格
'''


'''创建二项集列表'''
def twoindexlist(seqs,twoitems):
    #每条序列二项集列表集合
    out = 0
    n=0
    while n<len(seqs):
        oneseqtwoitem = {}#每条序列的二项集列表
        m=0
        while m<len(twoitems):
            p=twoitems[m]
            idx=[]
            que=[]
            i = 0
            while i < len(p.data):  # 创建抽出的Next数组
                j = 0
                while j < len(p.data[i]):
                    if p.data[i][j] in Nextlist[n].keys():
                        temp = copy.deepcopy(Nextlist[n].get(p.data[i][j]))
                        que.append(temp)
                    else:
                        que = []
                        out=1
                        break
                    j += 1
                i += 1
            if out==1:
                out=0
                m+=1
                continue
            f = 0
            s = 0
            if len(p.data)!=1:
                while 1:
                    while f<len(que[0]) and s<len(que[1]) and que[0][f]>=que[1][s]:
                        s+=1
                    if f<len(que[0]) and s<len(que[1]):
                        if isweak(seqs[n],que[0][f],que[1][s]):
                            idx.append([que[0][f],que[1][s]])
                            f+=1
                            s+=1
                        else:
                            f+=1
                    else:
                        break
            else:#p.data==1（bc）
                while f<len(que[0]) and s<len(que[1]):
                    if que[0][f]==que[1][s]:
                        idx.append([que[0][f]])
                        f += 1
                        s += 1
                    elif que[0][f]>que[1][s]:
                        s+=1
                    else:
                        f+=1
            if len(idx)!=0:#如果当前序列不存在二项集的出现，则没有，使用时候判断是否在二项集列表中存在
                oneseqtwoitem[str(p.data)]=idx
            m+=1
        twolist.append(copy.deepcopy(oneseqtwoitem))
        n+=1



'''计算候选模式支持度,拆分模式为两两一组'''
def splitpattern(p):
    pre=[]#拆分结果的二项集集合
    i=0
    f = p.data[0][0]
    k=0
    s = ''
    temp = []
    while i<len(p.data):
        j=0
        while j<len(p.data[i]) and i<len(p.data):
            if j+1<len(p.data[i]):
                s=p.data[i][j+1]
                temp.append(f)
                temp.append(s)
                pre.append([temp])
            else:
                if i+1>=len(p.data):
                    break
                s=p.data[i+1][0]
                temp.append([f])
                temp.append([s])
                pre.append(temp)
            f = s
            k += 1
            if k==1:
                k=0
                s = ''
                temp = []
            j+=1
        i+=1
    return pre#返回这个拆分结果

def searchfirst(pre,que,n,num,useflag):
    i=0
    while i<len(que):
        if que[i][0]==num:
            if len(pre[n])==1:
                if pre[n][0][-1] not in useflag.keys():
                    return que[i][-1]
                elif que[i][-1] not in useflag.get(pre[n][0][-1]):
                    return que[i][-1]
            else:
                if pre[n][-1][0] not in useflag.keys():
                    return que[i][-1]
                elif que[i][-1] not in useflag.get(pre[n][-1][0]):
                    return que[i][-1]
            break
        i+=1
    return None

'''使用第n条序列的二项集列表给pre的找支持度 单独一条序列'''
def splitlist(twolist,n,pre,p):
    que=[]
    usesup=[]
    useflag={}
    i=0
    while i<len(pre):
        if str(pre[i]) in twolist[n].keys():
            que.append(twolist[n].get(str(pre[i])))
        else:
            return 0#若这条序列中有一个不存在，那么就有一组无出现，支持度必为0
        i+=1
    '''计算支持度'''
    i=0
    while i<len(que[0]):
        if pre[0][0][0] in useflag.keys() and que[0][i][0] in useflag.get(pre[0][0][0]):
            i+=1
            continue
        usesup.append(que[0][i][0])
        num=searchfirst(pre,que[0],0,que[0][i][0],useflag)
        usesup.append(num)
        j=1
        while j<len(que):
            num=searchfirst(pre,que[j],j,num,useflag)
            if num==None:
                usesup.clear()#清空
                break
            else:
                usesup.append(num)
            j+=1
        if j == len(que):
            p.sup+=1
            m=len(p.data)-1
            while m>=0:
                n=len(p.data[m])-1
                while n>=0:
                    if p.data[m][n] not in useflag.keys():
                        useflag[p.data[m][n]]=[usesup.pop()]
                    else:
                        useflag[p.data[m][n]].append(usesup.pop())
                    n-=1
                m-=1
            usesup.clear()
        i+=1

'''频繁二项集归为FP中和FPItem中'''
def fretwo(seqs,twoitems,twolist):
    i=0
    while i<len(twoitems):
        if len(twoitems[i].data)==1:
            f=twoitems[i].data[0][0]
            s=twoitems[i].data[0][1]
        else:
            f=twoitems[i].data[0][0]
            s = twoitems[i].data[1][0]
        if f==s:
            flag=1
        else:
            flag=0
        j=0
        while j<len(seqs):
            useflag=[]
            if str(twoitems[i].data) in twolist[j].keys():
                if flag==0:
                    twoitems[i].sup+=len(twolist[j].get(str(twoitems[i].data)))
                else:
                    temp=twolist[j].get(str(twoitems[i].data))
                    m=0
                    while m<len(temp):
                        n=0
                        while n<len(temp[m]):
                            if temp[m][n] not in useflag:
                                useflag.append(temp[m][n])
                            else:
                                break
                            n+=1
                        if n==2:
                            twoitems[i].sup+=1
                        m+=1
            j+=1
        i+=1
    i=0
    #判断是否频繁
    while i<len(twoitems):
        if twoitems[i].sup>=minsup:
            FP.append(twoitems[i])
            FPItem.append(twoitems[i])
        i+=1

def sandilinked(sort_item):
    i=0
    while i<len(FP):
        j=0
        while j<len(sort_item):
            if len(FP[i].data)==1 and type(FP[i].data[0])==str:
                temp=[copy.deepcopy(FP[i].data)]#s-连接
            else:
                temp = copy.deepcopy(FP[i].data)
            temp.append([sort_item[j]])
            candi.append(Candilist(temp))
            if type(FP[i].data[-1])==str:
                lastidx = sort_item.index(FP[i].data[-1])
            else:
                lastidx=sort_item.index(FP[i].data[-1][-1])
            if j>lastidx:
                temp=copy.deepcopy(FP[i].data)#I-连接
                if type(temp[-1])==str:
                    temp.append(sort_item[j])
                    candi.append(Candilist([temp]))
                else:
                    temp[-1].append(sort_item[j])
                    candi.append(Candilist(temp))
            j+=1
        i+=1

def mainfun():
    conseqs()
    candinum=[]#候选模式不同长度起始位置
    starttime=time.time()
    sort_item=onepattern(seqs)#0->1
    sort_item=list(map(str,sort_item))
    candinum.append(len(candi))
    sandilinked(sort_item)#1->2
    i=candinum.pop(0)
    while i<len(candi):
        twoitems.append(candi[i])
        i+=1
    twoindexlist(seqs,twoitems)
    candinum.append(len(candi))
    FP.clear()
    fretwo(seqs,twoitems,twolist)
    sandilinked(sort_item)#2->3
    candinum.append(len(candi))
    FP.clear()
    while 1 :
        cannum = candinum.pop(0)
        i = cannum
        while i < len(candi):
            p = candi[i]
            pre = splitpattern(p)
            j = 0
            while j < len(seqs):
                splitlist(twolist,j,pre,p)
                j += 1
            if candi[i].sup >= minsup:
                FP.append(candi[i])
                FPItem.append(candi[i])
            i += 1
        sandilinked(sort_item)
        FP.clear()
        if cannum == len(candi):
            break
        else:
            candinum.append(len(candi))
    endtime = time.time()
    print("endtime:"+str(endtime-starttime))
    print("频繁模式结果集："+str(len(FPItem)))
    ''' 
    i=0
    while i<len(FPItem):
        print(str(FPItem[i].data)+":"+str(FPItem[i].sup))
        i+=1'''
    print("候选模式集："+str(len(candi)))
if __name__ == '__main__':
    maxusage = memory_usage((mainfun),max_usage=True)
    print(str(maxusage) + "Mb")


