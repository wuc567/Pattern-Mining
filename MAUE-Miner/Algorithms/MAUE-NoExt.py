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
import numpy as np


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
# performance of EMI-Miner
# s1 BPI_Challenge_2019.xes range(2000)-22035
# mineau = 5000
# maxtime = 3024000  # (5 week)
# s2 Road_Traffic_Fine_Management_Process.xes range(2000)-8947
# mineau = 80
# maxtime = 15120000  # (5 week)
# s2 BPIC15_5.xes range(300)-13782
# mineau = 1600
# maxtime = 3024000
mineau = 1500
maxtime = 10800  # (3 hour)
# s3 BPIC15_4.xes range(300)-12282
# minsup = 250
# maxtime = 3024000
# mineau = 2700
# maxtime = 10800  # (3 hour)
# s4 BPIC15_1.xes range(200)-7710
# minsup = 134
# maxtime = 3024000  # (5 week)
# mineau = 2700
# maxtime = 10800  # (3 hour)
# s5 BPIC15_2.xes range(300)-14588
# minsup = 230
# maxtime = 3024000  # (5 week)
# mineau = 3200
# maxtime = 10800  # (3 hour)
# s6 BPIC15_3.xes range(300)-11524
# minsup = 250
# maxtime = 3024000
# mineau = 1200
# maxtime = 10800  # (3 hour)
# s7 SDB7-2664
# mineau = 1500
# maxtime = 10800  # (3 hour)
# s8 SDB8-6996
# mineau = 3000
# maxtime = 10800  # (3 hour)

# different minsup
# minsup = 10

# Scalability
# minsup = 200
# time_scale = 1
# minconf = 0.35
# FERule = []
# SERule = []
'''各序列的Next数组集合'''
Nextlist = []
'''存放Next数组结构,用于支持度计算(字典)每条序列的'''
Next = {}
# 频繁情节：支持度
# FEDict = {}
# case study
# caserule = []
# 模型地址
# modelDict = {}
# strongDict = {}

def con_seqs(activity_chart, timestamp_list):
    seqs = []
    timestamp_s = []
    # 1.合并多序列
    # seq = []
    # tempitem = []
    # for i in range(len(activity_chart)):
    #     tempitem.append(activity_chart[i])
    #     item = Item(copy.deepcopy(tempitem))
    #     seq.append(item)
    #     tempitem.clear()
    # seqs.append(seq)
    # timestamp_s.append(timestamp_list)
    # 2. 多序列
    for act_s in activity_chart:
        seq = []
        for strs in act_s:
            tempitem = []
            tempitem.append(strs)
            item = Item(copy.deepcopy(tempitem))
            seq.append(item)
            tempitem.clear()
        seqs.append(seq)
    timestamp_s.extend(timestamp_list)
    return seqs, timestamp_s

def con_seqs2(activity_chart, timestamp_list):
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
                                trace_day[day_identity] = [copy.deepcopy(activity_list), copy.deepcopy(timestamp_list)]
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
    # for vals in trace_per.values():
    #     for svals in vals.values():
    #         activity_chart.extend(svals[0])
    #         timestamp_list.extend(svals[1])
    # 2. 以轨迹为序列，一个日志多个轨迹，即多条序列
    for vals in trace_per.values():
        for svals in vals.values():
            activity_chart.append(svals[0])
            timestamp_list.append(svals[1])
    return activity_chart, timestamp_list

'''
    读取xes文件
'''
def read_xes(file_address, addr):
    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    event_log = xes_importer.apply(file_address,  # 引号中的为文件地址
                                   variant=variant, parameters=parameters)
    uti = read_file(addr)
    u_list = list(map(lambda x: list(x), uti))
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    utility_list = []  # 效用
    # 1. 合并为单序列
    # for t in range(0, 2000):
    #     for e in event_log[t]:
    #         activity_chart.append(e["concept:name"])
    #         timestamp_list.append(e['time:timestamp'])
    # 2. 以轨迹为序列，一个日志多个轨迹，即多条序列
    for t in range(2000):
        activity_e = []
        timestamp_t = []
        utility_u = []
        for k in range(len(event_log[t])):
            activity_e.append(event_log[t][k]["concept:name"])
            timestamp_t.append(event_log[t][k]['time:timestamp'])
            utility_u.append(u_list[t][k])

        activity_chart.append(copy.deepcopy(activity_e))
        timestamp_list.append(copy.deepcopy(timestamp_t))
        utility_list.append(copy.deepcopy(utility_u))
    return activity_chart, timestamp_list, utility_list

# 读取TXT文件
def read_file(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    # map作用于每个可迭代对象的元素，并返回处理之后的元素;filter作用于可迭代内每个元素，根据计算后结果：True保留，Flase去掉
    # 去除首尾空格
    temp = list(filter(lambda x: x.strip() and x != 'NA\n', lines))
    # 去除\n
    return list(map(lambda x: x.strip('\n'), temp))

# 随机生成效用值
def write_txt(addr, len_line):
    base_u = []
    for siz in len_line:
        base_u.append(np.random.randint(1, 10, size=siz))
    with open(addr, 'w') as f:
        f.writelines([''.join(map(str, row)) + '\n' for row in base_u])

# 合成事件序列
def compose_timestamp(log_data, addr):
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    utility_list = []  # 效用
    uti = read_file(addr)
    u_list = list(map(lambda x: list(x), uti))
    for k in range(len(log_data)):
        date_time1 = parser.parse("2015-03-16 11:32:29")
        for t in range(len(log_data[k])):
            date_time1 = date_time1 + timedelta(minutes=10)
            activity_chart.append(log_data[k][t])
            timestamp_list.append(date_time1)
            utility_list.append(u_list[k][t])
    return activity_chart, timestamp_list, utility_list

def compose_timestamp_scalability(log_data):
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    for k in range(len(log_data)):
        date_time1 = parser.parse("2015-03-16 11:32:29")
        activity_chart_e = []
        timestamp_list_e = []
        for t in range(len(log_data[k])):
            date_time1 = date_time1 + timedelta(minutes=10)
            activity_chart_e.append(log_data[k][t])
            timestamp_list_e.append(date_time1)
        activity_chart.append(activity_chart_e)
        timestamp_list.append(timestamp_list_e)
    return activity_chart, timestamp_list

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

'''构造五元组形式'''
def reconstruction_database(utility_list):
    res = []
    rmu = []
    neu = []  # 新效用值（int）
    for subl in utility_list:
        max_u = 0
        subl.reverse()
        res_sub = []
        rmu_sub = []
        neu_sub = []
        for i in range(len(subl)):
            neu_sub.append(int(subl[i]))
            res_sub.append(i)
            rmu_sub.append(max_u)
            max_u = max(max_u, int(subl[i]))
        res.append(list(reversed(res_sub)))
        rmu.append(list(reversed(rmu_sub)))
        neu.append(list(reversed(neu_sub)))
    return neu, res, rmu

'''
   遍历序列，生成1长度候选模式,并且将频繁模式放入候选集合和频繁集合
   给每条序列创建一个Next数组，且只保存频繁项集的Next数组
'''
def onepattern(seqs, neu, res, rmu):
    candiones = {}
    i = 0
    while i < len(seqs):  # 序列库
        j = 0
        while j < len(seqs[i]):  # 序列
            k = 0
            while k < len(seqs[i][j].data):  # 项集
                # 统计单项的支持度
                epu = neu[i][j]
                tm_rmu = rmu[i][j]
                ruebound = 0
                if epu >= tm_rmu:
                    ruebound += (epu + tm_rmu) / 2
                else:
                    ruebound += (epu + tm_rmu * res[i][j]) / (1 + res[i][j])

                if seqs[i][j].data[k] not in candiones.keys():
                    candiones[seqs[i][j].data[k]] = [epu, ruebound]
                    candi.append(Candilist([seqs[i][j].data[k]]))
                else:
                    candiones[seqs[i][j].data[k]][0] = candiones.get(seqs[i][j].data[k])[0] + epu
                    candiones[seqs[i][j].data[k]][1] = candiones.get(seqs[i][j].data[k])[1] + ruebound

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
        if candione.get(key)[0] >= mineau:
            temp = Candilist(key.split(","))
            # temp.sup = candione.get(key)
            FPItem.append(temp)
        # if candione.get(key)[1] < mineau:
        #     i = 0
        #     while i < len(Nextlist):
        #         if key in Nextlist[i].keys():
        #             del Nextlist[i][key]
        #         i += 1
        #     candione.pop(key)
        if candione.get(key)[1] >= mineau:
            temp = Candilist(key.split(","))
            # temp.sup = candione.get(key)
            FP.append(temp)
    '''数字型字符串使用
    sort_item = sortitem(candione.keys())'''
    '''字符型数据使用'''
    sort_item = list(candione.keys())
    sort_item.sort()
    # i = 0
    # while i < len(sort_item):
    #     temp = Candilist([str(sort_item[i])])
    #     # temp.sup = candione.get(str(sort_item[i]))
    #     FP.append(temp)
    #     i += 1
    return sort_item

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

'''S/I连接生成候选模式'''
def sandilinked(sort_item):
    # print(len(FP))
    i = 0
    while i < len(FP):
        j = 0
        while j < len(sort_item):
            if len(FP[i].data) == 1 and type(FP[i].data[0]) == str:
                temp = [copy.deepcopy(FP[i].data)]  # s-连接
            else:
                temp = copy.deepcopy(FP[i].data)  # 不执行
            temp.append([sort_item[j]])
            candi.append(Candilist(temp))
            j += 1
        i += 1

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

'''求平均效用和上界效用'''
def average_utility(neu, res, rmu, ooc_dict, p):
    epu = 0
    ruebound = 0
    for k, v in ooc_dict.items():
        for adl in v:
            tm_au = 0
            for ad in adl:
                # au
                epu += neu[k][ad]
                # bound
                tm_au += neu[k][ad]
            tm_rmu = rmu[k][adl[-1]]
            if tm_au/len(p.data) >= tm_rmu:
                ruebound += (tm_au + tm_rmu)/(len(p.data)+1)
            else:
                ruebound += (tm_au + tm_rmu * res[k][adl[-1]])/(len(p.data)+res[k][adl[-1]])
    eau = epu/len(p.data)
    return eau, ruebound

'''
    计算支持度算法
    参数：序列，第几个序列，模式
'''
def newsup(timestamp_list, n, p):
    # 仅用于模型生成
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
        j = 0
        while j < len(p.data[i]):
            if p.data[i][j] in Nextlist[n].keys():
                temp = copy.deepcopy(Nextlist[n].get(p.data[i][j]))
                temp.insert(0, 1)  # 插入0为指针位置，表示该项next所在位置
                que.append(temp)
            else:
                return addlist
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
                addlist.append(copy.deepcopy(usearray))
                usearray.clear()
            if i == 0:
                MaxIndex = max
            count += 1
            i += 1
        count = 0
    return addlist

'''读取数据'''

def mainfun():
    candinum = []  # 候选模式不同长度起始位置
    # 数据集1 csv文件
    # trace_per = read_csv("../data/daily living/")
    # activity_chart_r, timestamp_list_r = data_preprocess(trace_per)

    # xes数据集
    # activity_chart_r, timestamp_list_r, utility_list = read_xes('../dataset/BPI_Challenge_2019.xes',
    #                                                             '../dataset/BPI_Challenge_2019_NoExt.txt')
    # activity_chart_r, timestamp_list_r, utility_list = read_xes('../dataset/Road_Traffic_Fine_Management_Process.xes',
    #                                                             '../dataset/Road_Traffic_Fine_Management_Process_NoExt.txt')
    # activity_chart_r, timestamp_list_r = read_xes('../dataset/BPIC15_1.xes')
    # activity_chart_r, timestamp_list_r = read_xes('../dataset/BPIC15_2.xes')
    # activity_chart_r, timestamp_list_r = read_xes('../dataset/BPIC15_3.xes')
    # activity_chart_r, timestamp_list_r = read_xes('../dataset/BPIC15_4.xes')
    # activity_chart_r, timestamp_list_r, utility_list = read_xes('../dataset/BPIC15_5.xes', '../dataset/BPIC15_5_NoExt.txt')
    log_data = read_file("../dataset/SDB2.txt")
    # log_data = read_file("../dataset/SDB3.txt")
    # log_data = read_file("../dataset/SDB4.txt")
    # log_data = read_file("../dataset/SDB5.txt")
    # log_data = read_file("../dataset/SDB6.txt")
    # log_data = read_file("../dataset/SDB7.txt")
    # log_data = read_file("../dataset/SDB8.txt")
    # 专为NoExt准备
    activity_chart_r, timestamp_list_r, utility_li = compose_timestamp(log_data, "../dataset/SDB2_NoExt.txt")
    # activity_chart_r, timestamp_list_r, utility_li = compose_timestamp(log_data, "../dataset/SDB3_NoExt.txt")
    # activity_chart_r, timestamp_list_r, utility_li = compose_timestamp(log_data, "../dataset/SDB4_NoExt.txt")
    # activity_chart_r, timestamp_list_r, utility_li = compose_timestamp(log_data, "../dataset/SDB5_NoExt.txt")
    # activity_chart_r, timestamp_list_r, utility_li = compose_timestamp(log_data, "../dataset/SDB6_NoExt.txt")
    # activity_chart_r, timestamp_list_r, utility_li = compose_timestamp(log_data, "../dataset/SDB7_NoExt.txt")
    # activity_chart_r, timestamp_list_r, utility_li = compose_timestamp(log_data, "../dataset/SDB8_NoExt.txt")
    utility_list = [utility_li]
    # 专为扩展性实验准备
    # activity_chart_r, timestamp_list_r = compose_timestamp_scalability(log_data)
    # print(len(activity_chart_r))
    # print(len(timestamp_list_r))

    # seqs, timestamp_s = con_seqs(activity_chart_r, timestamp_list_r)
    seqs, timestamp_s = con_seqs2(activity_chart_r, timestamp_list_r)
    # print(len(seqs))
    # print(len(timestamp_s))
    # 生成效用文件
    # len_line = [len(sublist) for sublist in timestamp_s]
    # print(len(len_line), len_line)
    # write_txt('../dataset/SDB6_NoExt.txt', len_line)
    # 读取效用文件
    neu, res, rmu = reconstruction_database(utility_list)
    # print(len(neu), len(res), len(rmu))

    starttime = time.time()
    # onepattern(seqs)  # 1序列模式及位置索引
    sort_item = onepattern(seqs, neu, res, rmu)  # 1序列模式及位置索引,0->1
    sort_item = list(map(str, sort_item))
    # print(sort_item)
    candinum.append(len(candi))
    # one_to_two()  # 从FP中生成存到candi
    sandilinked(sort_item)  # 1->2
    candinum.append(len(candi))
    FP.clear()
    while 1:
        cannum = candinum.pop(0)
        i = cannum
        while i < len(candi):
            ooc_dict = dict()
            j = 0
            while j < len(seqs):
                addlist = newsup(timestamp_s, j, candi[i])
                ooc_dict[j] = addlist
                j += 1
            # 计算平均效用(EAU)和效用上限（RUEbound）
            eau, ruebound = average_utility(neu, res, rmu, ooc_dict, candi[i])
            if eau >= mineau:
                FPItem.append(candi[i])
            if ruebound >= mineau:
                FP.append(candi[i])
            i += 1

        sandilinked(sort_item)
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

