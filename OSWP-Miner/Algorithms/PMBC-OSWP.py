#支持度对比算法 根据PMBC算法实现
import operator
import os
import sys
import time

import psutil

sys.setrecursionlimit(1000000)
import copy
import operator
'''支持度数组结构 SupQueue类成员有窗口大小win，队尾指针tail， 数组arr 元素和sum '''
class SupQueue(object):
    def __init__(self, n=10):
        self.arr = [0] * (n+1)  # 由于特意浪费了一个空间，所以arr的实际大小应该是用户传入的容量+1
        self.tail = 0
        self.win=n
        self.sum=0
        self.isFull=False
        self.last_seq=-1
    def updateTail(self,e):
        if e>=self.win:
            self.isFull=True
        self.tail=e%self.win if e>=self.win else e

    def enqueue(self, e): # 入队
        self.sum += e
        if self.isFull:
            self.sum-=self.arr[self.tail]
        self.arr[self.tail] = e   #0123
        if self.tail + 1 == self.win:
            self.isFull = True
        self.tail = (self.tail+1) % self.win


'''
序列结构
Item类
'''
class Item():
    def __init__(self,dataitems):
        self.data=dataitems
        self.len=len(dataitems)
        self.flag=[]
        for i in range(self.len):
            self.flag.append(0)
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
        self.prefix=[]
        self.suffer=[]

win=150   #窗口大小
minsup=7 #最小支持度阈值
maxlen=1 #最长模式的长度
len_init=0  #初始数据库中序列个数
seqnum=2759
step=50
current_seq=win #始终指向当前数据库中最后一条序列
Fmap=[{} for i in range(1000)]#对应长度的模式集合
Infmap=[{} for i in range(1000)]
patternone={}#每个项最后一次出现的位置
candione={}#初始数据库单项候选模式
Nextlist=[]#各序列的Next数组集合
Next={}#存放Next数组结构,用于支持度计算(字典)每条序列的
poplist=[{} for i in range(2)]
seqs=[]#序列集合
lens=0#序列数量

'''读取数据'''
def conseqs():
    global ns
    with open("./Datasets/SDB1.txt", "r") as f:  # 打开文件
        data = f.read()  # 读取文件
        f=0
        temp=''
        tempitem = []
        seq = []
        for c in data:
            if c=='\n':
                seqs.append(seq)
                seq=[]
                continue
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

max_number_of_fp=0
min_number_of_fp=1e9
avg_number_of_fp=0
avg_number_of_candi=0

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
def sortitem(items):
    sort_item=[]
    for x in items:
        sort_item.append(int(x))
    sort_item.sort()
    return sort_item

'''判断模式每一个项集是否在序列项集中，即（bc）是否在（abc）中,s是item，p是列表;
如果p=(bc)(c),s中有（bc）,其中的c被先用了，则再次使用的时候这个s中的bc就不满足一次性条件了'''
''''''
def isinitem(s,p):
    i = 0
    j = 0
    while i < len(s.data) and j<len(p):
        if operator.eq(s.data[i], p[j]):
            j += 1
        i += 1
    if j == len(p):
        return True
    else:
        return False
'''将使用的序列中元素标记flag'''
def used(s,p):
    i=0
    j=0
    while i<len(p) and j<len(s.data):
        if p[i]==s.data[j]:
            s.flag[j]=1
            i += 1
            j += 1
        else:
            j+=1
def unused(s,p):
    i=0
    j=0
    while i<len(p) and j<len(s.data):
        if p[i]==s.data[j] and s.flag[j]==1:
            return False
        elif p[i]==s.data[j]:
            i += 1
            j += 1
        else:
            j+=1
    if i==len(p):
        return True
    return False
'''将序列标记归零use和flag'''
def useto0(i):
    j=0
    while j<len(seqs[i]):
        seqs[i][j].use=0
        k=0
        while k<len(seqs[i][j].data):
            seqs[i][j].flag[k]=0
            k+=1
        j+=1
    i+=1
'''PMBC算法中的scan-one-way策略计算支持度，针对一条序列的，需要循环输入多条序列'''
def calsup(n,p):
    sup=0
    s=seqs[n]
    pos=[[]]*(len(p.data)+10)
    for i in range(0,len(p.data)):
        for j in range(0,len(s)):
            if isinitem(s[j],p.data[i]):
                pos[i].append(j)
    i=0
    while i<len(s):
        j=0
        while j<len(p.data) and i<len(s):
            if i in pos[j] and unused(s[i],p.data[j]):
                used(s[i], p.data[j])
                j+=1
            if j==len(p.data):
                sup+=1
                i=0
            i+=1
    useto0(n)
    return sup
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

def contain(p,t):
    len1=0
    len2=0
    while len1<len(t) and len2<len(p):
        if p[len2]==t[len1]:
            len2+=1
        len1+=1
    if len2==len(p):
        return True
    return False
def is_sub_pattern(p,s):
    pattern=p.pattern
    sequence=s.pattern
    len1=0
    len2=0
    while len1<len(sequence) and len2<len(pattern):
        if contain(pattern[len2], sequence[len1]):
            len2+=1
        len1+=1
    if len2==len(pattern):
        return True
    return False
def deleteNode(p,length):
    for i in range(length+1,10000):
        cnt=0
        for key in Fmap[i].keys():
            if is_sub_pattern(p,Fmap[i][key]):
                cnt+=1
                poplist[1][key] = i
        for key in Infmap[i].keys():
            if is_sub_pattern(p,Infmap[i][key]):
                cnt+=1
                poplist[0][key] = i
        if cnt==0:
            break

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


def updateSup(node):
    key=node.pattern
    pattern=Candilist(node.pattern)
    for i in range(max(node.last_seq+1,current_seq-win),current_seq):
        if node.len>=1:
            node.enqueue(calsup(i, pattern))
        else:
            node.enqueue(0)
    #print(node.pattern,node.sup)
    #print(node.supArr.arr)
    node.sup=node.supArr.sum
    node.last_seq = current_seq-1
'''主流程'''
conseqs() #读入初始数据库
info = psutil.virtual_memory()
print(u'内存使用：',psutil.Process(os.getpid()).memory_info().rss/(1024*1024))
onepattern(seqs)#得到1长度模式
i=0
sliding_cnt=0
for i in range(len(seqs)):
    j=0
    for j in range(len(seqs[i])):
        seqs[i][j].data=sorted(seqs[i][j].data)
start_time = time.time()
pretime=time.time()
for cur in range(current_seq,seqnum+1,step):
    current_seq=cur
    print((time.time()-pretime))
    pretime=time.time()
    info = psutil.virtual_memory()
    print(u'内存使用：', psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024))
    print('---------------------------------------------------')
    for i in range(1,100):
        for key in Fmap[i].keys():
            updateSup(Fmap[i][key])
            if Fmap[i][key].sup < minsup:
                Infmap[i][key] = Fmap[i][key]
                poplist[1][key] = i
                deleteNode(Infmap[i][key], i)

        for item in poplist[1].keys():
            length = poplist[1][item]
            if item in Fmap[length].keys():
                Fmap[length].pop(item)
        for item in poplist[0].keys():
            length = poplist[0][item]
            if item in Infmap[length].keys():
                Infmap[length].pop(item)
        poplist[0].clear()
        poplist[1].clear()
        for key in Infmap[i].keys():
            updateSup(Infmap[i][key])
            if Infmap[i][key].sup >= minsup:
                Fmap[i][key] = Infmap[i][key]
                # print(key,Fmap[i][key].sup,Fmap[i][key].supArr.arr)
                updateNode(Infmap[i][key], i)
                poplist[0][key] = i
        if i > maxlen:
            break
    cnt = 0
    for i in range(1, maxlen + 1):
        for key in Fmap[i].keys():
            cnt += 1
            # print(key, Fmap[i][key].sup)
    max_number_of_fp = max(max_number_of_fp, cnt)
    min_number_of_fp = min(min_number_of_fp, cnt)
    avg_number_of_fp += cnt
    avg_number_of_candi += cnt
    print("frequent pattern number is ", cnt)
    cnt = 0
    for i in range(1, maxlen + 1):
        for key in Infmap[i].keys():
            if i > 1:
                cnt += 1
            # print(key,Infmap[i][key].sup)
    print(cnt)
    avg_number_of_candi += cnt
    len_init = current_seq
    sliding_cnt += 1
all_time = time.time() - start_time
avg_time = all_time / sliding_cnt
print("all time = ", all_time, "s")
print("avg time per sliding window is ", avg_time)
print("avg frequent patterns per sliding window is ", avg_number_of_fp // sliding_cnt)
print("avg candidate patterns per sliding window is ", avg_number_of_candi // sliding_cnt)
print("max frequent patterns of sliding window is ", max_number_of_fp)
print("min frequent patterns of sliding window is ", min_number_of_fp)
info = psutil.virtual_memory()
print(u'内存使用：', psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024))
print(u'总内存：', info.total / (1024 * 1024))
print(u'内存占比：', info.percent)
print(u'cpu个数：', psutil.cpu_count())
