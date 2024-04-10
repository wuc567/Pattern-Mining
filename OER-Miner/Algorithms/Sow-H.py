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
        self.len = len(dataitems)
        self.flag = []
        i = 1
        for i in range(self.len):
            self.flag.append(0)
        self.use = 0

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
'''序列'''
# seqs = []

# 最大时间间隔
maxtime = 7200


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

# 项集序列中某个字符是否被使用
def isinuse(s, p):
    i = 0
    while i < len(p):
        idx = s.data.index(p[i])
        if s.flag[idx] == 1:
            return True
        i += 1
    return False

'''获取候选模式前后缀（深拷贝）'''
def preandsuf(p):
    if len(p.data) != 1:
        tp = copy.deepcopy(p.data)
        p.prefix = copy.deepcopy(p.data[0:-1])
        p.suffer = copy.deepcopy(p.data[1:])
        tp[0].pop(0)
        if len(tp[0]) != 0:
            p.suffer.insert(0, tp[0])
        tp[-1].pop(-1)
        if len(tp[-1]) != 0:
            p.prefix.append(tp[-1])
    else:
        p.prefix.append(copy.deepcopy(p.data[0][0:-1]))
        p.suffer.append(copy.deepcopy(p.data[0][1:]))

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
                k += 1
            j += 1
        i += 1

    '''将频繁模式顺序排放，放入候选集合和频繁集合'''
    candione = dict(sorted(candiones.items(), key=lambda x: x[1]))

    for key in sorted(candione.keys()):
        # print(key, candione.get(key))
        if candione.get(key) >= minsup:
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

'''1项集变成2项集'''
def one_to_two():
    i = 0
    while i < len(FP):
        tp = copy.deepcopy(FP[i].data)
        j = 0
        while j < len(FP):
            ad = copy.deepcopy(FP[j].data)
            tmp = []
            # if i < j:
            #     tmp.append(tp + ad)
            #     candi.append(Candilist(tmp))
            #     print(tmp)
            #     tmp = []
            tmp.append(tp)
            tmp.append(ad)
            candi.append(Candilist(tmp))
            j += 1
        i += 1

'''S/I连接生成候选模式,需要先求一下FP中模式的前后缀'''
def sorilink():
    i = 0  # 开始位置需要设置
    while i < len(FP):
        preandsuf(FP[i])
        i += 1
    for i in range(len(FP)):
        for j in range(len(FP)):
            if operator.eq(FP[i].prefix, FP[j].suffer):
                tmp = copy.deepcopy(FP[j].data)
                if len(FP[i].data[-1]) == 1:  # S扩展
                    tmp.append(FP[i].data[-1])
                else:                       # I扩展(不执行)
                    tmp[-1].append(FP[i].data[-1][-1])
                candi.append(Candilist(tmp))
    FP.clear()  # 每次生成完候选模式清空频繁项集

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

'''
    输入为项集，如果项集中每一个元素都被使用，则返回true
'''
def isuseall(item):
    i = 0
    while i < item.len:
        if item.flag[i] == 0:
            return False
        i += 1
    return True

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
    if isuseall(s):
        s.use = 1

'''将序列标记归零use和flag'''
def useto0(seqs):
    i = 0
    while i < len(seqs):
        j = 0
        while j < len(seqs[i]):
            seqs[i][j].use = 0
            k = 0
            while k < seqs[i][j].len:
                seqs[i][j].flag[k] = 0
                k += 1
            j += 1
        i += 1

'''one scan算法'''
def one_scan(timestamp_list, n, s, p):
    # lastpos = 0
    pos = []
    first = 0
    while 1:
        sup = p.sup
        i = 0
        j = 0
        while i < len(s):
            if s[i].use == 0:  # 未被使用
                if isinitem(s[i], p.data[j]) and not isinuse(s[i], p.data[j]):  # 匹配且未被使用
                    if j == 0:
                        first = i
                    if j != 0 and not time_ok(timestamp_list, n, pos[-1], i):
                        i = pos[-1] + 1
                        j = j - 1
                        pos.pop()
                        continue
                    # lastpos = i
                    pos.append(i)
                    j += 1
                if j >= len(p.data):
                    k = 0
                    while k < len(p.data):
                        labflag(s[pos[k]], p.data[k])
                        k += 1
                    # if p.data == [['DeskWork'], ['Eating/Drinking']]:
                    #     print(pos)
                    pos.clear()
                    j = 0
                    i = first
                    p.sup += 1
            i += 1
        # if sup == p.sup:
        #     break
        if i >= len(s):
            break

'''读取数据'''
def mainfun():
    candinum = []  # 候选模式不同长度起始位置
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
    onepattern(seqs)  # 1序列模式及位置索引
    candinum.append(len(candi))
    one_to_two()  # 从FP中生成存到candi
    candinum.append(len(candi))
    FP.clear()
    while 1:
        cannum = candinum.pop(0)
        i = cannum
        while i < len(candi):
            j = 0
            while j < len(seqs):
                one_scan(timestamp_s, j, seqs[j], candi[i])
                # print(candi[i].data, candi[i].sup)
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
    print("运行时间:", endtime - starttime)
    print("频繁模式结果集：", len(FPItem))
    print("候选模式集：", len(candi))

    # i = 0
    # while i < len(FPItem):
    #     print(str(FPItem[i].data) + ":" + str(FPItem[i].sup))
    #     i += 1



if __name__ == '__main__':
    maxusage = memory_usage(mainfun, max_usage=True)
    print(maxusage, "Mb")

