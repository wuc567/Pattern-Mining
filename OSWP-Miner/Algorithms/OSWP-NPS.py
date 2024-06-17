import sys
import time
import psutil
import os
sys.setrecursionlimit(1000000)
import copy
import operator

'''支持度字典结构 SupQueue类成员有窗口大小win，队尾指针tail， 数组arr 元素和sum '''


class SupQueue(object):
    def __init__(self, n=10):
        self.arr = [0] * (n + 1)  # 由于特意浪费了一个空间，所以arr的实际大小应该是用户传入的容量+1
        self.tail = 0
        self.win = n
        self.sum = 0
        self.isFull = False
        self.last_seq = -1

    def enqueue(self, e):  # 入队
        self.sum += e
        if self.isFull:
            self.sum -= self.arr[self.tail]
        self.arr[self.tail] = e
        if self.tail + 1 == self.win:
            self.isFull = True
        self.tail = (self.tail + 1) % self.win


'''
序列结构 Item类 具体的项
'''
class Item():
    def __init__(self, dataitems):
        self.data = dataitems


'''
Tries类 代表一个模式  成员对应支持度字典/模式/前后缀/支持度/模式长度/最后一次进行支持度计算的序列号
'''
class Tries():
    def __init__(self, supArr):
        self.supArr = supArr
        self.pattern = []
        self.sup = self.supArr.sum
        self.last_seq = supArr.last_seq
        self.prefix = []
        self.suffer = []
        self.len = 1

    def enqueue(self, e):
        self.supArr.enqueue(e)
        self.sup = self.supArr.sum


'''候选模式结构 data成员是对应序列，sup 支持度，prefix[]前缀，suffer[]后缀'''


class Candilist():
    def __init__(self, dataitems):
        self.data = dataitems
        self.sup = 0
        self.prefix = []
        self.suffer = []


'''
参数
'''
filename = "./Datasets/SDB1.txt"  # 数据集 文件路径/文件名
win = 150# 窗口大小
minsup = 7  # 最小支持度阈值
maxlen = 1  # 最长模式的长度
len_init = 0  # 初始数据库中序列个数
seqnum = 2759  # 数据库中序列总长度
step = 50  # 窗口每次滑动的长度
current_seq = win  # 始终指向当前数据库中最后一条序列
Fmap = [{} for i in range(1000)]  # 对应长度的模式集合
Infmap = [{} for i in range(1000)]
patternone = {}  # 每个项最后一次出现的位置
candione = {}  # 初始数据库单项候选模式
Nextlist =[{} for i in range(1510)]  # 各序列的Next数组集合
Next = {}  # 存放Next数组结构,用于支持度计算(字典)每条序列的
poplist = [{} for i in range(2)]
seqs = []  # 序列集合
lens = 0  # 序列数量
ml = []
Dict = [{} for i in range(1510)]  # 位置集合字典
useflag = [{} for i in range(1510)]  # 使用字典

def ActIndex(n):
    return n%win

max_number_of_fp=0
min_number_of_fp=1e9
avg_number_of_fp=0
avg_number_of_candi=0
'''
模式转换为对应的字符串
'''
def list_to_string(can):
    return ''.join('%s' % a for a in can)
def itemset_to_string(can):
    return ''.join(can)
'''
获取模式的前缀与后缀
'''
def preandsuf(p):
    if len(p.pattern) != 1:
        tp = copy.deepcopy(p.pattern)
        p.prefix = copy.deepcopy(p.pattern[0:-1])
        p.suffer = copy.deepcopy(p.pattern[1:])
        tp[0].pop(0)
        if len(tp[0]) != 0:
            p.suffer.insert(0, tp[0])
        tp[-1].pop(-1)
        if len(tp[-1]) != 0:
            p.prefix.append(tp[-1])
    else:
        p.prefix.append(copy.deepcopy(p.pattern[0][0:-1]))
        p.suffer.append(copy.deepcopy(p.pattern[0][1:]))


'''  
 为相应序列创建一个Next数组 即倒排索引
'''
def getNext(l, r):
    i = l
    while i < r:
        j = 0
        while j < len(seqs[i]):
            k = 0
            while k < len(seqs[i][j].data):
                if l > 0 and seqs[i][j].data[k] not in patternone.keys():
                    itemset = []
                    itemset.append(Candilist(seqs[i][j].data[k]).data)
                    pattern = []
                    pattern.append(itemset)
                    addNode(pattern, SupQueue(win), 1, 0)
                patternone[seqs[i][j].data[k]] = i
                if seqs[i][j].data[k] not in Next.keys():  # 每条序列创建一个Next数组
                    Next[seqs[i][j].data[k]] = [j]
                else:
                    Next[seqs[i][j].data[k]].append(j)
                k += 1
            j += 1
        Nextlist[ActIndex(i)]=copy.deepcopy(Next)
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
        sup = SupQueue(win);
        trie = Tries(sup)
        itemset = []
        itemset.append(Candilist(key).data)
        trie.pattern.append(itemset)
        trie.len = 1
        Infmap[1][list_to_string(trie.pattern)] = trie


'''使用深度优先搜索进行支持度计算'''
def dfs(i, n, p, len1, que, last):
    if i >= len1:
        p.sup += 1
        return True
    flag = 0
    res = False
    length = len(p.data[i])
    if length == 1:
        itemset = p.data[i][0]
    else:
        t=[]
        t.append(p.data[i])
        itemset = list_to_string(t)
        flag = 1
    length = ml[i]
    # if list_to_string(p.data) == "['10']['10', '212']" and n==4000:
    #     print(p.data[i])
    #     print("length=",length)
    #     print("level=",i)
    #     print("que[i]=",que[i])
    #     print("Last=",last)
    #     print(useflag[n][p.data[i][0]])
    if flag == 0:
        if que[i] >= length:
            return False
        while que[i] < length and Nextlist[ActIndex(n)].get(itemset)[que[i]] <= last:
            que[i] += 1
        while que[i] < length and Nextlist[ActIndex(n)].get(itemset)[que[i]] in useflag[ActIndex(n)][itemset]:
            que[i] += 1
        if que[i] >= length:
            return False
        if itemset not in useflag[ActIndex(n)].keys():
            useflag[ActIndex(n)][itemset] = [Nextlist[ActIndex(n)].get(itemset)[que[i]]]
        else:
            useflag[ActIndex(n)][itemset].append(Nextlist[ActIndex(n)].get(itemset)[que[i]])
        que[i] += 1
        res = dfs(i + 1, n, p, len1, que, Nextlist[ActIndex(n)].get(itemset)[que[i] - 1])
    else:
        if que[i] >= length:
            return False
        while que[i] < length and Dict[ActIndex(n)][itemset][que[i]] <= last:
            que[i] += 1
        while que[i] < length:
            f = 1
            position = Dict[ActIndex(n)][itemset][que[i]]
            if itemset not in useflag[ActIndex(n)].keys():
                useflag[ActIndex(n)][itemset] = []
            for item in p.data[i]:
                if item not in useflag[ActIndex(n)].keys():
                    useflag[ActIndex(n)][item] = []
                if position in useflag[ActIndex(n)][item]:
                    que[i] += 1
                    f = 0
                    break
            if que[i] >= length:
                return False
            if f == 1:
                break
        if que[i] < length:
            for item in p.data[i]:
                useflag[ActIndex(n)][item].append(Dict[ActIndex(n)][itemset][que[i]])
            que[i] += 1
            res = dfs(i + 1, n, p, len1, que, Dict[ActIndex(n)][itemset][que[i] - 1])
    return res


def calsup(n, p):  # 支持度计算
    i = 0
    que = []
    global ml
    ml = []
    useflag[ActIndex(n)].clear()
    while i < len(p.data):  # 创建抽出的Next数组
        que.append(0)
        t=[]
        t.append(p.data[i])
        if len(p.data[i]) == 1 and p.data[i][0] not in Nextlist[ActIndex(n)].keys():
            return p.sup
        if len(p.data[i]) == 1:
            useflag[ActIndex(n)][p.data[i][0]] = []
            ml.append(len(Nextlist[ActIndex(n)][p.data[i][0]]))
        elif list_to_string(t) not in Dict[ActIndex(n)].keys():
            update_itemset(n, p.data[i])
            ml.append(len(Dict[ActIndex(n)][list_to_string(t)]))
            if list_to_string(p.data) == "['10']['10', '212']" and n == 4000:
                print(Dict[ActIndex(n)][list_to_string(t)])
        else:
            if list_to_string(p.data) == "['10']['10', '212']" and n == 4000:
                print(Dict[ActIndex(n)][list_to_string(t)])
            ml.append(len(Dict[ActIndex(n)][list_to_string(t)]))
        i += 1
    # if list_to_string(p.data) == "['10']['10', '212']" and n==4000:
    #     print(ml)
    res = True
    while res:
        res = dfs(0, n, p, len(p.data), que, -1)

    return p.sup

'''新增一个结点'''
def addNode(p, sup, length, flag):
    trie = Tries(sup)
    trie.pattern = p
    trie.len = length
    global maxlen
    maxlen = max(maxlen, trie.len)
    str = list_to_string(trie.pattern)
    preandsuf(trie)
    if flag == 1:
        Fmap[length][str] = trie
    else:
        Infmap[length][str] = trie


'''判断模式a是否是模式b的子串  contain函数是判断一个项集是否是另一个项集的子集'''
def is_sub_pattern(p, s):
    pattern = p.pattern
    sequence = s.pattern
    len1 = 0
    len2 = 0
    while len1 < len(sequence) and len2 < len(pattern):
        if contain(pattern[len2], sequence[len1]):
            len2 += 1
        len1 += 1
    if len2 == len(pattern):
        return True
    return False


def contain(p, t):
    len1 = 0
    len2 = 0
    while len1 < len(t) and len2 < len(p):
        if p[len2] == t[len1]:
            len2 += 1
        len1 += 1
    if len2 == len(p):
        return True
    return False


'''窗口剪枝过程中 剪枝模式p  遍历的方式进行剪枝'''
def deleteNode(p, length):
    poplist[1][list_to_string(p.pattern)]=length


'''更新节点信息 支持度等'''
def updateNode(p, length):
    if length == 1:
        tp = copy.deepcopy(p.pattern[-1])
        for key in Fmap[length].keys():
            ad = copy.deepcopy(Fmap[length][key].pattern[-1])
            tmp = []
            if ad[-1] > tp[-1]:
                tmp.append(tp + ad)
                addNode(tmp, SupQueue(win), length + 1, 0)
                tmp = []
            tmp.append(tp)
            tmp.append(ad)
            addNode(tmp, SupQueue(win), length + 1, 0)
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
                addNode(tmp, SupQueue(win), length + 1, 0)
            if operator.eq(p.suffer, Fmap[length][key].prefix):
                tmp = copy.deepcopy(p.pattern)
                if len(Fmap[length][key].pattern[-1]) == 1:  # S扩展
                    tmp.append(Fmap[length][key].pattern[-1])
                else:  # I扩展
                    tmp[-1].append(Fmap[length][key].pattern[-1][-1])
                addNode(tmp, SupQueue(win), length + 1, 0)


'''读取数据'''
def conseqs():
    global ns
    with open(filename, "r") as f:  # 打开文件
        data = f.read()  # 读取文件
        f = 0
        temp = ''
        tempitem = []
        seq = []
        for c in data:
            if c == '\n':
                seqs.append(seq)
                seq = []
                continue
            if f == 1:
                f = 0
            elif c == ' ':
                tempitem.append(temp)
                temp = ''
            elif c == '-':
                f = 1
                item = Item(tempitem)
                seq.append(item)
                tempitem = []
            else:
                temp += c


def update(n, pattern):
    nx = []
    if pattern[0][0] in Nextlist[ActIndex(n)].keys():
        nx = copy.deepcopy(Nextlist[ActIndex(n)][pattern[0][0]])
    s = set(nx)
    for i in range(1, len(pattern[0])):
        if pattern[0][i] in Nextlist[ActIndex(n)].keys():
            s = s.intersection(set(Nextlist[ActIndex(n)][pattern[0][i]]))
        else:
            s.clear()
    t=[]
    t.append(pattern[0])
    Dict[ActIndex(n)][list_to_string(t)] = sorted(list(s))

def update_itemset(n, pattern):
    nx = []
    if pattern[0] in Nextlist[ActIndex(n)].keys():
        nx = copy.deepcopy(Nextlist[ActIndex(n)][pattern[0]])
    s = set(nx)
    for i in range(1, len(pattern)):
        if pattern[i] in Nextlist[ActIndex(n)].keys():
            s = s.intersection(set(Nextlist[ActIndex(n)][pattern[i]]))
        else:
            s.clear()
    t=[]
    t.append(pattern)
    Dict[ActIndex(n)][list_to_string(t)] = sorted(list(s))

def updateSup(node):
    key = node.pattern
    pattern = Candilist(node.pattern)
    for i in range(max(node.last_seq + 1,current_seq-win), current_seq):
        if len(key) == 1 and node.len > 1:
            if list_to_string(key) not in Dict[ActIndex(i)]:
                update(i, key)
        if node.len > 1:
            node.enqueue(calsup(i, pattern))
            # if list_to_string(node.pattern) == "['10']['10', '212']" and current_seq==4300 and node.supArr.tail>200 and node.supArr.tail<300:
            #     print(node.supArr.tail-1)
            #     print(node.supArr.arr[node.supArr.tail-1])
            #     print(i)
            #     print(seqs[i][0].data)
            pattern.sup = 0
        elif key[-1][-1] in Nextlist[ActIndex(i)].keys():
            node.enqueue(len(Nextlist[ActIndex(i)][key[-1][-1]]))
        else:
            node.enqueue(0)
    node.sup = node.supArr.sum
    node.last_seq = current_seq - 1


'''主流程'''
conseqs()  # 读入初始数据库
info = psutil.virtual_memory()
print(u'内存使用：',psutil.Process(os.getpid()).memory_info().rss/(1024*1024))
onepattern(seqs)  # 得到1长度模式
pretime = time.time()
start_time = time.time()
sliding_cnt=0
for cur in range(current_seq, seqnum + 1, step):
    current_seq = cur
    getNext(len_init, current_seq)
    print("sequence ", max(0, current_seq - win), "--sequence ", current_seq)
    print("time", (time.time() - pretime), 's')
    pretime = time.time()
    info = psutil.virtual_memory()
    print(u'内存使用：', psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024))
    print('---------------------------------------------------')
    for i in range(1, 10000):
        for key in Fmap[i].keys():
            updateSup(Fmap[i][key])
            if Fmap[i][key].sup < minsup:
                Infmap[i][key] = Fmap[i][key]
                poplist[1][key] = i

        for item in poplist[1].keys():
            length = poplist[1][item]
            if item in Fmap[length].keys():
                Fmap[length].pop(item)

        poplist[1].clear()
        for key in Infmap[i].keys():
            updateSup(Infmap[i][key])
            if Infmap[i][key].sup >= minsup:
                Fmap[i][key] = Infmap[i][key]
                updateNode(Infmap[i][key], i)
                poplist[0][key] = i
        if i > maxlen:
            break
    cnt = 0
    for i in range(1, maxlen + 1):
        for key in Fmap[i].keys():
            cnt += 1
            if current_seq == 4500:
                print(key, Fmap[i][key].sup,Fmap[i][key].supArr.arr)
            #print(key, Fmap[i][key].sup)
    max_number_of_fp = max(max_number_of_fp, cnt)
    min_number_of_fp = min(min_number_of_fp,cnt)
    avg_number_of_fp += cnt
    avg_number_of_candi += cnt
    print("frequent pattern number is ", cnt)
    cnt = 0
    for i in range(1, maxlen + 1):
        for key in Infmap[i].keys():
            if i>1:
                cnt += 1

            # print(key,Infmap[i][key].sup)
    print(cnt)
    avg_number_of_candi += cnt
    for i in range(current_seq-win, current_seq+step-win):
        Dict[ActIndex(i)].clear()
    len_init = current_seq
    sliding_cnt+=1
all_time = time.time() - start_time
avg_time=all_time/sliding_cnt
print("all time = ", all_time, "s")
print("avg time per sliding window is ",avg_time)
print("avg frequent patterns per sliding window is ",avg_number_of_fp//sliding_cnt)
print("avg candidate patterns per sliding window is ",avg_number_of_candi//sliding_cnt)
print("max frequent patterns of sliding window is ",max_number_of_fp)
print("min frequent patterns of sliding window is ",min_number_of_fp)
info = psutil.virtual_memory()
print(u'内存使用：',psutil.Process(os.getpid()).memory_info().rss/(1024*1024))
print(u'总内存：',info.total/(1024*1024))
print(u'内存占比：',info.percent)
print(u'cpu个数：',psutil.cpu_count())



