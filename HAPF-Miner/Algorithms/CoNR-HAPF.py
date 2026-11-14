import time
from pro import read_txt
from collections import defaultdict
# from utility import utility_table6
from shiyan_utility import (
    utility_table1,
    utility_table2,
    utility_table3,
    utility_table4,
    utility_table5,
    utility_table6,
    utility_table7
)
import psutil
import os
import threading
import math
import sys



CanNum = 0
matching_count= 0
sup_count=0

I_PSD = {"suf": defaultdict(set)}
S_PSD = {"suf": defaultdict(set)}
ItemMaskCache = {}
PatternSeqCache = defaultdict(set)

utility_table = None
#
# utility_table = {
#     'a': 1,
#     'b': 2,
#     'c': 4,
#     'd': 5,
#     'e': 3,
# }

def onepattern(seqs):
    ItemS = {}
    SeqNum = len(seqs)

    all_timestamps = []
    for seq in seqs:
        for itemset, ts in seq:
            ts = int(ts)
            all_timestamps.append(ts)
    if not all_timestamps:
        return ItemS, [], [0.0] * SeqNum, [0] * SeqNum
    n = max(all_timestamps)
    theta = 2 / n
    # print(theta)
    seq_forget = [0.0] * (n + 1)
    for t in range(1, n + 1):
        seq_forget[t] = math.exp(-theta * (n - t))
    seq_max_forget = [0.0] * SeqNum
    seq_max_ts = [0] * SeqNum
    for seq_idx, seq in enumerate(seqs):
        if not seq:
            continue
        cur_max_ts = max(int(ts) for itemset, ts in seq)
        seq_max_ts[seq_idx] = cur_max_ts
        max_forget = 0.0
        for itemset, ts in seq:
            ts = int(ts)
            forget_factor = seq_forget[ts]
            if forget_factor > max_forget:
                max_forget = forget_factor
            bit_pos = cur_max_ts - ts
            bit_weight = 1 << bit_pos

            for item in itemset:
                item_key = ((item,),)

                if item_key not in ItemS:
                    ItemS[item_key] = [0] * SeqNum

                ItemS[item_key][seq_idx] |= bit_weight

        seq_max_forget[seq_idx] = max_forget
    # print( seq_forget)
    # print(seq_forget[7])
    return ItemS, seq_forget, seq_max_forget, seq_max_ts

def non_sup_one(r, ItemS, seq_max_forget):
    masks = ItemS.get(r)
    if masks is None:
        return 0.0, masks
    sup_tk = 0.0
    for t, mask in enumerate(masks):
        if mask:
            sup_tk += mask.bit_count() * seq_max_forget[t]

    return sup_tk, masks


def non_sup(pat, ItemS, SeqNum, seq_max_forget):
    global sup_count

    pattern_len = len(pat)
    c = pat[:-1]
    e = pat[-1]
    M_p = [0] * SeqNum
    # 获取后缀bitmap
    e_masks = []
    for item in e:
        key = ((item,),)
        if key in ItemMaskCache:
            masks = ItemMaskCache[key]
        else:
            masks = ItemS.get(key, [0] * SeqNum)
            ItemMaskCache[key] = masks
        e_masks.append(masks)

    active_seq = None
    for masks in e_masks:
        seqs = {
            i for i, m in enumerate(masks)
            if m
        }
        if active_seq is None:
            active_seq = seqs
        else:
            active_seq &= seqs

    if not active_seq:
        return 0.0, M_p

    # 前缀模式出现序列限制
    if pattern_len > 1:
        c_masks = ItemS.get(c)
        if c_masks:
            active_seq &= {i for i, m in enumerate(c_masks) if m }

    sup_tk = 0.0
    for t in active_seq:
        tk_t = seq_max_forget[t]
        # 后缀项集内部匹配
        mask2 = None
        for masks in e_masks:
            val = masks[t]
            if mask2 is None:
                mask2 = val
            else:
                sup_count += 1
                mask2 &= val
        if not mask2:
            continue
        # 长度1模式
        if pattern_len == 1:
            mask = mask2
        else:
            mask1 = ItemS[c][t] >> 1
            mask = 0
            while mask1 and mask2:
                sup_count += 1
                temp = mask1 & mask2
                if temp:
                    mask |= temp
                    mask1 ^= temp
                    mask2 ^= temp
                    if mask1.bit_length() < (
                        mask2 & -mask2
                    ).bit_length():
                        break
                else:
                    mask1 >>= 1
        M_p[t] = mask
        seq_sup = mask.bit_count()
        if seq_sup:
            sup_tk += seq_sup * tk_t

    ItemS[pat] = M_p
    PatternSeqCache[pat] = {i for i, m in enumerate(M_p) if m }

    return sup_tk, M_p

def non_fsup(M_p, seq_forget,seq_max_ts):

    fsup_p_D = 0.0
    for t in range(SeqNum):
        temp = M_p[t]
        cur_max_ts = seq_max_ts[t]
        cur_ts = cur_max_ts + 1
        while temp:
            lowest_bit = temp & -temp
            ts = cur_ts - lowest_bit.bit_length()
            fsup_p_D += seq_forget[ts]
            temp ^= lowest_bit

    return fsup_p_D


def generate_two_len(ItemS,seq_forget,seq_max_forget,max_len,seq_max_ts,minwau):
    global I_PSD, S_PSD, CanNum, SeqNum, utility_table,matching_count
    util_get = utility_table.get
    HAWP = []
    H1 = []
    H2 = []
    I_connection_patterns = []
    S_connection_patterns = []
    #生成长度为1的模式
    sorted_items = sorted(k[0][0] for k in ItemS)
    # print(sorted_items)
    max_utility = max(utility_table.values())
    # print( max_utility )
    one_Umax = (max_len - 1) * max_utility
    two_Umax = (max_len - 2) * max_utility
    for x in sorted_items:
        CanNum += 1
        pattern = ((x,),)
        # print(pattern)
        sup_tk, masks = non_sup_one(pattern,ItemS,seq_max_forget)
        # print( sup_tk )

        utility_sum = util_get(x, 0)
        aub = (utility_sum + one_Umax) * sup_tk / max_len
        if aub >= minwau:
            H1.append(x)
            fsup = non_fsup(masks, seq_forget, seq_max_ts)
            hawu = utility_sum * fsup
            if hawu >= minwau:
                HAWP.append(pattern)
                # print(hawu)
        # print(utility_sum)
        # print(hawu)
    h1_len = len(H1)
    # print(H1)
    for i in range(h1_len):  #I-连接
        a = H1[i]
        ua = util_get(a, 0)
        for j in range(i + 1, h1_len):
            b = H1[j]
            pattern = ((a, b),)
            # print(pattern)
            CanNum += 1
            matching_count += 1
            sup_tk, M_p = non_sup(pattern,ItemS,SeqNum,seq_max_forget)

            if sup_tk <= 0:
                continue
            utility_sum = ua + util_get(b, 0)
            aub = (utility_sum + two_Umax) * sup_tk / max_len
            # print(aub)
            if aub >= minwau:
                H2.append(pattern)
                I_connection_patterns.append((a, b))
                fsup = non_fsup(M_p, seq_forget, seq_max_ts)
                hawu = utility_sum * fsup / 2
                # print( hawu)
                if hawu >= minwau:
                    HAWP.append(pattern)
    # 更新 I_PSD
    Isuf = I_PSD["suf"]

    for a, b in I_connection_patterns:
        key = (a,)
        Isuf[key].add(b)
        # ub = util_get(b, 0)
        # if ub > Imeu[key]:
        #     Imeu[key] = ub
    # 长度2 S连接 [a][b]
    for a in H1:
        ua = util_get(a, 0)
        for b in H1:
            pattern = ((a,), (b,))
            # print(pattern)
            CanNum += 1
            matching_count += 1
            sup_tk, M_p = non_sup(pattern,ItemS,SeqNum,seq_max_forget)
            # print( sup_tk)

            if sup_tk <= 0:
                continue
            utility_sum = ua + util_get(b, 0)
            aub = (utility_sum + two_Umax) * sup_tk / max_len
            # print(aub)
            if aub >= minwau:
                H2.append(pattern)
                S_connection_patterns.append((a, b))
                fsup = non_fsup(M_p, seq_forget, seq_max_ts)
                hawu = utility_sum * fsup / 2
                # print(hawu)
                if hawu >= minwau:
                    HAWP.append(pattern)
                    # print(hawu)


    # 更新 S_PSD
    Ssuf = S_PSD["suf"]
    # Smeu = S_PSD["meu"]
    for a, b in S_connection_patterns:
        key = (a,)
        Ssuf[key].add(b)
        # ub = util_get(b, 0)
        # if ub > Smeu[key]:
        #     Smeu[key] = ub
    # print(I_PSD)
    # print(S_PSD)
    # print(H2)
    return H2, HAWP, I_PSD, S_PSD

def join_with_pruning(p, t):
    global  CanNum,matching_count


    # 判断是 I-连接 条件：t 的最后一个项集长度 >=2
    last_item = t[-1][-1]
    key = (p[0][0],)

    matching_count += 1
    if len(t[-1]) >= 2:
        # key = tuple(p[0][0])
        if len(p) == 1:
            if last_item not in I_PSD["suf"][key]:  # 剪枝2
                return None
        else:

            if last_item not in S_PSD["suf"][key]:   #剪枝2
                return None

        # I-连接：追加到最后一个项集
        r = p[:-1] + (
            p[-1] + (last_item,),
        )

        CanNum += 1
        # print(CanNum)
        # print(r)
    else:

        if key not in S_PSD["suf"] or last_item not in S_PSD["suf"][key]:  # 剪枝3
            return None
        # S-连接：新增一个项集
        r = p + (
            (last_item,),
        )
        CanNum += 1
        # print(CanNum)
        # print(r)

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



def hawp_miner(ItemS, seq_forget, seq_max_forget, seq_max_ts, max_len, minwau):

    global I_PSD, S_PSD, CanNum, SeqNum,utility_table, matching_count, sup_count

    util_get = utility_table.get
    Umax = max(utility_table.values())

    H2, final_HAWP, I_PSD, S_PSD = generate_two_len(
        ItemS, seq_forget, seq_max_forget,
        max_len, seq_max_ts, minwau
    )
    H_current = H2.copy()
    # 缓存模式效用
    pattern_utility = {}
    for p in H_current:
        pattern_utility[p] = sum(util_get(item, 0) for itemset in p
            for item in itemset
        )
    current_m = 2
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
                    sup_tk, M_p = non_sup(
                        r, ItemS, SeqNum, seq_max_forget
                    )
                    if sup_tk == 0:
                        continue
                    utility_sum = (p_utility +util_get(t[-1][-1], 0))
                    aub = (utility_sum + remain_Umax) * sup_tk / max_len
                    if aub < minwau:
                        continue
                    H_next.append(r)
                    ItemS[r] = M_p
                    pattern_utility[r] = utility_sum
                    fsup = non_fsup(M_p, seq_forget, seq_max_ts)
                    hawu = utility_sum * fsup / pattern_len
                    if hawu >= minwau:
                        final_HAWP.append(r)

        print(f"\n✅ H_{pattern_len}候选模式数量：{len(H_next)}")
        H_current = H_next
        current_m += 1
        if not H_current:
            print(f"\n🛑 H_{current_m}为空，算法结束！")
            break

    return final_HAWP,I_PSD,S_PSD,CanNum,sup_count,matching_count


if __name__ == "__main__":

    # path1 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\supermarket_按天划分.txt'
    # path2 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\car_按天划分.txt'
    # path3 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\beauty_按天划分.txt'
    # path4 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\2026ecommerce_按天划分.txt'
    # path5 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\UserBehavior_按天划分.txt'
    # path6 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\Auto Sales_按天划分.txt'
    # path7 = r'E:\PythonProject\HAFP-Miner\按天划分数据集\SDB8 Credite.txt'
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
            "minwau": 950
        }

    }

    # dataset_configs = {
    #     1: {
    #         "name": "car_650",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 650
    #     },
    #     2: {
    #         "name": "car_750",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 750
    #     },
    #     3: {
    #         "name": "car_850",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 850
    #     },
    #     4: {
    #         "name": "car_950",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 950
    #     },
    #     5: {
    #         "name": "car_1050",
    #         "path": path2,
    #         "utility_table": utility_table2,
    #         "minwau": 1050
    #     },
    #     6: {
    #         "name": "car_1150",
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
        ItemS, seq_forget, seq_max_forget, seq_max_ts = onepattern(sdb)

        max_len = 10
        return hawp_miner(ItemS, seq_forget, seq_max_forget, seq_max_ts, max_len, minwau)


    monitoring = True
    monitor_thread = threading.Thread(
        target=monitor_memory,
        daemon=True
    )
    monitor_thread.start()
    start_time = time.time()
    final_hawp, I_PSD, S_PSD, CanNum, sup_count, matching_count = run_mining()
    end_time = time.time()
    monitoring = False
    monitor_thread.join(timeout=1)
    # print(f"Min Memory : {min_mem:.2f} MB")
    # print(f"Max Memory : {max_mem:.2f} MB")
    print(f"Peak Usage : {max_mem - min_mem:.2f} MB")
    print(f"running time: {end_time - start_time:.4f} 秒")
    print(f"生成候选模式数量：{CanNum}")
    print(f"支持度计算次数：{sup_count}")
    print(f"模式匹配次数：{matching_count}")
    print(f"hawp number：{len(final_hawp)}")

    # for p in final_hawp:
    #     print(p)








