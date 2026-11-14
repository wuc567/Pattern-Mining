import time
import math
import os
import threading
import psutil
from collections import defaultdict
from pro import read_txt
import sys
from shiyan_utility import (
    utility_table1,
    utility_table2,
    utility_table3,
    utility_table4,
    utility_table5,
    utility_table6,
    utility_table7
)


CanNum = 0
matching_count = 0
sup_count = 0
HAWP = []


utility_table = None


def onepattern(seqs):
    """计算每个时间戳的遗忘因子，以及每条序列的最大遗忘因子。"""
    seq_num = len(seqs)
    seq_max_ts = [0] * seq_num
    n = 0

    # 一次扫描得到全局最大时间戳和每条序列的最大时间戳
    for seq_idx, seq in enumerate(seqs):
        local_max = 0
        for _, ts in seq:
            ts = int(ts)
            if ts > local_max:
                local_max = ts
        seq_max_ts[seq_idx] = local_max
        if local_max > n:
            n = local_max

    if n <= 0:
        return [0.0], [0.0] * seq_num

    theta = 1 / n
    exp = math.exp
    seq_forget = [0.0] * (n + 1)
    for t in range(1, n + 1):
        seq_forget[t] = exp(-theta * (n - t))

    seq_max_forget = [seq_forget[ts] if ts > 0 else 0.0 for ts in seq_max_ts]

    return seq_forget, seq_max_forget


def Mine_ItemS(seq_forget, seq_max_forget, max_len, minwau):
    global CanNum

    S = {}
    one_sup_tk = defaultdict(float)
    one_fsup = defaultdict(float)

    # ItemS 只保存真正出现过该 item 的序列，减少大量空列表
    for seq_idx, seq in enumerate(sdb):
        max_forget_i = seq_max_forget[seq_idx]

        for itemset, ts in seq:
            ts = int(ts)
            forget_i = seq_forget[ts]

            for item in itemset:
                item_occ = S.get(item)
                if item_occ is None:
                    item_occ = {}
                    S[item] = item_occ

                positions = item_occ.get(seq_idx)
                if positions is None:
                    item_occ[seq_idx] = [ts]
                else:
                    positions.append(ts)
                # 建立 occurrence 的同时累计 sup_tk 和 fsup
                one_sup_tk[item] += max_forget_i
                one_fsup[item] += forget_i

    H1 = []
    ItemS = {}
    util_get = utility_table.get
    one_Umax = (max_len - 1) * max(utility_table.values())

    for item in sorted(utility_table):
        item_occ = S.get(item)
        if item_occ is None:
            continue

        CanNum += 1
        utility_sum = util_get(item, 0)
        aub = (utility_sum + one_Umax) * one_sup_tk[item] / max_len

        if aub >= minwau:
            pattern = ((item,),)
            H1.append(pattern)
            ItemS[pattern] = item_occ

            hawu = utility_sum * one_fsup[item]
            if hawu >= minwau:
                HAWP.append(pattern)

    return H1, HAWP, ItemS


def _intersect_two_sorted(a, b):
    """双指针求两个升序时间戳列表的交集。"""

    i = j = 0
    out = []
    la, lb = len(a), len(b)

    while i < la and j < lb:

        va, vb = a[i], b[j]
        if va == vb:
            out.append(va)
            i += 1
            j += 1
        elif va < vb:
            i += 1
        else:
            j += 1

    return out


def _iter_common_sequences(list1, list2):
    """只遍历两个模式共同出现的序列。"""
    if len(list1) <= len(list2):
        get2 = list2.get
        for seq_idx, L1 in list1.items():
            L2 = get2(seq_idx)
            if L2:
                yield seq_idx, L1, L2
    else:
        get1 = list1.get
        for seq_idx, L2 in list2.items():
            L1 = get1(seq_idx)
            if L1:
                yield seq_idx, L1, L2


def Matching_I(list1, list2, seq_max_forget):
    global sup_count
    list3 = {}
    sup_tk = 0.0

    for seq_idx, L1, L2 in _iter_common_sequences(list1, list2):
        result = _intersect_two_sorted(L1, L2)
        if result:
            list3[seq_idx] = result
            sup_tk += len(result) * seq_max_forget[seq_idx]
        sup_count += 1

    return list3, sup_tk


def Matching_S(r, list1, list2, seq_max_forget):
    global sup_count

    sup_tk = 0.0
    list3 = {}
    is_i_extension = len(r[-1]) > 1

    for seq_idx, L1, L2 in _iter_common_sequences(list1, list2):
        flag = 0
        # Rule 1：若候选最后一个项集长度大于1，则允许 x = y
        if is_i_extension:
            sup_count += 1
            matched = set(L1).intersection(L2)

            if matched:
                result = set(matched)
                L1_work = [x for x in L1 if x not in matched]
                L2_work = [x for x in L2 if x not in matched]
            else:
                result = set()
                L1_work = L1
                L2_work = L2
        else:
            result = set()
            L1_work = L1
            L2_work = L2

        # Rule 2：按顺序寻找满足 x < y 的匹配
        if L1_work and L2_work:
            len2 = len(L2_work)

            for x in L1_work:
                if flag >= len2:   #终止策略
                    break
                while flag < len2:
                    sup_count += 1
                    y = L2_work[flag]
                    if y > x:
                        result.add(y)
                        flag += 1
                        break
                    flag += 1

        if result:
            result = sorted(result)
            list3[seq_idx] = result
            sup_tk += len(result) * seq_max_forget[seq_idx]

    return list3, sup_tk


def compute_fsup(list3, seq_forget):
    fsup = 0.0
    for positions in list3.values():
        for pos in positions:
            fsup += seq_forget[pos]
    return fsup


def generate_two_len(H1, ItemS, seq_forget, seq_max_forget, max_len, minwau):
    global CanNum, matching_count

    util_get = utility_table.get
    H2 = []
    two_Umax = (max_len - 2) * max(utility_table.values())
    h1_len = len(H1)


    # I-extension：(a b)
    for i in range(h1_len):
        a_pattern = H1[i]
        a = a_pattern[0][0]
        ua = util_get(a, 0)
        occ_a = ItemS[a_pattern]

        for j in range(i + 1, h1_len):
            b_pattern = H1[j]
            b = b_pattern[0][0]
            pattern = ((a, b),)

            CanNum += 1
            matching_count += 1

            list3, sup_tk = Matching_I(
                occ_a, ItemS[b_pattern], seq_max_forget
            )
            if sup_tk <= 0:
                continue

            utility_sum = ua + util_get(b, 0)
            aub = (utility_sum + two_Umax) * sup_tk / max_len

            if aub >= minwau:
                H2.append(pattern)
                ItemS[pattern] = list3


                fsup = compute_fsup(list3, seq_forget)
                hawu = utility_sum * fsup / 2
                if hawu >= minwau:
                    HAWP.append(pattern)

    # S-extension：(a)(b)
    for a_pattern in H1:
        a = a_pattern[0][0]
        ua = util_get(a, 0)
        occ_a = ItemS[a_pattern]

        for b_pattern in H1:
            b = b_pattern[0][0]
            pattern = ((a,), (b,))

            CanNum += 1
            matching_count += 1

            list3, sup_tk = Matching_S(
                pattern, occ_a, ItemS[b_pattern], seq_max_forget
            )
            if sup_tk <= 0:
                continue
            utility_sum = ua + util_get(b, 0)
            aub = (utility_sum + two_Umax) * sup_tk / max_len
            if aub >= minwau:
                H2.append(pattern)
                ItemS[pattern] = list3

                fsup = compute_fsup(list3, seq_forget)
                hawu = utility_sum * fsup / 2
                if hawu >= minwau:
                    HAWP.append(pattern)

    return H2, HAWP,  ItemS


# def join_with_pruning(p, t):
#     global CanNum, matching_count
#
#     last_item = t[-1][-1]
#     key = (p[0][0],)
#     matching_count += 1
#
#     if len(t[-1]) >= 2:
#         r = p[:-1] + (p[-1] + (last_item,),)
#         CanNum += 1
#
#     else:
#         r = p + ((last_item,),)
#         CanNum += 1
#
#     return r, p, t

def join_with_pruning(p, t):
    global CanNum,   matching_count

    matching_count += 1
    last_item = t[-1][-1]

    if len(t[-1]) >= 2:

        r = p[:-1] + (p[-1] + (last_item,),)
    else:

        r = p + ((last_item,),)

    CanNum += 1

    return r

def build_prefix_suffix_dict(HC):
    prefix_dict = defaultdict(set)
    suffix_dict = defaultdict(set)

    for t in HC:
        last = t[-1][:-1]
        t_prefix = t[:-1] + (last,) if last else t[:-1]
        prefix_dict[t_prefix].add(t)

        first = t[0][1:]
        t_suffix = (first,) + t[1:] if first else t[1:]
        suffix_dict[t_suffix].add(t)

    return prefix_dict, suffix_dict


def hawp_miner(seq_forget, seq_max_forget, max_len, minwau):
    global CanNum, matching_count, sup_count

    util_get = utility_table.get
    Umax = max(utility_table.values())

    H1, HAWP_local, ItemS = Mine_ItemS(
        seq_forget, seq_max_forget, max_len, minwau
    )
    H2, HAWP_local, ItemS = generate_two_len(
        H1, ItemS, seq_forget, seq_max_forget, max_len, minwau
    )

    H_current = H2.copy()
    current_m = 2
    # 缓存模式效用，避免后续每次连接重新遍历模式中的所有 item
    pattern_utility = {}
    for p in H_current:
        total = 0
        for itemset in p:
            for item in itemset:
                total += util_get(item, 0)
        pattern_utility[p] = total

    while current_m < max_len:
        pattern_len = current_m + 1
        remain_Umax = (max_len - pattern_len) * Umax
        H_next = []
        prefix_dict, suffix_dict = build_prefix_suffix_dict(H_current)

        for s_key, suffix_patterns in suffix_dict.items():
            prefix_patterns = prefix_dict.get(s_key)

            if not prefix_patterns:
                continue

            for p in suffix_patterns:
                p_utility = pattern_utility[p]
                occ_p = ItemS[p]

                for t in prefix_patterns:
                    r = join_with_pruning(p, t)
                    if r is None:
                        continue

                    occ_t = ItemS[t]
                    if len(r) == 1:
                        list3, sup_tk = Matching_I(
                            occ_p, occ_t, seq_max_forget
                        )
                    else:
                        list3, sup_tk = Matching_S(
                            r, occ_p, occ_t, seq_max_forget
                        )

                    if sup_tk == 0:
                        continue
                    last_item = t[-1][-1]
                    utility_sum = p_utility + util_get(last_item, 0)
                    aub = (utility_sum + remain_Umax)* sup_tk/ max_len

                    if aub >= minwau:
                        H_next.append(r)
                        ItemS[r] = list3
                        pattern_utility[r] = utility_sum
                        fsup = compute_fsup(list3, seq_forget)
                        hawu = utility_sum * fsup / pattern_len
                        if hawu >= minwau:
                            HAWP_local.append(r)

        H_current = H_next
        current_m += 1
        print(f"\n✅ 本轮生成 H_{current_m} 高上界候选集，共 {len(H_next)} 个模式：")
        if not H_current:
            print(f"\n🛑 H_{current_m} 为空，算法提前结束！")
            break

    return HAWP_local, CanNum, matching_count, sup_count


if __name__ == "__main__":

    # path1 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\supermarket_按天划分.txt'
    # path2 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分.txt'
    # path3 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\beauty_按天划分.txt'
    # path4 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\2026ecommerce_按天划分.txt'
    # path5 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\UserBehavior_按天划分.txt'
    # path6 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\Auto Sales_按天划分.txt'
    # path7 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\SDB8 Credite.txt'
    #
    # # 每个数据集对应参数
    #
    # dataset_configs = {
    #     1: {
    #         "name": "supermarket",
    #         "path": path1,
    #         "utility_table": utility_table1,
    #         "minwau": 9000
    #     },
    #     2: {
    #         "name": "car",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 950
    #     },
    #     3: {
    #         "name": "beauty",
    #         "path": path3,
    #         "utility_table": utility_table3,
    #         "minwau": 300
    #     },
    #     4: {
    #         "name": "2026ecommerce",
    #         "path": path4,
    #         "utility_table": utility_table4,
    #         "minwau": 14000
    #     },
    #     5: {
    #         "name": "UserBehavior",
    #         "path": path5,
    #         "utility_table": utility_table5,
    #         "minwau": 8000
    #     },
    #     6: {
    #         "name": "Auto Sales",
    #         "path": path6,
    #         "utility_table": utility_table6,
    #         "minwau": 2500
    #     },
    #     7: {
    #         "name": "SDB8 Credite",
    #         "path": path7,
    #         "utility_table": utility_table7,
    #         "minwau": 15000
    #     }
    # }

    path2 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分.txt'
    path2_2 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_2.txt'
    path2_3 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_3.txt'
    path2_4 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_4.txt'
    path2_5 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_5.txt'
    path2_6 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_6.txt'
    path2_7 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_7.txt'
    path2_8 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_8.txt'

    dataset_configs = {
        1: {
            "name": "car",
            "path": path2,
            "utility_table": utility_table2,
            "minwau": 650
        },
        2: {
            "name": "car",
            "path": path2,
            "utility_table": utility_table2,
            "minwau": 750
        },
        3: {
            "name": "car",
            "path": path2,
            "utility_table": utility_table2,
            "minwau": 850
        },
        4: {
            "name": "car",
            "path": path2,
            "utility_table": utility_table2,
            "minwau": 1050
        },
        5: {
            "name": "car",
            "path": path2,
            "utility_table": utility_table2,
            "minwau": 1150
        }

    }

    dataset_id = int(sys.argv[1])
    config = dataset_configs[dataset_id]
    path = config["path"]
    utility_table = config["utility_table"]
    minwau = config["minwau"]

    # print("===================================")
    # print(f"Dataset ID : {dataset_id}")
    # print(f"Dataset Name : {config['name']}")
    # print(f"Dataset Path : {path}")
    # print(f"minwau : {minwau}")
    # print(f"utility_table size : {len(utility_table)}")
    # print(f"utility_table first 5 : {list(utility_table.items())[:5]}")
    # print("===================================")

    sdb, max_length, SeqNum = read_txt(path)

    # # 再打印数据集本身的信息
    # print(f"SeqNum : {SeqNum}")
    # print(f"max_length : {max_length}")

    start_time = time.time()

    process = psutil.Process(os.getpid())
    base_mem = process.memory_info().rss / 1024 / 1024

    min_mem = base_mem
    max_mem = base_mem
    monitoring = False

    def monitor_memory():
        global min_mem, max_mem, monitoring

        process = psutil.Process(os.getpid())

        while monitoring:
            mem = process.memory_info().rss / 1024 / 1024
            min_mem = min(min_mem, mem)
            max_mem = max(max_mem, mem)
            time.sleep(0.2)

    def run_mining():
        seq_forget, seq_max_forget = onepattern(sdb)

        max_len = 10

        return hawp_miner(
            seq_forget,
            seq_max_forget,
            max_len,
            minwau
        )

    monitoring = True

    monitor_thread = threading.Thread(
        target=monitor_memory,
        daemon=True
    )

    monitor_thread.start()
    final_hawp,  CanNum, matching_count, sup_count = run_mining()
    end_time = time.time()
    monitoring = False
    monitor_thread.join(timeout=1)

    print(f"Peak Usage : {max_mem - min_mem:.2f} MB")
    print(f"running time: {end_time - start_time:.4f} 秒")
    print(f"生成候选模式数量：{CanNum}")
    print(f"支持度计算次数：{sup_count}")
    print(f"模式匹配次数：{matching_count}")
    print(f"hawp number：{len(final_hawp)}")