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
I_PSD = {'suf': defaultdict(set)}
S_PSD = {'suf': defaultdict(set)}
utility_table = utility_table1

def onepattern(seqs):

    seq_num = len(seqs)
    seq_max_ts = [0] * seq_num
    n = 0
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
        return ([0.0], [0.0] * seq_num)
    theta = 1 / n
    exp = math.exp
    seq_forget = [0.0] * (n + 1)
    for t in range(1, n + 1):
        seq_forget[t] = exp(-theta * (n - t))
    seq_max_forget = [seq_forget[ts] if ts > 0 else 0.0 for ts in seq_max_ts]
    return seq_forget, seq_max_forget


def Mine_ItemS(seq_forget, seq_max_forget, max_len, minwau):

    global I_PSD, S_PSD, CanNum, utility_table, SeqNum, HAWP

    S = {}
    for seq_idx, seq in enumerate(sdb):
        for itemset, ts in seq:
            ts = int(ts)
            for item in itemset:
                if item not in S:
                    S[item] = [[] for _ in range(SeqNum)]
                S[item][seq_idx].append(ts)
    util_get = utility_table.get
    H1 = []
    ItemS = {}
    max_utility = max(utility_table.values())
    one_Umax = (max_len - 1) * max_utility
    sorted_items = sorted(utility_table.keys())
    for item in sorted_items:
        CanNum += 1
        timestamps = S.get(item)
        if timestamps is None:
            continue
        sup_tk = 0.0
        fsup = 0.0
        for seq_idx in range(SeqNum):
            seq_timestamps = timestamps[seq_idx]
            if not seq_timestamps:
                continue
            sup_tk += len(seq_timestamps) * seq_max_forget[seq_idx]
            for ts in seq_timestamps:
                fsup += seq_forget[ts]
        utility_sum = util_get(item, 0)
        aub = (utility_sum + one_Umax) * sup_tk / max_len
        if aub >= minwau:
            pattern = ((item,),)
            H1.append(pattern)
            ItemS[item,] = timestamps
            hawu = utility_sum * fsup
            if hawu >= minwau:
                HAWP.append(pattern)


    return H1, HAWP, ItemS

def Matching_I(list1, list2):

    global sup_count

    list3 = [[] for _ in range(SeqNum)]
    for seq_idx in range(SeqNum):
        list3[seq_idx] = sorted(set(list1[seq_idx]) & set(list2[seq_idx]))
        sup_count += 1
    return list3

def compute_support(list3, seq_max_forget):

    sup_k = 0.0

    for seq_idx in range(SeqNum):
        positions = list3[seq_idx]
        if not positions:
            continue
        sup_k += len(positions) * seq_max_forget[seq_idx]
    return sup_k

def compute_fsup(list3, seq_forget):

    fsup = 0.0

    for seq_idx in range(SeqNum):
        positions = list3[seq_idx]
        if not positions:
            continue
        for pos in positions:
            fsup += seq_forget[pos]
    return fsup

def _iter_common_sequences(unit):

    if not unit:
        return
    for seq_idx in range(SeqNum):
        positions_list = []
        valid = True
        for occ in unit:
            positions = occ[seq_idx]
            if not positions:
                valid = False
                break
            positions_list.append(positions)
        if valid:
            yield (seq_idx, positions_list)

def DFOM_support(pattern, ItemS, seq_max_forget):

    global sup_count

    sup_tk = 0.0
    list3 = [[] for _ in range(SeqNum)]
    pattern_len = len(pattern)
    unit = []
    for itemset in pattern:
        occ = ItemS[itemset]
        unit.append(occ)
    for seq_idx, positions_list in _iter_common_sequences(unit):
        max_forget_seq = seq_max_forget[seq_idx]

        nettree = [[] for _ in range(pattern_len)]
        end_positions = []
        first_positions = positions_list[0]
        for first_pos in first_positions:
            failed = False
            nettree[0].append(first_pos)

            for level in range(1, pattern_len):
                positions = positions_list[level]
                found = False

                if nettree[level]:
                    previous_same_level = nettree[level][-1]
                else:
                    previous_same_level = -1
                previous_level = nettree[level - 1][-1]

                for pos in positions:
                    sup_count += 1
                    if pos > previous_level and pos > previous_same_level:
                        nettree[level].append(pos)
                        found = True
                        if level == pattern_len - 1:
                            end_positions.append(pos)
                            sup_tk += max_forget_seq
                        break

                if not found:
                    failed = True
                    break

            if failed:
                break

        if end_positions:
            list3[seq_idx] = end_positions

    return sup_tk, list3

def generate_two_len(H1, ItemS, seq_forget, seq_max_forget, max_len, minwau):
    global CanNum, matching_count,HAWP

    util_get = utility_table.get
    H2 = []
    two_Umax = (max_len - 2) * max(utility_table.values())
    h1_len = len(H1)
    Isuf = I_PSD['suf']
    Ssuf = S_PSD['suf']

    for i in range(h1_len):
        a_pattern = H1[i]
        a = a_pattern[0][0]
        ua = util_get(a, 0)
        for j in range(i + 1, h1_len):
            b_pattern = H1[j]
            b = b_pattern[0][0]
            pattern = ((a, b),)
            CanNum += 1
            matching_count += 1
            list3 = Matching_I(ItemS[a,], ItemS[b,])
            sup_tk = compute_support(list3, seq_max_forget)
            if sup_tk <= 0:
                continue
            utility_sum = ua + util_get(b, 0)
            aub = (utility_sum + two_Umax) * sup_tk / max_len
            if aub >= minwau:
                H2.append(pattern)
                ItemS[pattern[0]] = list3
                Isuf[a,].add(b)
                fsup = compute_fsup(list3, seq_forget)
                hawu = utility_sum * fsup / 2
                if hawu >= minwau:
                    HAWP.append(pattern)
    for a_pattern in H1:
        a = a_pattern[0][0]
        ua = util_get(a, 0)
        for b_pattern in H1:
            b = b_pattern[0][0]
            pattern = ((a,), (b,))
            CanNum += 1
            matching_count += 1
            sup_tk, list3 = DFOM_support(pattern, ItemS, seq_max_forget)
            if sup_tk <= 0:
                continue
            utility_sum = ua + util_get(b, 0)
            aub = (utility_sum + two_Umax) * sup_tk / max_len

            if aub >= minwau:
                H2.append(pattern)
                Ssuf[a,].add(b)
                fsup = compute_fsup(list3, seq_forget)
                hawu = utility_sum * fsup / 2
                if hawu >= minwau:
                    HAWP.append(pattern)

    return H2, HAWP, I_PSD, S_PSD, ItemS

def join_with_pruning(p, t):
    global CanNum,matching_count

    last_item = t[-1][-1]
    key = (p[0][0],)
    matching_count += 1
    if len(t[-1]) >= 2:
        if len(p) == 1:
            if last_item not in I_PSD['suf'][key]:
                return None
        elif last_item not in S_PSD['suf'][key]:
            return None
        r = p[:-1] + (p[-1] + (last_item,),)

        CanNum += 1

    else:
        if key not in S_PSD['suf'] or last_item not in S_PSD['suf'][key]:
            return None
        r = p + ((last_item,),)
        CanNum += 1
    return r

def build_prefix_suffix_dict(HC):
    prefix_dict = defaultdict(set)
    suffix_dict = defaultdict(set)

    for t in HC:
        last = t[-1][:-1]
        if last:
            t_prefix = t[:-1] + (last,)
        else:
            t_prefix = t[:-1]
        prefix_dict[t_prefix].add(t)
        first = t[0][1:]
        if first:
            t_suffix = (first,) + t[1:]
        else:
            t_suffix = t[1:]
        suffix_dict[t_suffix].add(t)


    return prefix_dict, suffix_dict

def hawp_miner(seq_forget, seq_max_forget, max_len, minwau):
    global CanNum,matching_count,sup_count,HAWP

    util_get = utility_table.get
    Umax = max(utility_table.values())
    H1, HAWP_local, ItemS = Mine_ItemS(seq_forget, seq_max_forget, max_len, minwau)

    H2, HAWP_local, I_PSD_local, S_PSD_local, ItemS = generate_two_len(H1, ItemS,
                                    seq_forget, seq_max_forget, max_len, minwau)
    H_current = H2.copy()
    current_m = 2
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
                for t in prefix_patterns:
                    r = join_with_pruning(p, t)
                    if r is None:
                        continue
                    if len(r) == 1:
                        prefix_itemset = r[0][:-1]
                        last_itemset = (r[0][-1],)
                        list1 = ItemS.get(prefix_itemset)
                        list2 = ItemS.get(last_itemset)

                        if list1 is None or list2 is None:
                            continue

                        list3 = Matching_I(list1, list2)
                        sup_tk = compute_support(list3, seq_max_forget)

                    else:
                        missing_itemset = False
                        for itemset in r:
                            if itemset not in ItemS:
                                missing_itemset = True
                                break
                        if missing_itemset:
                            continue
                        sup_tk, list3 = DFOM_support(r, ItemS, seq_max_forget)

                    if sup_tk == 0:
                        continue
                    last_item = t[-1][-1]
                    utility_sum = p_utility + util_get(last_item, 0)
                    aub = (utility_sum + remain_Umax) * sup_tk / max_len

                    if aub >= minwau:
                        H_next.append(r)
                        pattern_utility[r] = utility_sum
                        if len(r) == 1:
                            ItemS[r[0]] = list3
                        fsup = compute_fsup(list3, seq_forget)
                        hawu = utility_sum * fsup / pattern_len
                        if hawu >= minwau:
                            HAWP_local.append(r)
        H_current = H_next
        current_m += 1
        print(f'\n✅ 本轮生成 H_{current_m} 高上界候选集，共 {len(H_next)} 个模式：')
        if not H_current:
            print(f'\n🛑 H_{current_m} 为空，算法提前结束！')
            break

    return HAWP_local, I_PSD_local, S_PSD_local, CanNum, matching_count, sup_count


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
    final_hawp, I_PSD, S_PSD, CanNum, matching_count, sup_count = run_mining()
    end_time = time.time()
    monitoring = False
    monitor_thread.join(timeout=1)

    print(f"Peak Usage : {max_mem - min_mem:.2f} MB")
    print(f"running time: {end_time - start_time:.4f} 秒")
    print(f"生成候选模式数量：{CanNum}")
    print(f"支持度计算次数：{sup_count}")
    print(f"模式匹配次数：{matching_count}")
    print(f"hawp number：{len(final_hawp)}")