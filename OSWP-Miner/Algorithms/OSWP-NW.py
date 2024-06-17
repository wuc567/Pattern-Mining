import operator
import sys
import time

sys.setrecursionlimit(1000000)
import copy
import operator
'''支持度数组结构 SupQueue类成员有窗口大小win，队尾指针tail， 数组arr 元素和sum '''
class SupQueue(object):
    def __init__(self, n=10):
        self.tail = 0
        self.win=n
        self.sum=0
        self.last_seq=-1

    def enqueue(self, e): # 入队
        self.sum += e
        self.tail += 1


'''
序列结构
Item类
'''
class Item():
    def __init__(self,dataitems):
        self.data=dataitems

class Tries():
    def __init__(self,supArr):
        self.supArr=supArr
        self.pattern=[]
        self.sup=self.supArr.sum
        self.last_seq=supArr.last_seq
        self.prefix=[]
        self.suffer=[]
        self.len=1
    def enqueue(self, e):
        self.supArr.enqueue(e)
        self.sup=self.supArr.sum

'''候选模式结构 data成员是对应序列，sup 支持度，prefix[]前缀，suffer[]后缀'''
class Candilist():
    def __init__(self,dataitems):
        self.data=dataitems
        self.sup =0
        self.prefix=[]
        self.suffer=[]

win=500   #窗口大小
minsup=1200 #最小支持度阈值
maxlen=1 #最长模式的长度
len_init=0  #初始数据库中序列个数
seqnum=24026
step=20
current_seq=win #始终指向当前数据库中最后一条序列
Fmap=[{'0':None} for i in range(1000)]#对应长度的模式集合
Infmap=[{'0':None} for i in range(1000)]
patternone={}#每个项最后一次出现的位置
candione={}#初始数据库单项候选模式
Nextlist=[]#各序列的Next数组集合
Next={}#存放Next数组结构,用于支持度计算(字典)每条序列的
poplist=[{'0':None} for i in range(2)]
seqs=[]#序列集合
lens=0#序列数量

def list_to_string(can):
    return ''.join('%s' % a for a in can)

def string_to_list(str):
    return list(str)

def preandsuf(p):
    if len(p.pattern)!=1:
        tp = copy.deepcopy(p.pattern)
        p.prefix=copy.deepcopy(p.pattern[0:-1])
        p.suffer=copy.deepcopy(p.pattern[1:])
        tp[0].pop(0)
        if len(tp[0])!=0:
            p.suffer.insert(0,tp[0])
        tp[-1].pop(-1)
        if len(tp[-1]) != 0:
            p.prefix.append(tp[-1])
    else:
        p.prefix.append(copy.deepcopy(p.pattern[0][0:-1]))
        p.suffer.append(copy.deepcopy(p.pattern[0][1:]))

'''  
 为相应序列创建一个Next数组，且只保存频繁项集的Next数组
 由于增量数据库可能出现新的项，在每次增量后之前计算的next数组也需要更新
'''
def getNext(l,r):
    i = l
    while i < r:
        j = 0
        while j < len(seqs[i]):
            k = 0
            while k < len(seqs[i][j].data):
                if l>0 and seqs[i][j].data[k] not in patternone.keys():
                    itemset=[]
                    itemset.append(Candilist(seqs[i][j].data[k]).data)
                    pattern=[]
                    pattern.append(itemset)
                    addNode(pattern,SupQueue(win),1,0)
                patternone[seqs[i][j].data[k]]=i
                if seqs[i][j].data[k] not in Next.keys():  # 每条序列创建一个Next数组
                    Next[seqs[i][j].data[k]] = [j]
                else:
                    Next[seqs[i][j].data[k]].append(j)
                k += 1
            j += 1
        Nextlist.append(copy.deepcopy(Next))
        Next.clear()
        i += 1

'''遍历序列，生成一长度候选模式,并且将频繁模式放入候选集合和频繁集合'''
def onepattern(seqs):
    i = 0
    while i < current_seq:
        j = 0
        while j < len(seqs[i]):
            k = 0
            while k < len(seqs[i][j].data):
                if seqs[i][j].data[k] not in candione.keys():
                    candione[seqs[i][j].data[k]] = 1
                k += 1
            j += 1
        i += 1
    '''将频繁模式顺序排放，放入候选集合和频繁集合'''
    for key in sorted(candione.keys()):
        temp = Candilist(key.split(","))
        temp.sup = candione.get(key)
        sup=SupQueue(win);
        trie = Tries(sup)
        itemset = []
        itemset.append(Candilist(key).data)
        trie.pattern.append(itemset)
        trie.len=1
        Infmap[1][list_to_string(trie.pattern)]=trie

'''计算支持度算法'''
def calsup(n,p):
    flag = 0
    out = 0
    que = []  # 存放Next数组
    count = 0  # 记存储Next顺序
    MaxIndex = -1
    useflag = {}  # 使用过的位置存放进来，保证多项集的一次性条件
    i=0
    p.sup=0
    while i<len(p.data):#创建抽出的Next数组
        j=0
        while j<len(p.data[i]):
            if p.data[i][j] in Nextlist[n].keys():
                temp = copy.deepcopy(Nextlist[n].get(p.data[i][j]))
                temp.insert(0, 1)  # 插入0为指针位置
                que.append(temp)
            else:
                return p.sup
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
                while que[count][0] < len(que[count]) and temp.count(que[count][que[count][0]]):#判断该项在这个位置是否用过
                    que[count][0] += 1
            if que[count][0] >= len(que[count]):
                flag = 1
                break
            if len(p.data[i])==1 and flag==0:#若为单项集
                if i==len(p.data)-1:
                    p.sup+=1
                max = que[count][que[count][0]]
                if p.data[i][0] not in useflag.keys():
                    useflag[p.data[i][0]]=[max]#标记该项为使用过
                else:
                    useflag[p.data[i][0]].append(max)
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
                        que[count+j][0]=que[count+j][1:].index(que[count][que[count][0]])
                        que[count+j][0]+=1
                        if i==len(p.data)-1 and j==len(p.data[i])-1:
                            p.sup+=1
                            #print(que)
                    j+=1
                if out==1:
                    out=0
                    break
                max = que[count][que[count][0]]
                if i == 0:
                    MaxIndex = max
                count+=len(p.data[i])
                j=0
                while j<len(p.data[i]) and flag==0:
                    if p.data[i][j] not in useflag.keys():
                        useflag[p.data[i][j]]=[max]  # 标记该项为使用过
                    else:
                        useflag[p.data[i][j]].append(max)
                    j+=1
            i+=1
        count=0
    return p.sup

'''l,r 需要计算支持度的序列范围 左闭右开   p 模式P    sup保存支持度计算结果'''
def newsup(l,r,p,sup):
    for i in range(l,r):
        sup.enqueue(calsup(i,p))
        sup.last_seq=r-1

def addNode(p,sup,length,flag):
    trie=Tries(sup)
    trie.pattern=p
    trie.len=length
    global  maxlen
    maxlen=max(maxlen,trie.len)
    str = list_to_string(trie.pattern)
    preandsuf(trie)
    if flag==1:
        Fmap[length][str]=trie
    else:
        Infmap[length][str]=trie

def updateNode(p,length):
    if length==1:
        tp = copy.deepcopy(p.pattern[-1])
        for key in Fmap[length].keys():
            ad = copy.deepcopy(Fmap[length][key].pattern[-1])
            tmp = []
            if ad[-1] > tp[-1]:
                tmp.append(tp + ad)
                addNode(tmp,SupQueue(win),length+1,0)
                tmp = []
            tmp.append(tp)
            tmp.append(ad)
            addNode(tmp,SupQueue(win),length+1,0)
        ad = copy.deepcopy(p.pattern[-1])
        for key in Fmap[length].keys():
            tp = copy.deepcopy(Fmap[length][key].pattern[-1])
            tmp = []
            if ad[-1] > tp[-1]:
                tmp.append(tp + ad)
                addNode(tmp, SupQueue(win), length + 1, 0)
                tmp = []
            tmp.append(tp)
            tmp.append(ad)
            addNode(tmp, SupQueue(win), length + 1, 0)
    else:
        for key in Fmap[length].keys():
            if operator.eq(p.prefix, Fmap[length][key].suffer):
                tmp = copy.deepcopy(Fmap[length][key].pattern)
                if len(p.pattern[-1]) == 1:  # S扩展
                    tmp.append(p.pattern[-1])
                else:  # I扩展
                    tmp[-1].append(p.pattern[-1][-1])
                addNode(tmp,SupQueue(win),length+1,0)
            if operator.eq(p.suffer, Fmap[length][key].prefix):
                tmp = copy.deepcopy(p.pattern)
                if len(Fmap[length][key].pattern[-1]) == 1:  # S扩展
                    tmp.append(Fmap[length][key].pattern[-1])
                else:  # I扩展
                    tmp[-1].append(Fmap[length][key].pattern[-1][-1])
                addNode(tmp,SupQueue(win),length+1,0)

'''读取数据'''
def conseqs():
    global ns
    with open("./Datasets/SDB2.txt", "r") as f:  # 打开文件
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

def updateSup(node):
    key=node.pattern
    pattern=Candilist(node.pattern)
    for i in range(node.last_seq+1,current_seq):
        if node.len>1:
            node.enqueue(calsup(i, pattern))
        elif key[-1][-1] in Nextlist[i].keys() :
            node.enqueue(len(Nextlist[i][key[-1][-1]]))
        else:
            node.enqueue(0)
    node.sup=node.supArr.sum
    node.last_seq = current_seq-1
for i in range(1000):
    Fmap[i].pop('0')
    Infmap[i].pop('0')
'''主流程'''
conseqs() #读入初始数据库
onepattern(seqs)#得到1长度模式
pretime=time.time()
for cur in range(current_seq,seqnum+1,step):
    current_seq=cur
    getNext(len_init,current_seq)
    print((time.time()-pretime))
    pretime=time.time()
    print('---------------------------------------------------')
    for i in range(1,10000):
        if len(Infmap[i].keys())<=0:
            break
        for key in Infmap[i].keys():
            updateSup(Infmap[i][key])
            if Infmap[i][key].sup >= minsup:
                Fmap[i][key] = Infmap[i][key]
                updateNode(Infmap[i][key], i)
    cnt = 0
    for i in range(1, maxlen + 1):
        for key in Fmap[i].keys():
            cnt += 1
    print(cnt)
    len_init = current_seq
