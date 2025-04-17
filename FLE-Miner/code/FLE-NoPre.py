from pm4py.objects.log.importer.xes import importer as xes_importer
from memory_profiler import memory_usage
from dateutil import parser
from datetime import timedelta
from collections import defaultdict
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
# 客户端位置索引
clientNext = {}

'''最小支持度'''
# performance of EMI-Miner
# ELog1 BPI_Challenge_2019.xes range(2000)-22035
# maxeac = 7
# maxtime = 3024000  # (5 week)
# mincor = 0.42

# ELog2 BPIC15_1.xes range(200)-7710
# maxeac = 5
# maxtime = 3024000  # (5 week)
# mincor = 0.90

# ELog3 BPIC15_2.xes range(300)-14588
# maxeac = 5
# maxtime = 3024000  # (5 week)
# mincor = 0.90

# ELog4 BPIC15_3.xes range(300)-11524
# maxeac = 5
# maxtime = 3024000  # (5 week)
# mincor = 0.90

# ELog5 BPIC15_4.xes range(300)-12282
# maxeac = 5
# maxtime = 3024000  # (5 week)
# mincor = 0.90

# ELog6 BPIC15_5.xes range(300)-13782
# maxeac = 6
# maxtime = 3024000
# mincor = 0.85

# ELog7 SDB2
# maxeac = 11.9
# maxtime = 10800  # (3 hour)
# mincor = 0.42

# ELog8 SDB3
maxeac = 12
maxtime = 10800  # (3 hour)
mincor = 0.42


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
    for t in range(300):
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
        base_u.append(np.random.randint(1, 5, size=siz))
    with open(addr, 'w') as f:
        f.writelines([''.join(map(str, row)) + '\n' for row in base_u])

# 合成事件序列
def compose_timestamp(log_data, addr, cli_data):
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

def compose_timestamp_scalability(log_data, addr):
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    cost_list = []  # 成本
    uti = read_file(addr)
    c_list = list(map(lambda x: list(x), uti))
    for k in range(len(log_data)):
        date_time1 = parser.parse("2015-03-16 11:32:29")
        activity_chart_e = []
        timestamp_list_e = []
        cost_u = []
        for t in range(len(log_data[k])):
            date_time1 = date_time1 + timedelta(minutes=10)
            activity_chart_e.append(log_data[k][t])
            timestamp_list_e.append(date_time1)
            cost_u.append(c_list[k][t])
        activity_chart.append(copy.deepcopy(activity_chart_e))
        timestamp_list.append(copy.deepcopy(timestamp_list_e))
        cost_list.append(copy.deepcopy(cost_u))
    return activity_chart, timestamp_list, cost_list

def compose_timestamp_pre(log_data, addr, cli_data):
    activity_2d = []  # 事件缩写结果集
    timestamp_2d = []  # 时间戳集
    cost_2d = []  # 成本
    uti = read_file(addr)
    c_list = list(map(lambda x: list(x), uti))
    for k in range(len(log_data)):
        date_time1 = parser.parse("2015-03-16 11:32:29")
        activity_chart_e = []
        timestamp_list_e = []
        cost_u = []
        for t in range(len(log_data[k])):
            date_time1 = date_time1 + timedelta(minutes=10)
            activity_chart_e.append(log_data[k][t])
            timestamp_list_e.append(date_time1)
            cost_u.append(c_list[k][t])
        activity_2d.append(copy.deepcopy(activity_chart_e))
        timestamp_2d.append(copy.deepcopy(timestamp_list_e))
        cost_2d.append(copy.deepcopy(cost_u))

    # 按 cli_data 拆分合并的通用函数
    def merge_groups(data_2d, cli_indices):
        merged = []
        start = 0
        for end in cli_indices:
            # 合并从 start 到 end（含）的子列表
            subgroup = []
            for i in range(start, end + 1):
                subgroup.extend(data_2d[i])
            merged.append(subgroup)
            start = end + 1  # 更新下一组的起始位置
        # 处理剩余未分组的子列表（若有）
        if start < len(data_2d):
            subgroup = []
            for i in range(start, len(data_2d)):
                subgroup.extend(data_2d[i])
            merged.append(subgroup)
        return merged

    activity_chart = merge_groups(activity_2d, cli_data)
    timestamp_list = merge_groups(timestamp_2d, cli_data)
    cost_list = merge_groups(cost_2d, cli_data)
    return activity_chart, timestamp_list, cost_list

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

'''构造四元组形式'''
def reconstruction_database(cost_list):
    # res = []
    cle = []
    neu = []  # 新效用值（int）
    # uti = read_file(addr)
    # u_list = list(map(lambda x: list(x), uti))
    for subl in cost_list:
        min_u = 100
        subl.reverse()
        # res_sub = []
        cle_sub = []
        neu_sub = []
        for i in range(len(subl)):
            neu_sub.append(int(subl[i]))
            # res_sub.append(i)
            min_u = min(min_u, int(subl[i]))
            cle_sub.append(min_u)
        # res.append(list(reversed(res_sub)))
        cle.append(list(reversed(cle_sub)))
        neu.append(list(reversed(neu_sub)))
    return neu, cle

'''客户端合并多序列
L1=[{'a':[1,4,6], 'b':[3,7,2], 'd':[2,4,1], 'f':[7,1,2]}, 
{'a':[3,2,1], 'b':[5,2,3], 'c':[3,2,1], 'd':[4,2,2], 'f':[6,3,1]}] 
L2=[{'a':[4,6,1], 'b':[8,9,2], 'c':[3,2,1], 'd':[6,6,1], 'f':[13,4,1]}] 
使用python写段代码，实现从L1转化生成L2
相同键的列表：前两个元素相加，第三个元素取最小值
不同键的列表：直接保留原始内容
'''
def mergerseq(L1):
    new_dict = {}
    # 获取所有可能的键（并集）
    all_keys = set().union(*L1)
    for key in all_keys:
        # 收集所有字典中该键对应的列表（仅当键存在时）
        values = [d[key] for d in L1 if key in d]
        # 合并逻辑：前两个元素求和，第三个取最小值
        merged = [
            sum(v[0] for v in values),  # 第一个元素总和
            sum(v[1] for v in values),  # 第二个元素总和
            min(v[2] for v in values)  # 第三个元素最小值
        ]
        new_dict[key] = merged
    return [new_dict]

'''
C1={'client_1':[{'a':[30,10,3], 'b':[12,6, 3]}],'client_2':[{'a':[14,7,1], 'b':[18,6,2], 'c':[16,2,4]}]} 
C2={'a':[(30/10+14/7)/2, min{3,1}], 'b':[(12/6+18/6)/2,min{3,2}], 'c':[(16/2)/1,min{4}]} 
使用python写段代码，实现从C1转化生成C2，如果元素中键相同则前两个元素相除后对应位置的元素求平均，第三个元素：取两个字典中对应位置的元素的最小值
'''
def avgcost(C1):
    # 收集所有键对应的数据列表
    all_data = defaultdict(list)
    for client in C1.values():
        client_dict = client[0]  # 提取每个客户端的字典
        for key, value in client_dict.items():
            all_data[key].append(value)

    # 构建C2
    C2 = {}
    for key, lists in all_data.items():
        # 计算前两个元素的商并求平均
        quotients = [lst[0] / lst[1] for lst in lists]
        avg_quotient = sum(quotients) / len(quotients)
        # 计算第三个元素的最小值
        min_third = min(lst[2] for lst in lists)
        C2[key] = [round(avg_quotient, 2), min_third]
    return C2

'''
   遍历序列，生成1长度候选模式,并且将频繁模式放入候选集合和频繁集合
   给每条序列创建一个Next数组，且只保存频繁项集的Next数组
'''
def onepattern(seqs, neu, cle, client):
    '''各序列的Next数组集合'''
    Nextlist = []
    '''存放Next数组结构,用于支持度计算(字典)每条序列的'''
    Next = {}
    candiones = {}
    list_candiones = []
    client_candiones = {}
    # {'client_1':[{'a':[cost,support,平均成本下界], 'b':[cost,support,,平均成本下界]},
    # {'a':[cost,support,平均成本下界], 'b':[cost,support,,平均成本下界]}]
    # 'client_2':[{'a':[cost,support,平均成本下界], 'b':[cost,support,,平均成本下界]},
    #     {'a':[cost,support,平均成本下界], 'b':[cost,support,,平均成本下界]}]}
    i = 0
    while i < len(seqs):  # 序列库
        j = 0
        while j < len(seqs[i]):  # 序列
            k = 0
            while k < len(seqs[i][j].data):  # 项集
                # 统计单项的支持度
                epu = neu[i][j]
                # tm_cle = cle[i][j]  # 整个序列该情节的第一个出现

                if seqs[i][j].data[k] not in candiones.keys():
                    candiones[seqs[i][j].data[k]] = [epu, 1, cle[i][j]]
                    # candi.append(Candilist([seqs[i][j].data[k]]))
                else:
                    candiones[seqs[i][j].data[k]][0] = candiones.get(seqs[i][j].data[k])[0] + epu
                    candiones[seqs[i][j].data[k]][1] = candiones.get(seqs[i][j].data[k])[1] + 1

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
        list_candiones.append(copy.deepcopy(candiones))
        candiones.clear()
        # 每个客户端的位置索引
        for n in range(len(client)):
            if client[n] == i:
                clientNext[n] = copy.deepcopy(Nextlist)
                Nextlist.clear()
                client_candiones[n] = copy.deepcopy(list_candiones)
                list_candiones.clear()
        i += 1
    # 求出每个客户端中每个元素的最终成本，支持度和平均成本下界
    # {'client_1':[{'a':[总cost,总support,min 平均成本下界], 'b':[总cost,总support, min 平均成本下界]}]
    # 'client_2':[{'a':[总cost,总support,min 平均成本下界], 'b':[总cost,总support,min 平均成本下界]}]}
    for key in client_candiones:
        # 将一个字典中的值做运算后，还放回该字典
        client_candiones[key] = mergerseq(client_candiones[key])
    '''
    C1 = {'client_1': [{'a': [30, 10, 3], 'b': [12, 6, 3]}],
          'client_2': [{'a': [14, 7, 1], 'b': [18, 6, 2], 'c': [16, 2, 4]}]}
    C2 = {'a': [(30 / 10 + 14 / 7) / 2, min{3, 1}], 'b': [(12 / 6 + 18 / 6) / 2, min{3, 2}],
          'c': [(16 / 2) / 1, min{4}]}'''
    event_cost = avgcost(client_candiones)

    for key in sorted(event_cost.keys()):
        candi.append(Candilist(key))
        if event_cost.get(key)[0] <= maxeac:  # 平均成本小于阈值
            temp = Candilist(key.split(","))
            # temp.sup = candione.get(key)
            FPItem.append(temp)
            FP.append(temp)
        elif event_cost.get(key)[1] <= maxeac:  # 成本下界小于阈值
            temp = Candilist(key.split(","))
            # temp.sup = candione.get(key)
            FP.append(temp)
        else:  #  删除不满足事件的位置索引
            for entries in clientNext.values():
                for entry in entries:
                    # 如果键存在则删除，避免KeyError
                    if key in entry:
                        del entry[key]
    return client_candiones

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
def sandilinked():
    for i in range(len(FP)):
        for j in range(len(FP)):
            if operator.eq(FP[i].prefix, FP[j].suffer):
                tmp = copy.deepcopy(FP[j].data)
                if len(FP[i].data[-1]) == 1:  # S扩展
                    tmp.append(FP[i].data[-1])
                else:  # I扩展(不执行)
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

'''求平均效用和上界效用'''
def average_cost(neu_dict, cle_dict, ooc_client):
    # 计算 cost_avg
    cost_avg_sum = 0.0
    client_count = 0

    for client_id in ooc_client:
        client_seqs = ooc_client[client_id]
        sup_p = sum(len(seq) for seq in client_seqs.values())
        # 如果该客户端不存在出现，则不用统计该客户端数据
        if sup_p == 0:
            continue

        neu_sublists = neu_dict.get(client_id, [])
        # client_total_cost = 0
        # client_total_intervals = 0

        # 按序列名称排序以确保顺序正确
        sorted_seqs = sorted(client_seqs.items(), key=lambda x: x[0])
        for seq_idx, (seq_name, intervals_list) in enumerate(sorted_seqs):
            if seq_idx >= len(neu_sublists):
                continue  # 忽略无对应 neu 数据的序列
            neu_data = neu_sublists[seq_idx]
            for interval in intervals_list:
                # 计算每个区间的 neu 值总和
                sum_neu = 0
                for i in interval:
                    if i < len(neu_data):
                        sum_neu += neu_data[i]
                cost_avg_sum += sum_neu
            client_count += len(intervals_list)

        # if client_count == 0:
        #     client_avg = 0.0
        # else:
        #     client_avg = client_total_cost / client_total_intervals
        # cost_avg_sum += client_avg
        # client_count += 1

    cost_avg = cost_avg_sum / client_count if client_count != 0 else 0.0
    cost_avg = round(cost_avg, 2)  # 保留两位小数

    # 计算 cle_min
    cle_client_values = []
    for client_id in ooc_client:
        client_seqs = ooc_client[client_id]
        sup_p = sum(len(seq) for seq in client_seqs.values())
        # 如果该客户端不存在出现，则不用统计该客户端数据
        if sup_p == 0:
            continue

        cle_sublists = cle_dict.get(client_id, [])
        seq_sums = []

        # 按序列名称排序以确保顺序正确
        sorted_seqs = sorted(client_seqs.items(), key=lambda x: x[0])
        for seq_idx, (seq_name, intervals_list) in enumerate(sorted_seqs):
            if not intervals_list:
                continue  # 跳过空区间列表
            if seq_idx >= len(cle_sublists):
                continue  # 跳过无对应 cle 数据的序列
            cle_sublist = cle_sublists[seq_idx]
            first_interval = intervals_list[0]  # 取第一个区间
            # 计算该区间的 cle 值总和
            interval_sum = 0
            for idx in first_interval:
                if idx < len(cle_sublist):
                    interval_sum += cle_sublist[idx]
            seq_sums.append(interval_sum)

        if seq_sums:
            cle_client = min(seq_sums)
            cle_client_values.append(cle_client)

    cle_min = min(cle_client_values) if cle_client_values else 0.0

    return cost_avg, cle_min

'''
    计算支持度算法
    参数：序列，第几个序列，模式
'''
def newsup(timestamp_dict, n, p, client_i):
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
        j = 0
        while j < len(p.data[i]):
            if p.data[i][j] in clientNext.get(client_i)[n].keys():
                temp = copy.deepcopy(clientNext.get(client_i)[n].get(p.data[i][j]))
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
                gaptime_flag = time_ok(timestamp_dict.get(client_i), n, usearray[-1], que[count][que[count][0]])
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

# 将时间列表分给每个客户端
def convert_list_to_dict(client, list_s):
    time_dict = {}
    for i in range(len(client)):
        if i == 0:
            start = 0
        else:
            start = client[i-1] + 1
        end = client[i]
        # 提取 time_s 的 [start, end] 区间（包含两端）
        time_dict[i] = list_s[start: end + 1]
    return time_dict

'''
ooc_client = {'client_1':{'seq_1':[[0,2,3], [1,4], [3,4]], 'seq_2':[[0,1], [2,5]]}, 'client_2':{'seq_1':[[0,3], [1,4]]}}
sup_client = {'client_1':[{'a':[30,10,3], 'b':[12,6, 3], 'c':[10,8, 3], 'd':[8,7, 3]}],'client_2':[{'a':[14,7,1], 'b':[18,6,2], 'c':[16,2,4]}]} 
p = [['a'], ['c']]
sup_p_client_1 = len(ooc_client[client_1][seq_1])+len(ooc_client[client_1][seq_2]) = 3+2 =5
sup_p_client_2 = len(ooc_client[client_2][seq_1])= 2
all_conf_client_1 = sup_p_client_1/max{sup_client[client_1][0][a][1], sup_client[client_1][0][c][1]}= 5/max{10,8}= 5/10 =0.5
all_conf_client_2 = sup_p_client_2/max{sup_client[client_2][0][a][1], sup_client[client_2][0][c][1]}= 2/max{7,2} = 2/7
all_conf = (all_conf_client_1+all_conf_client_2)/2 = (0.5+2/7)/2 = 0.39
输入为 ooc_client，sup_client 和 p ，输出为all_conf，使用python代码实现,保留两位小数点
'''
def calculate_all_conf(ooc_client, sup_client, p):
    # 计算分子：所有客户端的序列长度总和
    numerator = 0
    for client in ooc_client:
        client_data = ooc_client[client]
        client_total = sum(len(seq) for seq in client_data.values())
        numerator += client_total

    # 计算分母：最大的项集支持度总和
    denominator = 0
    for itemset in p:
        current_total = 0
        for item in itemset:
            for client in sup_client:
                client_sup = sup_client[client][0]  # 每个客户端的支持信息字典
                if item in client_sup:
                    current_total += client_sup[item][1]  # 第二个数值
        if current_total > denominator:
            denominator = current_total

    # 避免除以0的情况
    if denominator == 0:
        return 0.0

    all_conf = numerator / denominator
    return round(all_conf, 2)

'''读取数据'''
def mainfun():
    # 客户端1，2，3数据分割
    # cli_data = [0, 2, 4]  # 只用于SDB2生成分割数据
    cli_data = [2, 6, 8]  # 只用于SDB3生成分割数据
    # 客户端1，2，3数据分割
    # client = [600, 1200, 1999]  # BPI_Challenge_2019(ELog1)
    # client = [60, 120, 199]  # BPIC15_1(ELog2)
    # client = [100, 200, 299]  # BPIC15_2(ELog3)
    # client = [100, 200, 299]  # BPIC15_3(ELog4)
    # client = [100, 200, 299]  # BPIC15_4(ELog5)
    # client = [100, 200, 299]  # BPIC15_5(ELog6)
    # client = [0, 1, 2]  # SDB2(ELog7)
    client = [0, 1, 2]  # SDB3(ELog8)

    candinum = []  # 候选模式不同长度起始位置
    # 数据集1 csv文件
    # trace_per = read_csv("../data/daily living/")
    # activity_chart_r, timestamp_list_r = data_preprocess(trace_per)

    # xes数据集
    # activity_chart_r, timestamp_list_r, cost_list = read_xes('../dataset/BPI_Challenge_2019.xes',
    #                                                          '../dataset/BPI_Challenge_2019_NoExt.txt')
    # activity_chart_r, timestamp_list_r, cost_list = read_xes('../dataset/BPIC15_1.xes', '../dataset/BPIC15_1_NoExt.txt')
    # activity_chart_r, timestamp_list_r, cost_list = read_xes('../dataset/BPIC15_2.xes', '../dataset/BPIC15_2_NoExt.txt')
    # activity_chart_r, timestamp_list_r, cost_list = read_xes('../dataset/BPIC15_3.xes', '../dataset/BPIC15_3_NoExt.txt')
    # activity_chart_r, timestamp_list_r, cost_list = read_xes('../dataset/BPIC15_4.xes', '../dataset/BPIC15_4_NoExt.txt')
    # activity_chart_r, timestamp_list_r, cost_list = read_xes('../dataset/BPIC15_5.xes', '../dataset/BPIC15_5_NoExt.txt')

    # log_data = read_file("../dataset/SDB2.txt")
    log_data = read_file("../dataset/SDB3.txt")

    # 专为NoExt准备
    # activity_chart_r, timestamp_list_r, cost_list = compose_timestamp_pre(log_data, "../dataset/SDB2_NoExt.txt", cli_data)
    activity_chart_r, timestamp_list_r, cost_list = compose_timestamp_pre(log_data, "../dataset/SDB3_NoExt.txt", cli_data)

    # cost_list = [cost_li]
    # 专为扩展性实验准备
    # activity_chart_r, timestamp_list_r = compose_timestamp_scalability(log_data)
    # print(len(activity_chart_r))
    # print(len(timestamp_list_r))

    seqs, timestamp_s = con_seqs(activity_chart_r, timestamp_list_r)
    # seqs, timestamp_s = con_seqs2(activity_chart_r, timestamp_list_r)
    # print(len(seqs))
    # print(len(timestamp_s))
    # 生成效用文件
    # len_line = [len(sublist) for sublist in timestamp_s]
    # print(len(len_line), len_line)
    # write_txt('../dataset/BPI_Challenge_2019_NoExt.txt', len_line)
    # 读取效用文件
    neu, cle = reconstruction_database(cost_list)
    # print(len(neu), len(res), len(rmu))

    starttime = time.time()
    # onepattern(seqs)  # 1序列模式及位置索引
    sup_client = onepattern(seqs, neu, cle, client)  # 1序列模式及位置索引,0->1

    timestamp_dict = convert_list_to_dict(client, timestamp_s)
    neu_dict = convert_list_to_dict(client, neu)
    cle_dict = convert_list_to_dict(client, cle)
    # sort_item = list(map(str, sort_item))
    # print(sort_item)
    candinum.append(len(candi))
    one_to_two()  # 从FP中生成存到candi
    # sandilinked(sort_item)  # 1->2
    candinum.append(len(candi))
    FP.clear()
    while 1:
        cannum = candinum.pop(0)
        i = cannum
        while i < len(candi):
            ooc_client = {}
            # 先计算每个客户端的成本
            # {'client_1':[{'a':[1,3,5], 'b':[2,4]}, {'a':[2,3], 'b':[1,4]}], 'client_2':[{'a':[1,3,5], 'b':[2,4]}]}
            # {'client_1':[{'a':[1,3,5], 'b':[2,4]}, {'a':[2,3], 'b':[1,4]}], 'client_2':[{'a':[1,3,5], 'b':[2,4]}]}
            for c, v in clientNext.items():
                ooc_dict = dict()
                j = 0
                while j < len(v):
                    addlist = newsup(timestamp_dict, j, candi[i], c)
                    # print(candi[i].data, candi[i].sup)
                    ooc_dict[j] = addlist
                    j += 1
                ooc_client[c] = ooc_dict
            allconf = calculate_all_conf(ooc_client, sup_client, candi[i].data)
            # print(candi[i].data, allconf)
            if allconf >= mincor:
                # 计算平均成本(eac)和成本下限（lbc）
                eac, lbc = average_cost(neu_dict, cle_dict, ooc_client)
                # print(eac, lbc)
                preandsuf(candi[i])
                if eac <= maxeac:
                    FPItem.append(candi[i])
                    FP.append(candi[i])
                elif lbc <= maxeac:
                    FP.append(candi[i])
            i += 1

        sandilinked()
        # FP.clear()
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

