import sys
sys.setrecursionlimit(1000000)
import time
import os
import psutil
from collections import Counter
import numpy as np
import cProfile

sDB = []
# sdbstore = []
# filter1 = []  # 设置过滤，长度为1的filter；如果为0，对应ID的sequence被过滤掉；为1进行计算,
filter = []  # 设置过滤，如果为0，对应的ID的sequence被过滤掉；为1进行计算
# num_lines = 2000  #用来选取数据库中序列的数量
mingap = 0
maxgap = 2
DT=5
delta = 10
minpua = 20
first = ('T', '58')  # 用于共生的一长度情节


minpua = 120*1
filename="sdb6-1.txt"
#filename="t-509.txt"
#filename="t-550.txt"
#minpua = 40
#filename="t-683.txt"
#minpua = 30
#filename="t-759.txt"
#minpua = 50
#filename="t-904.txt"
#minpua = 50
#filename="t-1010.txt"
#minpua = 20
#filename="T-1492.txt"

allsigma = []  # 所有字符
frequence = {}  # 用于收集字符频率
new_allsigma = []  #共生字符
new_frequence = {}  #共生字符频率

class sigma_sdb_struct:
    def __init__(self):
        self.id = -1
        self.sigma = {}
        self.store = []

class sigma_pos_struct:
    def __init__(self):
        self.ch = 'a'
        self.position = []
        self.timestamp = []  # 新增列表以存储时间戳
        self.fre = -1

class episode_struct:
    def __init__(self):
        self.episode = []  # 将存储形如 [('S', '145'), ('T', '109')] 的模式
        self.utility = -1

'''读取原txt数据，把文本数据的每一行转存到事件结果集和时间戳集中'''
def data_preprocess(txt_data):
    activity_chart = []  # 事件缩写结果集
    timestamp_list = []  # 时间戳集
    # 1. 逐行处理 TXT 数据
    for line in txt_data:
        # 创建新的事件缩写列表和时间戳列表
        activity_line = []
        timestamp_line = []
        # 删除行中的括号，然后根据逗号拆分成二元组
        tuples = line.strip()[1:-1].split(")(")
        # 处理每个二元组
        for tup in tuples:
            # 假设二元组的格式为 "事件缩写,时间戳"
            parts = tup.split(",")
            if len(parts) == 2:
                activity_line.append(parts[0])
                timestamp_line.append(parts[1])
        # 将每行的事件缩写列表和时间戳列表添加到结果集中
        activity_chart.append(activity_line)
        timestamp_list.append(timestamp_line)
    # 返回结果，确保activity_chart每个元素都是一个嵌套列表
    return activity_chart, timestamp_list

def read_txt_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

'''
生成情节效用值字典，便于之后频繁一长度情节的计算，5.11：要注意不同数据集中时间戳的分布会影响其百分比
'''
def utility_calculate(activity_chart, timestamp_list):
    # 统计字符和时间戳出现的次数
    char_counter = Counter()
    timestamp_counter = Counter()

    for activity in activity_chart:
        char_counter.update(activity)

    for timestamps in timestamp_list:
        timestamp_counter.update(timestamps)

    # 计算总数
    total_chars = sum(char_counter.values())
    total_timestamps = sum(timestamp_counter.values())

    # 计算每个字符和时间戳的百分比
    char_percentages = {item: (count / total_chars * 100) for item, count in char_counter.items()}
    timestamp_percentages = {item: (count / total_timestamps * 100) for item, count in timestamp_counter.items()}

    # 初始化效用字典和效用值计数器
    char_utility = {}
    timestamp_utility = {}
    timestamp_utility_count = {0.5: 0, 1: 0, 2: 0, 3: 0}  # 初始化效用值计数器

    # 效用值给字符
    for rank, (char, percentage) in enumerate(char_percentages.items(), start=1):
        if rank <= 3:
            char_utility[char] = 5
        elif rank <= 10:
            char_utility[char] = 4
        elif rank <= 15:
            char_utility[char] = 3
        else:
            char_utility[char] = 2

    # 效用值给时间戳
    for timestamp, percentage in timestamp_percentages.items():
        if percentage >= 1.5:
            timestamp_utility[timestamp] = 3
            timestamp_utility_count[3] += 1
        elif percentage >= 1.0 and percentage < 1.5:
            timestamp_utility[timestamp] = 2
            timestamp_utility_count[2] += 1
        elif percentage >= 0.5 and percentage < 1.0:
            timestamp_utility[timestamp] = 1
            timestamp_utility_count[1] += 1
        elif percentage <= 0.5:
            timestamp_utility[timestamp] = 0.5
            timestamp_utility_count[0.5] += 1

    return char_utility, char_percentages, timestamp_utility, timestamp_percentages, timestamp_utility_count

def scan_sequence(activity_line, timestamp_line, store, sigma):
    count = 1
    for i in range(len(activity_line)):
        ch = activity_line[i]
        ts = timestamp_line[i]
        if ch not in sigma:
            current = sigma_pos_struct()
            sigma[ch] = count
            count += 1
            current.ch = ch
            current.position.append(i)
            current.timestamp.append(ts)  # 添加时间戳
            store.append(current)
        else:
            chno = sigma[ch] - 1
            store[chno].position.append(i)
            store[chno].timestamp.append(ts)  # 添加时间戳

def scan_SDB(first, allsigma,frequence, sDB, new_allsigma, new_frequence):
    global filter1
    filter1 = []
    sdbstore = []

    character, time = first
    activity_chart, timestamp_list = sDB

    for id in range(len(activity_chart)):
        activity_line = activity_chart[id]
        timestamp_line = timestamp_list[id]

        temp = sigma_sdb_struct()
        temp.id = id
        temp.store = []
        temp.sigma = {}
        scan_sequence(activity_line, timestamp_line, temp.store, temp.sigma)
        sdbstore.append(temp)

    for id in range(len(activity_chart)):
        flag = 0
        for j in range(len(sdbstore[id].store)):
            ch = sdbstore[id].store[j].ch
            for k in range(len(sdbstore[id].store[j].position)):
                pos = sdbstore[id].store[j].position[k]
                ts = sdbstore[id].store[j].timestamp[k]

                ch_ts_pair = (ch, ts)
                if ch_ts_pair not in frequence:
                    frequence[ch_ts_pair] = 1
                    allsigma.append(ch_ts_pair)
                else:
                    frequence[ch_ts_pair] += 1

                if ch == character and ts == time:
                    flag += 1

        filter1.append(flag)
    filtered_sdbstore = [sdbstore[i] for i in range(len(filter1)) if filter1[i] != 0]

    for store in filtered_sdbstore:
        for item in store.store:
            for pos, ts in zip(item.position, item.timestamp):
                ch_ts_pair = (item.ch, ts)
                # 生成共生情节信息
                if ch_ts_pair not in new_frequence:
                    new_frequence[ch_ts_pair] = 1
                    new_allsigma.append(ch_ts_pair)
                else:
                    new_frequence[ch_ts_pair] += 1

    return sdbstore, filter1, filtered_sdbstore, new_allsigma, new_frequence

'''
4.27:正确使用DBI来进行支持度的计算，逻辑是正确的，能返回支持度的值.注意：cand的长度必须大于等于2
'''
def support_sequence(cand, filtered_sdbstore, mingap, maxgap):
    sup = 0
    # next = []
    # 遍历过滤后sdbstore中的每个sigma_sdb_struct实例
    for seq_idx, seq_store in enumerate(filtered_sdbstore):
        pv = [[] for _ in cand]  # 初始化候选匹配位置列表
        all_match = True
        # print(f"\nProcessing sequence {seq_idx + 1} in sdbstore")

        # 检查每个候选模式元素及其时间戳是否存在
        for i, (character, timestamp) in enumerate(cand):
            timestamp = str(timestamp)
            # print(f"  Checking candidate {character} at timestamp {timestamp}")

            if character not in seq_store.sigma:
                # print(f"  - Character {character} not found in sigma")
                all_match = False
                break

            char_index = seq_store.sigma[character] - 1
            matched_positions = [pos for pos, ts in zip(seq_store.store[char_index].position,
                                                       seq_store.store[char_index].timestamp) if ts == timestamp]
            # print(f"  - Found positions for {character} at timestamp {timestamp}: {matched_positions}")

            if not matched_positions:
                # print(f"  - No positions found for {character} at timestamp {timestamp}")
                all_match = False
                break

            pv[i] = matched_positions  # 存储每个候选的匹配位置

        if not all_match:
            # print("  - Not all candidates matched, skipping this sequence.")
            continue

        roots1 = []
        for i in range(len(pv[0])):
            root1 = pv[0][i]
            roots1.append(root1)
        for len_ in range(len(pv[0])):
            root = roots1[len_]
            # print('root1:',root )
            level = 1
            occurrence = {0: root}
            next = [0] * len(cand)
            next[level-1] = len_ + 1

            result = depthfirst_support(root, level, cand, mingap, maxgap, next, pv, occurrence)
            if result == len(cand):
                sup += 1
                # print(f"  Complete pattern found starting at root {root}. Total support count now {sup}")
            if result == -3:
                break
            # else:
            #     print("  DFS did not find a complete pattern.")

    # print(f"Total patterns found after processing all sequences: {sup}")
    return sup

def depthfirst_support(node, level, cand, mingap,
                       maxgap, next, patternv, occurrence):
    while True:
        childlevel = level
        while True:
            # childstore = patternv[childlevel]
            childpos = next[childlevel]
            if childpos == len(patternv[childlevel]):
                return -3
            next[childlevel] += 1
            child = patternv[childlevel][childpos]
            val = child - node - 1
            if val >= mingap:
                break
        if (mingap <= val) and (val <= maxgap):
            occurrence[level] = child
            node = child
            # occurrence = {level: child}
            level += 1
            # print(f"  Complete pattern found level:{level} at root {child}.")
        else:
            next[childlevel] -= 1
            if level - 2 < 0:
                return -1
            cparentpos = next[level - 2] -1
            # cparentstore = patternv[level - 2]
            pv_re = patternv[level - 2]
            cparent = pv_re[cparentpos]
            node = cparent
            level = level - 1

        if not ((level > 0) and (level < len(cand))):
            break

    if level == len(cand):
        return level
    elif level <= 0:
        return -1

# cand = [('T', '72'), ('O', '73')]  # 将元组转换为列表
# # seq_store = sdbstore  #没有用到哦，其实还是用到了
# support_count = support_sequence(cand, filtered_sdbstore, mingap, maxgap)
# print("Support count for the cand:", support_count)

'''
可以计算出cand在整个数据集中的支持度
'''
def support_SDB_prefix(cand, sdbstore, filter1, mingap, maxgap):
    global filter
    sup = 0
    len_ = len(cand)
    if len_ >= 2:
        filter = []  # 初始化filter列表
        for id in range(len(sdbstore)):
            result = support_sequence(cand, [sdbstore[id]], mingap, maxgap)
            filter.append(result)
            sup += result
    else:
        filter = filter1
        for id in range(len(sdbstore)):
            sup += filter[id]
    return sup

HU1_utility={}
HAU1 = []
HU1 = []
def discover_frequent_sigma(new_allsigma, HAU1, minpua, HU1, char_utility, timestamp_utility, new_frequence):
    # 计算时间戳效用值中的最大值
    max_timestamp_utility = max(timestamp_utility.values())

    for ch_ts_pair in new_allsigma:
        ch, ts = ch_ts_pair
        # 检查字符和时间戳是否都有对应的效用值和频率记录
        if ch in char_utility and ts in timestamp_utility and ch_ts_pair in new_frequence:
            char_util_value = char_utility[ch]
            timestamp_util_value = timestamp_utility[ts]
            freq = new_frequence[ch_ts_pair]
            ##hupval = char_util_value * timestamp_util_value * freq  # 效用值计算方式
            hupval = char_util_value * timestamp_util_value  # 效用值计算方式
            Umax = char_util_value * max_timestamp_utility

            HAU1.append(ch_ts_pair)     #enumeration   all items
            HU1.append(ch_ts_pair)      #enumeration   all items
            
            #if hupval >= minpua:
            #    HAU1.append(ch_ts_pair)
            #    HU1.append(ch_ts_pair)
            #else:
            #    uphupval = freq * Umax  # 根据新的 Umax 更新这个计算方式
            #    HU1.append(ch_ts_pair)
            #    if uphupval >= minpua:
            #        HU1.append(ch_ts_pair)
        else:
            print(f"Utility or frequency value missing for {ch_ts_pair}")

def calculate_hu1_utility(new_allsigma, minpua, char_utility, timestamp_utility, new_frequence):
    max_timestamp_utility = max(timestamp_utility.values())
    for ch_ts_pair in new_allsigma:
        ch, ts = ch_ts_pair
        # 检查字符和时间戳是否都有对应的效用值和频率记录
        if ch in char_utility and ts in timestamp_utility and ch_ts_pair in new_frequence:
            char_util_value = char_utility[ch]
            timestamp_util_value = timestamp_utility[ts]
            freq = new_frequence[ch_ts_pair]
            # hupval = char_util_value * timestamp_util_value * freq  # 效用值计算方式
            hupval = char_util_value * timestamp_util_value  # 效用值计算方式
            Umax = char_util_value * max_timestamp_utility
            
            HU1_utility[ch_ts_pair] = hupval   #enumruation

            #if hupval >= minpua:
            #    HU1_utility[ch_ts_pair] = hupval
            #else:
            #    uphupval = freq * Umax  # 根据新的 Umax 更新这个计算方式
            #    if uphupval >= minpua:
            #        HU1_utility[ch_ts_pair] = hupval
    return HU1_utility



def support_Filtered_SDB(cand, mingap, maxgap):
    sup = 0
    for id in range(len(filtered_sdbstore)):
        sup += support_sequence(cand, [filtered_sdbstore[id]], mingap, maxgap)
    return sup

HAU2 = []
HU2 = []
# def discover_frequent_2pattern(HU1, minpua, HU2, HAU2, mingap, maxgap, prefix):
#     Umax_try = 15   #一长度情节自身最大的内部效用值，如（ch, timestamp）的最大效用值:ch-max * timestamp-max
#     len_fp = len(prefix)
#     HU1_utility = calculate_hu1_utility(new_allsigma, minpua, char_utility, timestamp_utility, new_frequence)
#     if len_fp == 1:  # 只处理长度为1的前缀，用于生成长度为2的情节
#         for i in range(len(HU1)):
#             for j in range(len(HU1)):  # 避免自身组合和重复组合i + 1, len(HU1)
#                 ti = HU1[i]
#                 tj = HU1[j]
#                 # 提取时间戳并转换为整数
#                 ti_char, ti_time = ti
#                 tj_char, tj_time = tj
#                 ti_time = int(ti_time)
#                 tj_time = int(tj_time)
#                 # 检查时间戳逻辑
#                 if ti_time < tj_time and 1 <= (tj_time - ti_time) <= 5:
#                     cand = [ti, tj]  # 创建候选二元组
#                     # o = support_SDB_prefix([ti], filtered_sdbstore, filter1, mingap,
#                     #                    maxgap)  # 必须得调用support_SDB_prefix函数，不然没有filter会超出索引
#                     sup = support_Filtered_SDB(cand, mingap, maxgap)  # 计算候选模式的支持度
#                     # hupval = 0
#                     # for s in range(len(cand)):
#                     #     hupval += HU1_utility[cand[s]]
#                     # hupval = sup * hupval / len(cand)
#                     hupval = (HU1_utility[ti] + HU1_utility[tj]) * sup / len(cand)   # 效用值计算，使用字典中的值,两种方式都可以
#                     # print("1", HU1_utility[ti])
#                     # print("2", HU1_utility[tj])
#                     if hupval >= minpua:
#                         HAU2.append(cand)
#                         HU2.append(cand)
#                     else:
#                         uphupval = sup * minpua  # 计算最大可能效用，避免遗漏有用的模式
#                         if uphupval >= minpua:
#                             HU2.append(cand)

def discover_frequent_2pattern(HU1, minpua, HU2, HAU2, mingap, maxgap, prefix):
    Umax_try = 20   #一长度情节自身最大的内部效用值，如（ch, timestamp）的最大效用值:ch-max * timestamp-max
    len_fp = len([prefix])
    Co_char, Co_time = prefix
    Co_time = int(Co_time)
    HU1_utility = calculate_hu1_utility(new_allsigma, minpua, char_utility, timestamp_utility, new_frequence)
    if len_fp == 1:  # 只处理长度为1的前缀，用于生成长度为2的情节
        for i in range(len(HU1)):
            for j in range(len(HU1)):  # 避免自身组合和重复组合i + 1, len(HU1)
                ti = HU1[i]
                tj = HU1[j]
                # 提取时间戳并转换为整数
                ti_char, ti_time = ti
                tj_char, tj_time = tj
                ti_time = int(ti_time)
                tj_time = int(tj_time)

                time_2_diff = tj_time - ti_time
                ti_relative = ti_time - Co_time
                tj_relative = tj_time - Co_time
                # 检查时间戳逻辑
                if ti_time < tj_time and 1 <= time_2_diff <= DT and 0 <= ti_relative <= delta and 0 <= tj_relative <= delta:
                    cand = [ti, tj]  # 创建候选二元组
                    # o = support_SDB_prefix([ti], filtered_sdbstore, filter1, mingap,
                    #                    maxgap)  # 必须得调用support_SDB_prefix函数，不然没有filter会超出索引
                    sup = support_Filtered_SDB(cand, mingap, maxgap)  # 计算候选模式的支持度
                    # hupval = 0
                    # for s in range(len(cand)):
                    #     hupval += HU1_utility[cand[s]]
                    # hupval = sup * hupval / len(cand)
                    hupval = (HU1_utility[ti] + HU1_utility[tj]) * sup / len(cand)   # 效用值计算，使用字典中的值,两种方式都可以
                    # print("1", HU1_utility[ti])
                    # print("2", HU1_utility[tj])
                    if hupval >= minpua:
                        HAU2.append(cand)
                        HU2.append(cand)
                    else:
                        uphupval = sup * minpua  # 计算最大可能效用，避免遗漏有用的模式
                        if uphupval >= minpua:
                            HU2.append(cand)


candidate = []
maxsize = 0
HACoE = []
routes = {}
BET = 0
nonBET = 0
length_canlen = []

def enumtree_BETsigma(prefix, freq_sigma,
                      HU2, mingap, maxgap, minpua):
    global BET, nonBET, maxsize
    cur_pattern = [prefix]
    prefixlen = len(prefix)
    HU1_utility = calculate_hu1_utility(new_allsigma, minpua, char_utility, timestamp_utility, new_frequence)
    candcount = 0
    while True:
        for i in range(len(freq_sigma)):
            item = freq_sigma[i]
            cur_pattern_char, cur_pattern_time = cur_pattern[-1]  #是cur_pattern的最后一个元素的二元组信息
            cur_pattern_char_first, cur_pattern_time_first = cur_pattern[0]  #是cur_pattern的第一个元素的二元组信息
            item_char, item_time = item
            cur_pattern_time = int(cur_pattern_time)
            cur_pattern_time_first = int(cur_pattern_time_first)
            item_time = int(item_time)
            if cur_pattern_time < item_time and 1 <= (item_time - cur_pattern_time) <= 5 and 1 <= (item_time - cur_pattern_time_first) <= 10:
                cand = []
                cand.extend(cur_pattern)
                cand.append(item)
                # print("cand:", cand)
                cur_len = len(cur_pattern)
                # if prefixlen < cur_len:
                #     t = cur_pattern[cur_len - 1]
                #     last2 = [t, item]
                #     if last2 not in HU2:
                #         BET += 1
                #         continue
                size = len(candidate)
                if maxsize < size:
                    maxsize = size
                nonBET += 1
                # o = support_SDB_prefix(cand, sdbstore, filter1, mingap,
                #                        maxgap)  # 必须得调用support_SDB_prefix函数，不然没有filter会超出索引
                sup = support_Filtered_SDB(cand, mingap, maxgap)  # 计算候选模式的支持度
                # print("sup:", sup)
                hupval = 0
                candcount += 1
                for s in range(len(cand)):
                    # if cand == [('T', '58'), ('T', '62')]:
                    #     print(cand[s], '------', HU1_utility[cand[s]])
                    hupval += HU1_utility[cand[s]]

                hupval_ = sup * hupval / len(cand)
                # if cand == [('T', '58'), ('T', '62')]:
                #     print(hupval, sup, len(cand), hupval_)
                # print("hupval:", hupval_)

                if hupval_ >= minpua:
                    HACoE.append(cand)
                    # if len (cand)==2:
                    #    print('HACop:', cand, sup, hupval_, len (cand), hupval)
                    tmp = episode_struct()
                    tmp.name = cand
                    tmp.utility = hupval_
                    candidate.append(cand)
                    if len(cand) not in routes:
                        routes[len(cand)] = {}
                    cand_str = "-".join(f"{char}:{ts}" for char, ts in cand)  # 转换每个元组为字符串
                    routes[len(cand)][cand_str] = hupval_
        if len(candidate) == 0:
            break
        cur_pattern = candidate[-1]
        candidate.pop()
        # length_canlen.append(len(candidate))
        # print(candidate)    #只是为了观察挖掘的进程
        # print('Min candidate len:',np.array(length_canlen).min(),'candidate len:',len(candidate))   #只是为了观察挖掘的进程，无实际意义
    print('候选模式数量', candcount)


pr = cProfile.Profile()
pr.enable()

s = time.time()
print ('minpua=',minpua)
print (filename)

txt_data = read_txt_file(filename)
#txt_data = read_txt_file("D:\\tianchi\EPISODE_MINING\HACoE_Miner\Merged_A_B_x7.txt")
activity_chart, timestamp_list = data_preprocess(txt_data)
processed_sdb = (activity_chart, timestamp_list)
char_utility, char_percentages, timestamp_utility, timestamp_percentages, timestamp_utility_count = utility_calculate(
    activity_chart, timestamp_list)

sdbstore, filter1, filtered_sdbstore, new_allsigma, new_frequence = scan_SDB(first, allsigma, frequence,
                                                                             processed_sdb, new_allsigma, new_frequence)
discover_frequent_sigma(new_allsigma, HAU1, minpua, HU1, char_utility, timestamp_utility, new_frequence)
discover_frequent_2pattern(HU1, minpua, HU2, HAU2, mingap, maxgap, first)
enumtree_BETsigma(first, HU1, HU2, mingap, maxgap, minpua)

print('运行时间', time.time() - s)
# print('HU1的长度：', len(HU1))
# print('HU1:', HU1)
# print('HU2:', HU2)
# print('HU2的长度：', len(HU2))
print('HACE-Enum数量', len(HACoE))
#print('处理序列个数', len(filtered_sdbstore))
# print(HACoE)
# for length, route in routes.items():
#     tmp = sorted(route.items(), key=lambda x:x[1], reverse=True)
#     print('长度为{}的情节:'.format(length), dict(tmp))
print(u'Memory usage of the current process: %.3f MB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024))


<<<<<<< HEAD
#pr.disable()
#pr.print_stats(sort='time')
=======
# cand = [('T', '72'), ('T', '73'), ('O', '75'), ('X', '76')]  # 将元组转换为列表
# HU1_utility = calculate_hu1_utility(new_allsigma, minpua, char_utility, timestamp_utility, new_frequence)
# sup_cand = support_Filtered_SDB(cand, mingap, maxgap)
# for i in range(len(cand)):
#     print(HU1_utility[cand[i]])
#
# cand1 = [('O', '75'),('X', '76')]
# sup_cand1 = support_Filtered_SDB(cand1, mingap, maxgap)
# print('sup_cand1:', sup_cand1)
# for i in range(len(cand1)):
#     print(HU1_utility[cand1[i]])
# hupval = 0
# for s in range(len(cand1)):
#     hupval += HU1_utility[cand1[s]]
# hupval_ = sup_cand1 * hupval / len(cand1)
# print('hupval:', hupval_)

# cur_pattern = [('T', '72'),('T', '73'),('O', '75')]
# cur_len = len(cur_pattern)
# print(cur_len)
# t = cur_pattern[cur_len - 1]
# print(t)

# cand2 = [('T', '72'), ('T', '73'), ('O', '75'), ('X', '76'), ('I', '77'),('P', '78'),('X', '82')]  # 将元组转换为列表
# for i in range(len(cand2)):
#     print(HU1_utility[cand2[i]])
#
# cand1 = [('I', '77'),('P', '78')]
# sup_cand1 = support_Filtered_SDB(cand1, mingap, maxgap)
# print('sup_cand1:', sup_cand1)
# for i in range(len(cand1)):
#     print(HU1_utility[cand1[i]])
# hupval = 0
# for s in range(len(cand1)):
#     hupval += HU1_utility[cand1[s]]
# hupval_ = sup_cand1 * hupval / len(cand1)
# print('hupval:', hupval_)
>>>>>>> cfa4dbc9dcdbad0c2bb3ef52bb1ab7da0f069ed9
