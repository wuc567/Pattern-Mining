from pm4py.objects.log.importer.xes import importer as xes_importer
from memory_profiler import memory_usage
from dateutil import parser
from datetime import timedelta
import operator
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

'''候选模式结构'''
class Candilist():
    def __init__(self, dataitems):
        self.data = dataitems
        self.sup = 0
        self.prefix = []
        self.suffer = []

'''候选模式列表（字典）'''
candione = {}
'''候选模式集合（列表）'''
candi = []
'''频繁模式集合'''
FPItem = []
'''频繁模式过渡集合'''
FP = []
'''最小支持度'''
# s1 daily living
# minsup = 20
# s2 Road_Traffic_Fine_Management_Process.xes range(2000)-8947
# minsup = 100
# s3 BPIC15_1.xes range(200)-7710
# minsup = 134
# s4 BPIC15_2.xes range(300)-14588
# minsup = 200
# s5 BPIC15_3.xes range(300)-11524
# minsup = 230
# s6 BPI_Challenge_2019.xes range(2000)-22035
# minsup = 903
# s7 SDB7-2664
minsup = 170
# s8 SDB8-6996
# minsup = 310

# different minsup
# minsup = 35

# Scalability
# minsup = 289
# time_scale = 1
# minsup = 578
# time_scale = 2
# minsup = 867
# time_scale = 3
# minsup = 1156
# time_scale = 4
# minsup = 1445
# time_scale = 5
# minsup = 1734
# time_scale = 6
# minsup = 2023
# time_scale = 7
# minsup = 2312
# time_scale = 8
'''各序列的Next数组集合'''
Nextlist = []
'''存放Next数组结构,用于支持度计算(字典)每条序列的'''
Next = {}
# 最大时间间隔
maxtime = 7200
sort_item = []
FPnum = []


def con_seqs(activity_chart, timestamp_list):
    seqs = []
    timestamp_s = []
    # 1.合并多序列
    seq = []
    tempitem = []
    for i in range(len(activity_chart)):
        tempitem.append(activity_chart[i])
        item = Item(copy.deepcopy(tempitem))
        seq.append(item)
        tempitem.clear()
    seqs.append(seq)
    timestamp_s.append(timestamp_list)
    # 2. 多序列
    # for act_s in activity_chart:
    #     seq = []
    #     for strs in act_s:
    #         tempitem = []
    #         tempitem.append(strs)
    #         item = Item(copy.deepcopy(tempitem))
    #         seq.append(item)
    #         tempitem.clear()
    #     seqs.append(seq)
    # timestamp_s.extend(timestamp_list)
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
    for t in range(2000):
        for e in event_log[t]:
            activity_chart.append(e["concept:name"])
            timestamp_list.append(e['time:timestamp'])
    # 2. 以轨迹为序列，一个日志多个轨迹，即多条序列
    # for t in range(300):
    #     activity_e = []
    #     timestamp_t = []
    #     for e in event_log[t]:
    #         activity_e.append(e["concept:name"])
    #         timestamp_t.append(e['time:timestamp'])
    #     activity_chart.append(activity_e)
    #     timestamp_list.append(timestamp_t)
    return activity_chart, timestamp_list

# 读取TXT文件
def read_file(file_path):
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
def onepattern(seqs):
    candiones = {}
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
        if candione.get(key) >= minsup:
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
        i += 1
    return sort_item


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

def isincandi(list):
    i = 0
    while i < len(FPItem):
        if operator.eq(FPItem[i].data, list):
            return True
        i += 1
    return False

'''s连接'''
def sbacktracking(seqs, timestamp_list, fp, sort_item):
    if fp.sup == 0:
        j = 0
        while j < len(seqs):
            newsup(timestamp_list, j, fp)
            j += 1
    if fp.sup < minsup:
        return
    elif not (len(fp.data) == 1 and type(fp.data[0]) == str):
        if not isincandi(fp.data):
            FPItem.append(fp)
    i = 0
    while i < len(sort_item):
        if len(fp.data) == 1 and type(fp.data[0]) == str:
            temp = [copy.deepcopy(fp.data)]  # s-连接
        else:
            temp = copy.deepcopy(fp.data)
        temp.append([sort_item[i]])
        tmp = Candilist(temp)
        candi.append(tmp)
        sbacktracking(seqs, timestamp_list, tmp, sort_item)
        i += 1

'''深度优先生成候选模式 DFjion+isincan+DFjionin'''
def DFjoin(seqs, timestamp_list, sort_item):
    FPnum.append(len(FPItem))
    while len(FPnum) != 0:
        i = 0
        while i < len(FP):
            sbacktracking(seqs, timestamp_list, FP[i], sort_item)
            i += 1
        FPnum.append(len(FPItem))
        FP.clear()
        i = FPnum.pop(0)
        if i == len(FPItem):
            break
        while i < len(FPItem):
            FP.append(FPItem[i])
            i += 1

'''
    计算支持度算法
    参数：序列，第几个序列，模式
'''
def newsup(timestamp_list, n, p):
    flag = 0
    que = []  # 存放Next数组
    count = 0  # 记存储Next顺序
    MaxIndex = -1
    useflag = {}  # 使用过的位置存放进来，保证多项集的一次性条件
    usearray = []
    i = 0
    # 根据模式构建Next数组结构
    while i < len(p.data):
        j = 0
        while j < len(p.data[i]):
            if p.data[i][j] in Nextlist[n].keys():
                temp = copy.deepcopy(Nextlist[n].get(p.data[i][j]))
                temp.insert(0, 1)  # 插入0为指针位置，表示该项next所在位置
                que.append(temp)
            else:
                return
            j += 1
        i += 1

    while flag == 0:
        i = 0
        max = MaxIndex
        while i < len(p.data):
            # 第一个位置就要大于上一个元素的索引，如果不满足则指针后移
            while que[count][0] < len(que[count]) and que[count][que[count][0]] <= max:
                que[count][0] += 1
            if p.data[i][0] in useflag.keys():
                temp = useflag.get(p.data[i][0])  # 该项已使用位置列表
                while que[count][0] < len(que[count]) and temp.count(que[count][que[count][0]]):  # count()方法返回列表中某个元素的出现次数
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
                # if len(p.data) == 3:
                #     print(p.data, usearray)
                usearray.clear()
            if i == 0:
                MaxIndex = max
            count += 1
            i += 1
        count = 0

'''读取数据'''
def mainfun():
    # trace_per = read_csv("../data/daily living/")
    # activity_chart_r, timestamp_list_r = data_preprocess(trace_per)
    # xes数据集
    # activity_chart_r, timestamp_list_r = read_xes('../data/Road_Traffic_Fine_Management_Process.xes')
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPIC15_1.xes')
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPIC15_2.xes')
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPIC15_3.xes')
    # activity_chart_r, timestamp_list_r = read_xes('../data/BPI_Challenge_2019.xes')
    log_data = read_file("../data/SDB7.txt")
    # log_data = read_file("../data/SDB8.txt")
    activity_chart_r, timestamp_list_r = compose_timestamp(log_data)
    # 专为扩展性实验准备
    # activity_chart_r, timestamp_list_r = compose_timestamp_scalability(log_data)
    # print(activity_chart)
    # print(len(timestamp_list))
    seqs, timestamp_s = con_seqs(activity_chart_r, timestamp_list_r)
    starttime = time.time()
    sort_item = onepattern(seqs)  # 1序列模式及位置索引, 0->1
    sort_item = list(map(str, sort_item))
    DFjoin(seqs, timestamp_s, sort_item)
    endtime = time.time()
    print("运行时间:", endtime - starttime)
    print("频繁模式结果集：", len(FPItem))
    print("候选模式集：", len(candi))

    # i = 0
    # while i < len(FPItem):
    #     print(FPItem[i].data, FPItem[i].sup)
    #     i += 1


if __name__ == '__main__':
    maxusage = memory_usage(mainfun, max_usage=True)
    print(maxusage, "Mb")

