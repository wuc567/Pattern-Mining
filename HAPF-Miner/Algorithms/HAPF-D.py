import time
from pro import read_txt
from collections import defaultdict
import psutil
import os
import threading
import math
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
matching_count= 0
sup_count=0
HAWP=[]

utility_table = None

# utility_table = {

#     # 'a': 1,
#     # 'b': 2,
#     # 'c': 4,
#     # 'd': 5,
#     # 'e': 3,
# }

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
    global sup_count

    i = j = 0
    out = []
    la, lb = len(a), len(b)

    while i < la and j < lb:
        sup_count += 1
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

    list3 = {}
    sup_tk = 0.0

    for seq_idx, L1, L2 in _iter_common_sequences(list1, list2):
        result = _intersect_two_sorted(L1, L2)
        if result:
            list3[seq_idx] = result
            sup_tk += len(result) * seq_max_forget[seq_idx]

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


def non_sup(pat, ItemS, SeqNum, seq_max_forget):

    if pat in ItemS:
        list3 = ItemS[pat]
        sup_tk = 0.0

        for seq_idx, positions in list3.items():
            sup_tk += len(positions) * seq_max_forget[seq_idx]

        return sup_tk, list3

    c, d = get_cd(pat)

    if c not in ItemS:
        non_sup(c, ItemS, SeqNum, seq_max_forget)

    if d not in ItemS:
        non_sup(d, ItemS, SeqNum, seq_max_forget)

    p_list = ItemS.get(c)
    t_list = ItemS.get(d)

    if p_list is None or t_list is None:
        list3 = {}
        ItemS[pat] = list3
        return 0.0, list3

    if len(pat) == 1:
        list3, sup_tk = Matching_I(
            p_list, t_list, seq_max_forget
        )
    else:
        list3, sup_tk = Matching_S(
            pat, p_list, t_list, seq_max_forget
        )

    ItemS[pat] = list3

    return sup_tk, list3


def non_fsup(list3, seq_forget):
    fsup = 0.0
    for positions in list3.values():
        for pos in positions:
            fsup += seq_forget[pos]
    return fsup


def get_cd(pat):
    last = pat[-1][:-1]
    if len(last):
        c = pat[:-1] + (last,)
    else:
        c = pat[:-1]
    first = pat[0][1:]
    if len(first):
        d = (first,) + pat[1:]
    else:
       d = pat[1:]

    return c, d


def generate_two_len(H1, ItemS, seq_forget, seq_max_forget, max_len, minwau):
    global CanNum, matching_count

    util_get = utility_table.get
    H2 = []

    max_utility = max(utility_table.values())
    two_Umax = (max_len - 2) * max_utility
    h1_len = len(H1)

    # I-extension: (a b)
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

            list3, sup_tk = Matching_I(
                ItemS[a_pattern], ItemS[b_pattern], seq_max_forget
            )

            if sup_tk <= 0:
                continue

            utility_sum = ua + util_get(b, 0)
            aub = (utility_sum + two_Umax) * sup_tk / max_len

            if aub >= minwau:
                H2.append(pattern)
                ItemS[pattern] = list3

                fsup = non_fsup(list3, seq_forget)
                hawu = utility_sum * fsup / 2

                if hawu >= minwau:
                    HAWP.append(pattern)


    # S-extension: (a)(b)
    for a_pattern in H1:
        a = a_pattern[0][0]
        ua = util_get(a, 0)

        for b_pattern in H1:
            b = b_pattern[0][0]
            pattern = ((a,), (b,))

            CanNum += 1
            matching_count += 1

            list3, sup_tk = Matching_S(
                pattern, ItemS[a_pattern], ItemS[b_pattern], seq_max_forget
            )

            if sup_tk <= 0:
                continue

            utility_sum = ua + util_get(b, 0)
            aub = (utility_sum + two_Umax) * sup_tk / max_len

            if aub >= minwau:
                H2.append(pattern)
                ItemS[pattern] = list3

                fsup = non_fsup(list3, seq_forget)
                hawu = utility_sum * fsup / 2

                if hawu >= minwau:
                    HAWP.append(pattern)


    return H2, HAWP, ItemS



def S_join_dfs(p, H1, ItemS, seq_forget,seq_max_forget ,minwau, max_len, current_depth=2):
    global  CanNum, final_HAWP,matching_count

    if current_depth >= max_len:
        return

    for j in range(len(H1)):
        # H1[j] 的结构是 ((item,),)，取出真正的 item
        t = H1[j][0][0]
        r = p + ((t,),)
        matching_count += 1
        CanNum += 1
        new_depth = current_depth + 1
        # c, d = get_cd(r)
        sup_tk,list3 = non_sup(r, ItemS, SeqNum, seq_max_forget)

        if sup_tk == 0:
            continue
        utility_sum = 0
        for itemset in r:
            for item in itemset:
                utility_sum += utility_table.get(item, 0)

        Umax = max(utility_table.values())
        aub = (utility_sum + (max_len - new_depth) * Umax) * sup_tk / max_len

        if aub >= minwau:
            # print(aub)
            fsup = non_fsup(list3, seq_forget)
            hawu = utility_sum * fsup / new_depth
            if hawu >= minwau:
                # print(hawu)
                final_HAWP.append(r)
            S_join_dfs(r, H1, ItemS, seq_forget, seq_max_forget, minwau, max_len, new_depth)
            I_join_dfs(r, H1, ItemS, seq_forget, seq_max_forget, minwau, max_len, new_depth)



    return


def I_join_dfs(p, H1, ItemS, seq_forget, seq_max_forget,minwau, max_len, current_depth=2):
    global  CanNum, final_HAWP,matching_count
    if current_depth >= max_len:
        return
    last_item_p = p[-1][-1]
    for j in range(len(H1)):
        # H1[j] 的结构是 ((item,),)，取出真正的 item
        last_item = H1[j][0][0]
        matching_count += 1
        if last_item_p is not None and last_item > last_item_p:
            h = p[:-1] + (
                p[-1] + (last_item,),
            )
            CanNum += 1

            new_depth = current_depth + 1
            # print(new_depth)
            # c, d = get_cd(h)
            sup_tk, list3 = non_sup(h, ItemS, SeqNum, seq_max_forget)

            if sup_tk == 0:
                continue
            utility_sum = 0
            for itemset in h:
                for item in itemset:
                    utility_sum += utility_table.get(item, 0)

            Umax = max(utility_table.values())
            aub = (utility_sum + (max_len - new_depth) * Umax) * sup_tk / max_len
            # print(aub)
            if aub >= minwau:
                # print(aub)
                fsup = non_fsup(list3, seq_forget)
                hawu = utility_sum * fsup / new_depth
                if hawu >= minwau:
                    # print(hawu)
                    final_HAWP.append(h)
                S_join_dfs(h, H1, ItemS, seq_forget, seq_max_forget,minwau, max_len, new_depth)
                I_join_dfs(h, H1, ItemS, seq_forget, seq_max_forget, minwau, max_len, new_depth)



    return


def hawp_miner( seq_forget, seq_max_forget,max_len ,minwau):
    global  CanNum, SeqNum, utility_table, final_HAWP,matching_count,sup_count

    final_HAWP = []
    H1, HAWP, ItemS = Mine_ItemS(
        seq_forget, seq_max_forget, max_len, minwau
    )
    H2, HAWP, ItemS = generate_two_len(
        H1, ItemS, seq_forget, seq_max_forget, max_len, minwau
    )

    final_HAWP.extend(HAWP)
    for pattern in H2:
        # print(f"\n{'=' * 50}")
        # print(f"开始处理模式: {pattern}")
        # print(f"{'=' * 50}")
        current_depth = 2
        # print(f"\n--- 从模式 {pattern} (深度{current_depth}) 生成第{current_depth + 1}层 ---")

        S_join_dfs(pattern, H1, ItemS, seq_forget, seq_max_forget,minwau, max_len, current_depth)
        I_join_dfs(pattern, H1, ItemS, seq_forget, seq_max_forget,minwau, max_len, current_depth)

    return final_HAWP, CanNum,matching_count,sup_count


if __name__ == "__main__":

    path1 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\supermarket_按天划分.txt'
    path2 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分.txt'
    path3 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\beauty_按天划分.txt'
    path4 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\2026ecommerce_按天划分.txt'
    path5 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\UserBehavior_按天划分.txt'
    path6 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\Auto Sales_按天划分.txt'
    path7 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\SDB8 Credite.txt'

    # 每个数据集对应参数

    dataset_configs = {
        1: {
            "name": "supermarket",
            "path": path1,
            "utility_table": utility_table1,
            "minwau": 9000
        },
        2: {
            "name": "car",
            "path": path2,
            "utility_table": utility_table2,
            "minwau": 950
        },
        3: {
            "name": "beauty",
            "path": path3,
            "utility_table": utility_table3,
            "minwau": 300
        },
        4: {
            "name": "2026ecommerce",
            "path": path4,
            "utility_table": utility_table4,
            "minwau": 25000
        },
        5: {
            "name": "UserBehavior",
            "path": path5,
            "utility_table": utility_table5,
            "minwau": 8000
        },
        6: {
            "name": "Auto Sales",
            "path": path6,
            "utility_table": utility_table6,
            "minwau": 2500
        },
        7: {
            "name": "SDB8 Credite",
            "path": path7,
            "utility_table": utility_table7,
            "minwau": 15000
        }
    }

    # path2 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分.txt'
    # path2_2 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_2.txt'
    # path2_3 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_3.txt'
    # path2_4 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_4.txt'
    # path2_5 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_5.txt'
    # path2_6 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_6.txt'
    # path2_7 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_7.txt'
    # path2_8 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分_8.txt'
    #
    # dataset_configs = {
    #     1: {
    #         "name": "car",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 650
    #     },
    #     2: {
    #         "name": "car",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 750
    #     },
    #     3: {
    #         "name": "car",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 850
    #     },
    #     4: {
    #         "name": "car",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 1050
    #     },
    #     5: {
    #         "name": "car",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 1150
    #     }
    #
    # }

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
    final_hawp, CanNum, matching_count, sup_count = run_mining()
    end_time = time.time()
    monitoring = False
    monitor_thread.join(timeout=1)

    print(f"Peak Usage : {max_mem - min_mem:.2f} MB")
    print(f"running time: {end_time - start_time:.4f} 秒")
    print(f"生成候选模式数量：{CanNum}")
    print(f"支持度计算次数：{sup_count}")
    print(f"模式匹配次数：{matching_count}")
    print(f"hawp number：{len(final_hawp)}")