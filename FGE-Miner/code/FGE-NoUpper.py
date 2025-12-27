from pm4py.objects.log.importer.xes import importer as xes_importer
from memory_profiler import memory_usage
from dateutil import parser
from datetime import timedelta
import sys
sys.setrecursionlimit(1000000)
import time
import copy
import csv
import os

'''序列结构'''
class Item():
    def __init__(self, dataitems):
        self.data = dataitems
        self.len = len(dataitems)
        self.flag = []
        i = 1
        for i in range(self.len):
            self.flag.append(0)

'''候选模式结构'''
class Candilist():
    def __init__(self, dataitems):
        self.data = dataitems
        self.sup = 0
        self.prefix = []
        self.suffer = []

# Elog1 BPIC15_1.xes range(200)-7710
# csup = 0.0172
# fsup = 0.0174
# maxtime = 3024000
# Elog2 BPIC15_2.xes range(300)-14588
csup = 0.0149
fsup = 0.0151
maxtime = 3024000
# Elog3 BPIC15_3.xes range(300)-11524
# csup = 0.0214
# fsup = 0.0215
# maxtime = 3024000
# ELog4 BPIC15_4.xes range(300)-12282
# csup = 0.0191
# fsup = 0.0193
# maxtime = 3024000  # (5 week)
# ELog5 BPIC15_5.xes range(300)-13782
# csup = 0.0177
# fsup = 0.0179
# maxtime = 3024000  # (5 week)
# ELog6 BPI_Challenge_2019.xes range(600)-9975
# csup = 0.0239
# fsup = 0.0241
# maxtime = 86400  # (1 day)
# Elog7
# csup = 0.073
# fsup = 0.078
# maxtime = 9000
# Elog8
# csup = 0.115
# fsup = 0.117
# maxtime = 9000

def group_and_extract(activity_chart, timestamp_list):
    if not activity_chart or not timestamp_list or len(activity_chart) != len(timestamp_list):
        return [], []

    seqs = []  # 存储分组后的list1
    timestamp_s = []  # 存储每个分组对应的唯一值
    current_group = []
    current_value = None

    for item, value in zip(activity_chart, timestamp_list):
        if current_value is None:
            # 处理第一个元素
            current_group = [item]
            current_value = value
        elif value == current_value:
            # 值相同，继续当前分组
            current_group.append(item)
        else:
            # 值不同，结束当前分组
            seqs.append(Item(copy.deepcopy(current_group)))
            timestamp_s.append(current_value)
            current_group = [item]
            current_value = value

    # 添加最后一个分组
    if current_group:
        seqs.append(Item(copy.deepcopy(current_group)))
        timestamp_s.append(current_value)

    return seqs, timestamp_s

def con_seqs(activity_chart, timestamp_list):
    seqs = []
    timestamp_s = []
    # 2. 多序列
    for i in range(len(activity_chart)):
        seq, timestamp_l = group_and_extract(activity_chart[i], timestamp_list[i])
        seqs.append(seq)
        timestamp_s.append(timestamp_l)
    return seqs, timestamp_s

'''
    读取csv文件，结果格式为
    {测试者: {day_1:[[activity],[timestamp]],day_2:[[activity],[timestamp]]}}
'''
def read_csv(origin_data_folder_address):
    trace_per = dict()   # {5: {1:[[activity],[timestamp]],2:[[activity],[timestamp]]}}
    subjectId = 0
    file_list = os.listdir(origin_data_folder_address)  # 获取文件夹下的所有文件名称
    for file_name in file_list:
        # print(file_name)
        if ".csv" in file_name:
            # print(origin_data_folder_address + file_name)  # 读取文件
            with open(origin_data_folder_address + file_name, 'r') as file:
                reader = csv.reader(file)
                trace_day = dict()  # {1:[[activity],[timestamp]],2:[[activity],[timestamp]]}
                i = 0  # 去除标题
                day_identity = 0
                activity_list = list()
                timestamp_list = list()
                for row in reader:
                    if i == 0:
                        i = i + 1
                    else:
                        if day_identity != row[1]:
                            if day_identity != 0:
                                trace_day[day_identity] = [copy.deepcopy(activity_list),copy.deepcopy(timestamp_list)]
                            day_identity = row[1]
                            activity_list.clear()
                            timestamp_list.clear()
                            activity_list.append(row[5])
                            timestamp_list.append(parser.parse(row[4]))
                        else:
                            activity_list.append(row[5])
                            timestamp_list.append(parser.parse(row[4]))
                    if i == 1:
                        subjectId = row[2]
                trace_per[subjectId] = copy.deepcopy(trace_day)
    return trace_per

'''
    处理成情节挖掘所需格式
'''
def data_preprocess(trace_per):
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    # 1. 合并为单序列
    for vals in trace_per.values():
        for svals in vals.values():
            activity_chart.extend(svals[0])
            timestamp_list.extend(svals[1])
    # 2. 以轨迹为序列，一个日志多个轨迹，即多条序列
    # for vals in trace_per.values():
    #     for svals in vals.values():
    #         activity_chart.append(svals[0])
    #         timestamp_list.append(svals[1])
    return activity_chart, timestamp_list

'''
    读取xes文件
'''
def read_xes(file_address):
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    event_log = xes_importer.apply(file_address,  # 引号中的为文件地址
                                   variant=variant, parameters=parameters)
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    # 1. 合并为单序列
    # for t in range(2000):
    #     for e in event_log[t]:
    #         activity_chart.append(e["concept:name"])
    #         timestamp_list.append(e['time:timestamp'])
    # 2. 以轨迹为序列，一个日志多个轨迹，即多条序列
    for t in range(300):
        activity_e = []
        timestamp_t = []
        for e in event_log[t]:
            activity_e.append(e["concept:name"])
            timestamp_t.append(e['time:timestamp'])
        activity_chart.append(activity_e)
        timestamp_list.append(timestamp_t)
    return activity_chart, timestamp_list

# 读取TXT文件
def read_file(file_path):
    seqs = []
    with open(file_path, "r") as f:  # 打开文件
        data = f.read()  # 读取文件
        f = 0
        temp = ''
        tempitem = []
        seq = []
        for c in data:
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
            if c == '\n':
                seqs.append(seq)
                seq = []
    return seqs

# 读取TXT文件
def read_file2(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # map作用于每个可迭代对象的元素，并返回处理之后的元素;filter作用于可迭代内每个元素，根据计算后结果：True保留，Flase去掉
    # 去除首尾空格
    temp = list(filter(lambda x: x.strip() and x != 'NA\n', lines))
    # 去除\n
    return list(map(lambda x: x.strip('\n'), temp))

# 合成事件序列
def compose_timestamp(log_data):
    date_time1 = parser.parse("2015-03-16 11:32:29")
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    for data_e in log_data:
        for e in data_e:
            date_time1 = date_time1 + timedelta(minutes=10)
            activity_chart.append(e)
            timestamp_list.append(date_time1)
    return activity_chart, timestamp_list

def compose_timestamp_scalability(log_data):
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    date_time1 = parser.parse("2015-03-16 11:32:29")
    for data_e in log_data:
        activity_chart_e = []
        timestamp_list_e = []
        for e in data_e:
            date_time1 = date_time1 + timedelta(minutes=10)
            activity_chart_e.append(e)
            timestamp_list_e.append(date_time1)
        activity_chart.append(activity_chart_e)
        timestamp_list.append(timestamp_list_e)
    return activity_chart, timestamp_list

'''
   遍历序列，生成1长度候选模式,并且将频繁模式放入候选集合和频繁集合
   给每条序列创建一个Next数组，且只保存频繁项集的Next数组
'''
def onepattern(seqs, Lminsup):
    candiones = {}
    '''候选模式列表'''
    fre_patt = []
    '''候选模式集合（列表）'''
    candi = []
    '''频繁模式集合'''
    FPItem = []
    '''频繁模式过渡集合'''
    FP = []

    '''各序列的Next数组集合'''
    Nextlist = []
    '''存放Next数组结构,用于支持度计算(字典)每条序列的'''
    Next = {}

    i = 0
    while i < len(seqs):  # 序列库
        j = 0
        while j < len(seqs[i]):  # 序列
            k = 0
            while k < len(seqs[i][j].data):  # 项集
                # 统计单项的支持度
                if seqs[i][j].data[k] not in candiones.keys():
                    candiones[seqs[i][j].data[k]] = 1
                    candi.append(Candilist([seqs[i][j].data[k]]))
                else:
                    candiones[seqs[i][j].data[k]] = candiones.get(seqs[i][j].data[k]) + 1
                # 构建位置索引
                if seqs[i][j].data[k] not in Next.keys():  # 每条序列创建一个Next数组
                    Next[seqs[i][j].data[k]] = [j]
                else:
                    Next[seqs[i][j].data[k]].append(j)
                k += 1
            j += 1
        # 每条序列各有一个位置索引
        Nextlist.append(copy.deepcopy(Next))
        Next.clear()
        i += 1

    '''将频繁模式顺序排放，放入候选集合和频繁集合'''
    candione = dict(sorted(candiones.items(), key=lambda x: x[1]))

    for key in sorted(candione.keys()):
        if candione.get(key) >= Lminsup:
            temp = Candilist(key.split(","))
            temp.sup = candione.get(key)
            FPItem.append(temp)
        else:
            i = 0
            while i < len(Nextlist):
                if key in Nextlist[i].keys():
                    del Nextlist[i][key]
                i += 1
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
        fre_patt.append([str(sort_item[i])])
        # fre_patt[[str(sort_item[i])]] = temp.sup
        i += 1
    return sort_item, Nextlist, candi, fre_patt, FPItem, FP

'''
    验证时间范围
'''
def time_ok(timestamp_list, n, s_strart, s_end):
    #
    time_start = timestamp_list[n][s_strart]
    time_end = timestamp_list[n][s_end]
    interval = time_end - time_start
    intersec = interval.total_seconds()
    if intersec > maxtime or intersec < 0:
        return 0
    return 1

'''
    计算支持度算法
    参数：序列，第几个序列，模式
'''
def newsup(timestamp_list, n, p, Nextlist):
    #
    addlist = []
    flag = 0
    que = []  # 存放Next数组
    count = 0  # 记存储Next顺序
    MaxIndex = -1
    useflag = {}  # 使用过的位置存放进来，保证多项集的一次性条件
    usearray = []  # 临时存储模式匹配位置
    i = 0
    # 根据模式构建Next数组结构
    while i < len(p.data):
        # 如果是单项则取单项，如果是项集则取元组{'a': [0, 4, 5, 6, 8], ('a', 'e'): [0, 5, 6]}
        if len(p.data[i]) == 1:
            k = p.data[i][0]
        else:
            k = tuple(p.data[i])
        if k in Nextlist[n].keys():
            temp = copy.deepcopy(Nextlist[n].get(k))
            # if p.data == [['a', 'c'], ['b', 'c']]:
            #     print(n, k, temp)
            temp.insert(0, 1)  # 插入0为指针位置，表示该项next所在位置
            que.append(temp)
        else:
            return addlist
        i += 1

    while flag == 0:
        i = 0
        max = MaxIndex
        while i < len(p.data):
            # 第一个位置就要大于上一个元素的索引，如果不满足则指针后移
            while que[count][0] < len(que[count]) and que[count][que[count][0]] <= max:
                que[count][0] += 1
            # 如何保证一次性条件？例如 [['e']['b','e']]
            m = 0
            merger_list = []
            while m < len(p.data[i]):
                if p.data[i][m] in useflag.keys():
                    temp = useflag.get(p.data[i][m])  # 该项已使用位置列表
                    merger_list = merger_list + temp
                    # if n == 7 and p.data == [['a', 'c'], ['c'], ['a']]:
                    #     print(p.data[i][m], temp)
                    #     print(que[count][que[count][0]], temp.count(que[count][que[count][0]]))
                m += 1
            while que[count][0] < len(que[count]) and merger_list.count(que[count][que[count][0]]):  # count()方法返回列表中某个元素的出现次数
                # if n == 7 and p.data == [['a', 'c'], ['c'], ['a']]:
                #     print(que[count][que[count][0]], temp.count(que[count][que[count][0]]))
                que[count][0] += 1

            if que[count][0] >= len(que[count]):
                flag = 1
                break

            if i != 0:
                # 是否满足时间约束
                gaptime_flag = time_ok(timestamp_list, n, usearray[-1], que[count][que[count][0]])
                if not gaptime_flag:  # 不满足时间约束,回溯
                    count = count - 1
                    # que[count][0] += 1
                    # if que[count][0] >= len(que[count]):
                    #     flag = 1
                    #     break
                    i = i - 1
                    # max应该随着层级的变化有所变化
                    max = usearray[-1]
                    usearray.pop()
                    continue

            max = que[count][que[count][0]]
            usearray.append(max)
            if i == len(p.data) - 1:
                # 这里也不对，这里是按照项存储出现位置，但是按照项集查找的出现位置，应该将项集中的每个单项进行存储
                a = 0
                k = 0
                while a < len(p.data):
                    b = 0
                    while b < len(p.data[a]):
                        if p.data[a][b] not in useflag.keys():
                            useflag[p.data[a][b]] = [usearray[k]]  # 标记该项为使用过
                        else:
                            useflag[p.data[a][b]].append(usearray[k])
                        b += 1
                    k += 1
                    a += 1
                p.sup += 1
                # if n==7 and p.data == [['a', 'c'], ['c'], ['a']]:
                #     print(usearray)
                addlist.append(copy.deepcopy(usearray))
                usearray.clear()
            if i == 0:
                MaxIndex = max
            count += 1
            i += 1
        count = 0
    return addlist


'''一次性标记'''
def init_bool(seqs):
    i = 0
    while i < len(seqs):
        j = 0
        while j < len(seqs[i]):
            # seqs[i][j].use = 0
            k = 0
            while k < seqs[i][j].len:
                seqs[i][j].flag[k] = 0
                k += 1
            j += 1
        i += 1

'''将使用的序列中元素标记flag'''
def labflag(s, p):
    i = 0
    j = 0
    while i < len(p) and j < len(s.data):
        if p[i] == s.data[j]:
            s.flag[j] = 1
            i += 1
            j += 1
        else:
            j += 1

# 项集序列中某个字符是否被使用
def isinuse(s, p):
    i = 0
    while i < len(p):
        if p[i] not in s.data:
            return False
        idx = s.data.index(p[i])
        if s.flag[idx] == 1:
            return True
        i += 1
    return False

'''
    判断模式每一个项集是否在序列项集中，即（bc）是否在（abc）中,s是item，p是列表;
    如果p=(bc)(c),s中有（bc）,其中的c被先用了，则再次使用的时候这个s中的bc就不满足一次性条件了
'''
def isinitem(s, p):
    i = 0
    while i < len(p):
        if p[i] not in s.data:
            return False
        i += 1
    return True


def no_que(timestamp_s, n, seq, pattern):
    addlist = []
    usearray = []  # 标记本轮已用结点
    sflag = 1  # 判断是否终止循环
    k = 0
    while k < len(seq) and sflag:
        m = 0
        l = k
        pflag = 1  # 是否终止模式循环
        while m < len(pattern.data) and pflag:
            while l < len(seq):
                # if pattern.data == [['a'], ['b']] and n == 9:
                #     print(pattern.data[m], seq[l].data, isinitem(seq[l], pattern.data[m]), isinuse(seq[l], pattern.data[m]))
                if isinitem(seq[l], pattern.data[m]) and not isinuse(seq[l], pattern.data[m]):
                    if m != 0:
                        # 如果不满足时间约束，应该回溯
                        gaptime_flag = time_ok(timestamp_s, n, usearray[-1], l)
                        #
                        if not gaptime_flag:  # 不满足时间约束
                            m = m - 1
                            l = usearray[-1] + 1
                            usearray.pop()
                            continue
                    #
                    usearray.append(l)
                    # 模式匹配成功
                    if m == len(pattern.data) - 1:
                        j = 0
                        while j < len(pattern.data):
                            labflag(seq[usearray[j]], pattern.data[j])
                            j += 1
                        pattern.sup += 1
                        addlist.append(copy.deepcopy(usearray))
                        usearray.clear()
                        pflag = 0
                        break
                    if m == 0:
                        k = l + 1
                    m = m + 1
                    l = l + 1
                    continue
                l = l + 1
            # 结束循环
            if l >= len(seq):
                sflag = 0
                break
    return addlist

def oneepisode(seqs, p):
    sup_p = 0
    i = 0
    while i < len(seqs):  # 序列库
        j = 0
        while j < len(seqs[i]):  # 序列
            k = 0
            while k < len(seqs[i][j].data):  # 项集
                # 统计单项的支持度
                if seqs[i][j].data[k] == p[0]:
                    sup_p += 1
                k += 1
            j += 1
        i += 1
    return sup_p

def transform_rules(rule):
    first_sublist = rule[0]
    # 处理第一个子列表有多个元素的情况
    if len(first_sublist) > 1:
        last_element = first_sublist[1:]
        new_rule = [last_element] + rule[1:]
    # 处理第一个子列表只有一个元素的情况
    else:
        # 直接保留第一个子列表之后的所有子列表
        new_rule = rule[1:]
        # 特殊处理：如果结果只有一个元素且是单元素列表，则展平
    if len(new_rule) == 1 and len(new_rule[0]) == 1:
        return new_rule[0]
    else:
        return new_rule

def transform_rules_pre(rule):
    last_sublist = rule[-1]
    # 处理第一个子列表有多个元素的情况
    if len(last_sublist) > 1:
        last_element = last_sublist[0:-1]
        new_rule = rule[0:-1] + [last_element]
    # 处理第一个子列表只有一个元素的情况
    else:
        # 直接保留第一个子列表之后的所有子列表
        new_rule = rule[0:-1]
        # 特殊处理：如果结果只有一个元素且是单元素列表，则展平
    if len(new_rule) == 1 and len(new_rule[0]) == 1:
        return new_rule[0]
    else:
        return new_rule

# 二叉树层序遍历
def get_sub_value(dict1, pattern):
    patt = to_immulist(pattern)
    que = []
    # 如果size是1，则不存在返回-1
    if len(patt) == 1 and type(patt[0]) == str:
        return -1
    pre_patt = transform_rules_pre(patt)
    suf_patt = transform_rules(patt)
    que.append(to_immutable(pre_patt))
    que.append(to_immutable(suf_patt))
    while que:
        node = que.pop(0)
        if node in dict1:
            return dict1.get(node)
        patt_node = to_immulist(node)
        if len(patt_node) == 1 and type(patt_node[0]) == str:
            continue
        else:
            pre_node = transform_rules_pre(patt_node)
            suf_node = transform_rules(patt_node)
            que.append(to_immutable(pre_node))
            que.append(to_immutable(suf_node))
    return -1

'''S/I连接生成候选模式'''
def sandilinked(sort_item, FP, fre_patt, candi):
    i = 0
    while i < len(FP):
        j = 0
        while j < len(sort_item):
            # s-连接
            if len(FP[i].data) == 1 and type(FP[i].data[0]) == str:
                temp = [copy.deepcopy(FP[i].data)]
            else:
                temp = copy.deepcopy(FP[i].data)
            temp.append([sort_item[j]])
            # 添加之前先校验最大后缀是否在FP中，如果不在，则直接剪枝
            suf_temp = transform_rules(temp)
            # print(temp, '->', suf_temp)
            if suf_temp in fre_patt:
                candi.append(Candilist(temp))

            # I-连接
            if type(FP[i].data[-1]) == str:
                lastidx = sort_item.index(FP[i].data[-1])
            else:
                lastidx = sort_item.index(FP[i].data[-1][-1])
            if j > lastidx:
                temp = copy.deepcopy(FP[i].data)
                if type(temp[-1]) == str:
                    temp.append(sort_item[j])
                    suf_temp = transform_rules([temp])
                    # if temp == ['a', 'b']:
                    #     print(temp, '->', suf_temp)
                    if suf_temp in fre_patt:
                        candi.append(Candilist([temp]))
                else:
                    temp[-1].append(sort_item[j])
                    suf_temp = transform_rules(temp)
                    # if temp == ['a', 'b']:
                    #     print(temp, '->', suf_temp)
                    if suf_temp in fre_patt:
                        candi.append(Candilist(temp))
            j += 1
        i += 1
    return candi

def transform_suf_pre(rule):
    suf_rule = rule[0][1:]
    pre_rule = rule[0][:-1]
    return suf_rule, pre_rule

def count_inner_elements(list1):
    total = 0
    for sublist in list1:        # 遍历外层列表的每个子列表
        for inner_list in sublist:  # 遍历子列表中的每个内层列表
            total += len(inner_list.data)  # 累加内层列表的长度
    return total

'''每个客户端频繁情节'''
def client_episodes(seqs, timestamp_s, result):
    candinum = []  # 候选模式不同长度起始位置
    Lminsup = result * csup
    # print('支持度阈值', result, Lminsup)

    sort_item, Nextlist, candi, fre_patt, FPItem, FP = onepattern(seqs, Lminsup)  # 1序列模式及位置索引,0->1
    sort_item = list(map(str, sort_item))
    candinum.append(len(candi))
    candi = sandilinked(sort_item, FP, fre_patt, candi)  # 1->2
    candinum.append(len(candi))
    FP.clear()
    fre_patt.clear()
    while 1:
        cannum = candinum.pop(0)
        i = cannum
        while i < len(candi):
            j = 0
            while j < len(seqs):
                p = candi[i].data
                # 这个时候需要判断下，如果size=1，则使用规则1，否则使用规则2
                # size=1的情节需要存储出现位置
                # 在这个位置判断size是否为1,采用不同点的规则，因为（abcd）长度为4，size也为1
                if len(p) == 1:
                    p_suf, p_pre = transform_suf_pre(p)
                    if len(p_suf) == 1:
                        k_suf = p_suf[0]
                    else:
                        k_suf = tuple(p_suf)
                    if len(p_pre) == 1:
                        k_pre = p_pre[0]
                    else:
                        k_pre = tuple(p_pre)
                    # 遍历Nextlist中的每个字典
                    for d in Nextlist:
                        # 遍历p中的每个模式（如['a','e']）
                        # 将模式列表转换为元组，作为新键
                        key_tuple = tuple(p[0])
                        # 获取当前模式中所有键对应的列表
                        list_suf = d.get(k_suf, [])
                        list_pre = d.get(k_pre, [])
                        intersection = set(list_suf)
                        intersection &= set(list_pre)
                        # 将交集转换为排序后的列表，并添加到字典
                        d[key_tuple] = sorted(intersection)

                    # 计算模式的支持度 sup_p
                    sup_p = 0
                    for d in Nextlist:
                        tuple_key = tuple(p[0])
                        if tuple_key in d:
                            # 累加交集列表的长度
                            sup_p += len(d[tuple_key])
                    candi[i].sup = sup_p
                    # 如果支持度小于阈值，将位置索引列表进行删除
                    if sup_p < Lminsup:
                        k = 0
                        while k < len(Nextlist):
                            if tuple(p[0]) in Nextlist[k].keys():
                                del Nextlist[k][tuple(p[0])]
                            k += 1
                else:
                    addlist = newsup(timestamp_s, j, candi[i], Nextlist)
                j += 1

            # if candi[i].data == [['d'], ['d']]:
            #     print(candi[i].data, '支持度-->', candi[i].sup)

            if candi[i].sup >= Lminsup:
                FP.append(candi[i])
                fre_patt.append(candi[i].data)
                FPItem.append(candi[i])
            i += 1
        candi = sandilinked(sort_item, FP, fre_patt, candi)
        FP.clear()
        fre_patt.clear()
        if cannum == len(candi):
            break
        else:
            candinum.append(len(candi))
    # print('--------------')
    # i = 0
    # while i < len(candi):
    #     print(str(candi[i].data) + ":" + str(candi[i].sup))
    #     i += 1
    return FPItem, candi, Lminsup

'''某个情节在客户端支持度'''
def client_episodes_one(seqs, timestamp_s, pattern):
    p = pattern.data
    # if p == [['d'], ['d']]:
    #     print(len(seqs), pattern.sup)
    # 如果是单项['h']需要特殊处理
    if isinstance(p[0], str):
        pattern.sup = oneepisode(seqs, p)
    else:
        j = 0
        while j < len(seqs):
            addlist = no_que(timestamp_s, j, seqs[j], pattern)
            j += 1
        init_bool(seqs)
        # if p == [['d'], ['d']]:
        #     print(pattern.sup)
    return pattern.sup

def to_immutable(obj):
    if isinstance(obj, list):
        return tuple(to_immutable(x) for x in obj)
    return obj

def to_immulist(obj):
    if isinstance(obj, tuple):
        return list(to_immulist(x) for x in obj)
    return obj

#
def get_result_value(result, pattern):
    patt = to_immulist(pattern)
    # 如果size是1，则不存在返回-1
    if len(patt) == 1 and type(patt[0]) == str:
        return 1
    pre_patt = transform_rules_pre(patt)
    suf_patt = transform_rules(patt)
    if to_immutable(pre_patt) in result and to_immutable(suf_patt) in result:
        return 1
    else:
        return 0


def zip_code_value(k, clients_rem, seqs, clients, timestamp_s):
    rem_sup = 0
    pattern = Candilist(to_immulist(k))
    for i in clients_rem:
        pattern.sup = 0
        rem_s = client_episodes_one(seqs[clients.get(i)[0]:clients.get(i)[1]],
                                    timestamp_s[clients.get(i)[0]:clients.get(i)[1]], pattern)
        rem_sup += rem_s
    return rem_sup

def merge_dicts_backward(input_dict, fminsup, clients_all, seqs, timestamp_s, clients, clientsSup):
    filter_result = {}
    result = {}
    # 标记某个情节上传支持度信息客户端列表
    occurrence_dict = {}
    for outer_key, dict_list in input_dict.items():  # 遍历输入字典的每个键
        processed_keys = set()
        for d in dict_list:  # 遍历列表中的每个字典
            # if d.data == [['d'], ['d']]:
            #     print('上传的h的支持度', outer_key, '--->', d.sup)
            data = to_immutable(d.data)
            result[data] = result.get(data, 0) + d.sup

            if data not in processed_keys:
                processed_keys.add(data)
                # 将外层键添加到occurrence_dict
                if data not in occurrence_dict:
                    occurrence_dict[data] = []
                occurrence_dict[data].append(outer_key)
    # 判断情节支持度是否大于阈值，如果小于阈值，则需要判断是否所有客户端都上传了支持度信息，如果没有，则需要在剩下客户端中查找该情节的支持度
    for k, v in result.items():
        if v >= fminsup:
            filter_result[k] = v
        else:
            # 先检查该情节的前后缀是否都是频繁的，如果不是则该情节肯定不是，直接过
            if get_result_value(filter_result, k):
                # 先检查在未上传支持度信息的父情节是否存在
                clients_list = occurrence_dict.get(k)
                clients_rem = set(clients_all) - set(clients_list)
                sum_rem = 0
                for key in clients_rem:
                    if key in clientsSup:
                        # 将值转换为整数（截断小数部分）并累加
                        sum_rem += int(clientsSup[key])
                if sum_rem >= fminsup - v:
                    rem_sup = zip_code_value(k, clients_rem, seqs, clients, timestamp_s)
                    all_sup = rem_sup + v
                    if all_sup >= fminsup:
                        filter_result[k] = all_sup
    # 使用字典推导式过滤值大于等于fminsup的项
    return filter_result

def merge_dicts(input_dict, fminsup):
    result = {}
    # 标记某个情节上传支持度信息客户端列表
    for key in input_dict:  # 遍历输入字典的每个键
        dict_list = input_dict[key]
        for d in dict_list:  # 遍历列表中的每个字典
            data = to_immutable(d.data)
            result[data] = result.get(data, 0) + d.sup

    # 使用字典推导式过滤值大于等于fminsup的项
    return {k: v for k, v in result.items() if v >= fminsup}

def extract_unique_sublists(dict_data):
    # 用于存储唯一子列表的集合（使用元组形式）
    unique_tuples = set()

    # 遍历字典的所有值
    for value in dict_data.values():
        # print(len(value))
        # 遍历每个值中的子列表
        for sublist in value:
            # 递归将嵌套列表转换为元组，使其可哈希
            def list_to_tuple(lst):
                return tuple(list_to_tuple(item) if isinstance(item, list) else item for item in lst)

            # 将子列表转换为元组并添加到集合（自动去重）
            unique_tuples.add(list_to_tuple(sublist.data))

    # 将集合中的元组转换回列表并返回
    return unique_tuples

def flatten_groups(activity_chart_r, timestamp_list_r, split_points):
    """
    将数据按分割点分组并展平每个分组内的子列表

    :param activity_chart_r: 活动图表数据列表
    :param timestamp_list_r: 时间戳数据列表
    :param split_points: 分割点列表，如 [0, 70, 140, 200]
    :return: 展平后的活动图表分组列表，展平后的时间戳分组列表
    """
    flattened_list_c = []
    flattened_list_t = []

    # 确保分割点列表有效
    if not split_points or len(split_points) < 2:
        raise ValueError("分割点列表至少需要2个值")

    # 遍历分割点区间
    for i in range(len(split_points) - 1):
        start = split_points[i]
        end = split_points[i + 1]

        # 处理活动图表数据
        group_c = activity_chart_r[start:end]
        flat_group_c = [item for sublist in group_c for item in sublist]
        flattened_list_c.append(flat_group_c)

        # 处理时间戳数据
        group_t = timestamp_list_r[start:end]
        flat_group_t = [item for sublist in group_t for item in sublist]
        flattened_list_t.append(flat_group_t)

    return flattened_list_c, flattened_list_t

def flatten_log_groups(log_data, split_points):
    """
    将日志数据按分割点分组并展平每个分组内的子列表

    :param log_data: 包含嵌套列表的日志数据
    :param split_points: 分割点列表，如 [0, 120, 240, 360]
    :return: 展平后的分组列表
    """
    if not split_points or len(split_points) < 2:
        raise ValueError("分割点列表至少需要2个值")

    flattened_list = []

    # 遍历分割点区间
    for i in range(len(split_points) - 1):
        start = split_points[i]
        end = split_points[i + 1]

        # 获取当前分组的切片
        group = log_data[start:end]

        # 展平嵌套列表
        flat_group = [item for sublist in group for item in sublist]

        # 添加到结果列表
        flattened_list.append(flat_group)

    return flattened_list

'''读取数据'''
def mainfun():
    # candinum = []  # 候选模式不同长度起始位置

    # xes数据集
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPIC15_1.xes')
    # flattened_list_c, flattened_list_t = flatten_groups(activity_chart_r, timestamp_list_r, [0, 35, 70, 105, 140, 170, 200])
    # clients = {1: [0, 2], 2: [2, 4], 3: [4, 6]}
    activity_chart_r, timestamp_list_r = read_xes('../data/BPIC15_2.xes')
    flattened_list_c, flattened_list_t = flatten_groups(activity_chart_r, timestamp_list_r, [0, 50, 100, 150, 200, 250, 300])
    clients = {1: [0, 2], 2: [2, 4], 3: [4, 6]}
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPIC15_3.xes')
    # flattened_list_c, flattened_list_t = flatten_groups(activity_chart_r, timestamp_list_r, [0, 50, 100, 150, 200, 225, 250, 280, 300])
    # clients = {1: [0, 3], 2: [3, 5], 3: [5, 8]}
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPIC15_4.xes')
    # flattened_list_c, flattened_list_t = flatten_groups(activity_chart_r, timestamp_list_r,
    #                                                     [0, 50, 100, 150, 200, 225, 250, 300])
    # clients = {1: [0, 2], 2: [2, 4], 3: [4, 7]}
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPIC15_5.xes')
    # flattened_list_c, flattened_list_t = flatten_groups(activity_chart_r, timestamp_list_r,
    #                                                     [0, 50, 100, 150, 200, 225, 250, 300])
    # clients = {1: [0, 2], 2: [2, 4], 3: [4, 7]}
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPI_Challenge_2019.xes')
    # flattened_list_c, flattened_list_t = flatten_groups(activity_chart_r, timestamp_list_r,
    #                                                     [0, 15, 20,  50, 100, 120, 165, 250, 420, 600])
    # clients = {1: [0, 3], 2: [3, 6], 3: [6, 9]}
    # Elog7
    # log_data = read_file("../data/Elog7.txt")
    # flattened_list = flatten_log_groups(log_data, [0, 25, 30, 38])
    # clients = {1: [0, 1], 2: [1, 2], 3: [2, 3]}
    # Elog8
    # log_data = read_file("../data/Elog8.txt")
    # flattened_list = flatten_log_groups(log_data, [0, 120, 240, 361])
    # clients = {1: [0, 1], 2: [1, 2], 3: [2, 3]}

    # log_data = read_file("../data/SDB8.txt")
    # activity_chart_r, timestamp_list_r = compose_timestamp(log_data)
    # 专为扩展性实验准备
    # seqs, timestamp_s = compose_timestamp_scalability(flattened_list)

    # activity_chart_r, timestamp_list_r = compose_timestamp_scalability(log_data)
    # print(activity_chart)
    # print(len(timestamp_list))
    seqs, timestamp_s = con_seqs(flattened_list_c, flattened_list_t)

    clients_FPItem = {}
    clients_candi = {}
    clientsSup = {}
    starttime = time.time()
    #
    # 客户端 1
    c1_result = count_inner_elements(seqs[clients.get(1)[0]:clients.get(1)[1]])
    c1_FPItem, c1_candi, c1_Lminsup = client_episodes(seqs[clients.get(1)[0]:clients.get(1)[1]],
                                                       timestamp_s[clients.get(1)[0]:clients.get(1)[1]], c1_result)
    clients_FPItem[1] = c1_FPItem
    clients_candi[1] = c1_candi
    clientsSup[1] = c1_Lminsup
    # 客户端 2
    c2_result = count_inner_elements(seqs[clients.get(2)[0]:clients.get(2)[1]])
    c2_FPItem, c2_candi, c2_Lminsup = client_episodes(seqs[clients.get(2)[0]:clients.get(2)[1]],
                                                       timestamp_s[clients.get(2)[0]:clients.get(2)[1]], c2_result)
    clients_FPItem[2] = c2_FPItem
    clients_candi[2] = c2_candi
    clientsSup[2] = c2_Lminsup
    # 客户端 3
    c3_result = count_inner_elements(seqs[clients.get(3)[0]:clients.get(3)[1]])
    c3_FPItem, c3_candi, c3_Lminsup = client_episodes(seqs[clients.get(3)[0]:clients.get(3)[1]],
                                                       timestamp_s[clients.get(3)[0]:clients.get(3)[1]], c3_result)
    clients_FPItem[3] = c3_FPItem
    clients_candi[3] = c3_candi
    clientsSup[3] = c3_Lminsup

    fminsup = (c1_result + c2_result + c3_result) * fsup
    # print(fminsup)
    # 服务器合并客户端结果
    FPItem = merge_dicts_backward(clients_FPItem, fminsup, [1, 2, 3], seqs, timestamp_s, clients, clientsSup)
    # FPItem = merge_dicts(clients_FPItem, fminsup)
    candi = extract_unique_sublists(clients_candi)

    endtime = time.time()
    print("运行时间:", endtime - starttime)
    print("频繁模式结果集：", len(FPItem))
    print("候选模式集：", len(candi))

    # for k, v in FPItem.items():
    #     print(str(k) + ":" + str(v))

if __name__ == '__main__':
    maxusage = memory_usage(mainfun, max_usage=True)
    print(maxusage, "Mb")

