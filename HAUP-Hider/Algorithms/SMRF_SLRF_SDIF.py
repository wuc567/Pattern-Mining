# -*- coding: utf-8 -*-
import sys
from copy import deepcopy
import copy
import math
import time
import json
from collections import defaultdict
import tracemalloc

def calculate_item_utility(item, tid, S_dict, utility_table):
    """计算某个item在某个transaction中的utility"""
    if item not in S_dict or len(S_dict[item][tid]) == 0:
        return 0
    return len(S_dict[item][tid]) * utility_table[item]


def is_pattern_contained(pattern, sid, S_dict):
    """
    检查序列模式pattern是否被sequence sid包含
    """
    if not pattern:
        return False, []

    first_item = pattern[0]
    if first_item not in S_dict or len(S_dict[first_item][sid]) == 0:
        return False, []

    if len(pattern) == 1:
        return True, [S_dict[first_item][sid][0]]

    matched_positions = []

    for i, item in enumerate(pattern):
        if item not in S_dict or len(S_dict[item][sid]) == 0:
            return False, []

        item_positions = S_dict[item][sid]

        if i == 0:
            matched_positions = [[pos] for pos in item_positions]
        else:
            new_matched = []
            for prev_match in matched_positions:
                last_pos = prev_match[-1]
                for pos in item_positions:
                    if pos > last_pos:
                        new_matched.append(prev_match + [pos])
                        break  # 只取第一个满足条件的位置(贪心策略)

            matched_positions = new_matched

            if not matched_positions:
                return False, []

    return True, matched_positions[0] if matched_positions else []


def calculate_pattern_utility(pattern, sid, S_dict, utility_table):
    """
    计算序列模式pattern在某个sequence中的utility
    """
    utility = 0
    for item in pattern:
        if item in S_dict and len(S_dict[item][sid]) > 0:
            utility += calculate_item_utility(item, sid, S_dict, utility_table)
    return utility


def calculate_total_utility(pattern, S_dict, utility_table, seqnum):
    """
    计算序列模式pattern在数据库中的总utility
    """
    total_util = 0
    for sid in range(seqnum):
        is_contained, _ = is_pattern_contained(pattern, sid, S_dict)
        if is_contained:
            seq_util = calculate_pattern_utility(pattern, sid, S_dict, utility_table)
            total_util += seq_util
    return total_util


def calculate_sequence_utility(sid, S_dict, utility_table):
    """计算某个sequence的总utility (transaction utility)"""
    utility = 0
    for item in S_dict:
        if len(S_dict[item][sid]) > 0:
            utility += len(S_dict[item][sid]) * utility_table[item]
    return utility


def delete_item(item, sid, S_dict):
    """删除某个item在某个sequence中的所有出现"""
    if item in S_dict and len(S_dict[item][sid]) > 0:
        S_dict[item][sid] = []


def decrease_item(item, sid, S_dict, utility_table, target_utility):
    """减少某个item在某个sequence中的quantity"""
    if item not in S_dict or len(S_dict[item][sid]) == 0:
        return

    current_utility = calculate_item_utility(item, sid, S_dict, utility_table)
    if current_utility <= target_utility:
        delete_item(item, sid, S_dict)
    else:
        new_quantity = target_utility // utility_table[item]
        if new_quantity <= 0:
            delete_item(item, sid, S_dict)
        else:
            S_dict[item][sid] = S_dict[item][sid][:new_quantity]

def calculate_RISU(S_dict, utility_table, sensitive_itemsets, seqnum):
    """
    计算Real Item Sensitive Utility (RISU)
    """
    sensitive_transactions = set()
    for itemset in sensitive_itemsets:
        for tid in range(seqnum):
            is_contained, _ = is_pattern_contained(itemset, tid, S_dict)
            if is_contained:
                sensitive_transactions.add(tid)

    sensitive_items = set()
    for itemset in sensitive_itemsets:
        sensitive_items.update(itemset)

    RISU = {}
    for item in sensitive_items:
        RISU[item] = 0
        for tid in sensitive_transactions:
            if item in S_dict and len(S_dict[item][tid]) > 0:
                RISU[item] += calculate_item_utility(item, tid, S_dict, utility_table)

    return RISU, sensitive_transactions


def calculate_sensitive_cover(sensitive_itemsets, S_dict, seqnum):
    """
    计算Sensitive Cover (SC)
    """
    item_SC = defaultdict(int)
    trans_SC = defaultdict(int)

    for itemset in sensitive_itemsets:
        for item in itemset:
            item_SC[item] += 1

        for tid in range(seqnum):
            is_contained, _ = is_pattern_contained(itemset, tid, S_dict)
            if is_contained:
                trans_SC[tid] += 1

    return item_SC, trans_SC


def calculate_non_sensitive_cover(sensitive_itemsets, non_sensitive_itemsets, S_dict, seqnum):
    """
    计算Non-Sensitive Cover (NSC)
    """
    item_NSC = defaultdict(int)
    trans_NSC = defaultdict(int)

    for itemset in non_sensitive_itemsets:
        for item in itemset:
            item_NSC[item] += 1

        for tid in range(seqnum):
            is_contained, _ = is_pattern_contained(itemset, tid, S_dict)
            if is_contained:
                trans_NSC[tid] += 1

    return item_NSC, trans_NSC


def calculate_transaction_weight(trans_SC, trans_NSC, seqnum):
    """
    计算transaction的权重
    """
    weights = {}
    for tid in range(seqnum):
        sc = trans_SC.get(tid, 0)
        nsc = trans_NSC.get(tid, 0)
        weights[tid] = sc / (nsc + 1)
    return weights


def weighted_sorting(sensitive_transactions, weights):
    """
    Weighted Sorting: 按权重降序排序敏感transactions
    """
    sorted_trans = sorted(sensitive_transactions,
                          key=lambda tid: weights.get(tid, 0),
                          reverse=True)
    return sorted_trans


# SMRF Algorithm
def SMRF_algorithm(S, utility_table, sensitive_itemsets, minutil, seqnum, non_sensitive_itemsets):
    """
    Selecting the Most Real item sensitive utility First (SMRF) Algorithm
    """
    S_new = deepcopy(S)
    modified_sequences = set()

    RISU, sensitive_transactions = calculate_RISU(S_new, utility_table, sensitive_itemsets, seqnum)

    victim_items = {}
    for itemset in sensitive_itemsets:
        max_risu = -1
        victim_item = None
        for item in itemset:
            if item in RISU and RISU[item] > max_risu:
                max_risu = RISU[item]
                victim_item = item
        victim_items[tuple(itemset)] = victim_item

    item_SC, trans_SC = calculate_sensitive_cover(sensitive_itemsets, S_new, seqnum)
    item_NSC, trans_NSC = calculate_non_sensitive_cover(sensitive_itemsets, non_sensitive_itemsets, S_new, seqnum)

    weights = calculate_transaction_weight(trans_SC, trans_NSC, seqnum)
    sorted_trans = weighted_sorting(sensitive_transactions, weights)

    sorted_itemsets = sorted(sensitive_itemsets,
                             key=lambda x: RISU.get(victim_items[tuple(x)], 0),
                             reverse=True)

    for itemset in sorted_itemsets:
        victim_item = victim_items[tuple(itemset)]

        current_utility = calculate_total_utility(itemset, S_new, utility_table, seqnum)
        diff = current_utility - int(minutil) + 1

        for tid in sorted_trans:
            if diff > 0:
                is_contained, _ = is_pattern_contained(itemset, tid, S_new)
                if is_contained:
                    victim_item_utility = calculate_item_utility(victim_item, tid, S_new, utility_table)

                    if victim_item_utility == 0:
                        continue

                    if diff >= victim_item_utility:
                        delete_item(victim_item, tid, S_new)
                        diff -= victim_item_utility
                        modified_sequences.add(tid)
                    else:
                        diu = math.ceil(diff / utility_table[victim_item])
                        current_quantity = len(S_new[victim_item][tid])
                        new_quantity = max(0, current_quantity - diu)
                        decrease_item(victim_item, tid, S_new, utility_table, new_quantity * utility_table[victim_item])
                        diff = 0
                        modified_sequences.add(tid)
            else:
                break

    return S_new, len(modified_sequences)


# SLRF Algorithm
def SLRF_algorithm(S, utility_table, sensitive_itemsets, minutil, seqnum, non_sensitive_itemsets):
    """
    Selecting the Least Real item sensitive utility First (SLRF) Algorithm
    """
    S_new = deepcopy(S)
    modified_sequences = set()

    RISU, sensitive_transactions = calculate_RISU(S_new, utility_table, sensitive_itemsets, seqnum)

    victim_items = {}
    for itemset in sensitive_itemsets:
        min_risu = float('inf')
        victim_item = None
        for item in itemset:
            if item in RISU and RISU[item] < min_risu:
                min_risu = RISU[item]
                victim_item = item
        victim_items[tuple(itemset)] = victim_item

    item_SC, trans_SC = calculate_sensitive_cover(sensitive_itemsets, S_new, seqnum)
    item_NSC, trans_NSC = calculate_non_sensitive_cover(sensitive_itemsets, non_sensitive_itemsets, S_new, seqnum)

    weights = calculate_transaction_weight(trans_SC, trans_NSC, seqnum)
    sorted_trans = weighted_sorting(sensitive_transactions, weights)

    sorted_itemsets = sorted(sensitive_itemsets,
                             key=lambda x: RISU.get(victim_items[tuple(x)], 0),
                             reverse=True)

    for itemset in sorted_itemsets:
        victim_item = victim_items[tuple(itemset)]
        current_utility = calculate_total_utility(itemset, S_new, utility_table, seqnum)
        diff = current_utility - int(minutil) + 1

        for tid in sorted_trans:
            if diff > 0:
                is_contained, _ = is_pattern_contained(itemset, tid, S_new)
                if is_contained:
                    victim_item_utility = calculate_item_utility(victim_item, tid, S_new, utility_table)

                    if victim_item_utility == 0:
                        continue

                    if diff >= victim_item_utility:
                        delete_item(victim_item, tid, S_new)
                        diff -= victim_item_utility
                        modified_sequences.add(tid)
                    else:
                        diu = math.ceil(diff / utility_table[victim_item])
                        current_quantity = len(S_new[victim_item][tid])
                        new_quantity = max(0, current_quantity - diu)
                        decrease_item(victim_item, tid, S_new, utility_table, new_quantity * utility_table[victim_item])
                        diff = 0
                        modified_sequences.add(tid)
            else:
                break

    return S_new, len(modified_sequences)


# SDIF Algorithm
def SDIF_algorithm(S, utility_table, sensitive_itemsets, minutil, seqnum, non_sensitive_itemsets):
    """
    Selecting the most Desirable Item First (SDIF) Algorithm
    """
    S_new = deepcopy(S)
    modified_sequences = set()

    RISU, sensitive_transactions = calculate_RISU(S_new, utility_table, sensitive_itemsets, seqnum)

    item_SC, trans_SC = calculate_sensitive_cover(sensitive_itemsets, S_new, seqnum)
    item_NSC, trans_NSC = calculate_non_sensitive_cover(sensitive_itemsets, non_sensitive_itemsets, S_new, seqnum)

    victim_items = {}
    for itemset in sensitive_itemsets:
        candidates = []
        for item in itemset:
            sc = item_SC.get(item, 0)
            nsc = item_NSC.get(item, 0)
            candidates.append((item, sc, nsc, RISU.get(item, 0)))

        max_sc = max(c[1] for c in candidates) if candidates else 0
        min_nsc = min(c[2] for c in candidates) if candidates else 0
        desirable = [c for c in candidates if c[1] >= max_sc and c[2] <= min_nsc]

        if len(desirable) >= 1:
            victim_item = min(desirable, key=lambda x: x[3])[0]
        else:
            victim_item = min(candidates, key=lambda x: (x[2], x[3]))[0]

        victim_items[tuple(itemset)] = victim_item

    weights = calculate_transaction_weight(trans_SC, trans_NSC, seqnum)
    sorted_trans = weighted_sorting(sensitive_transactions, weights)

    sorted_itemsets = sorted(sensitive_itemsets,
                             key=lambda x: RISU.get(victim_items[tuple(x)], 0),
                             reverse=True)

    for itemset in sorted_itemsets:
        victim_item = victim_items[tuple(itemset)]
        current_utility = calculate_total_utility(itemset, S_new, utility_table, seqnum)
        diff = current_utility - int(minutil) + 1

        for tid in sorted_trans:
            if diff > 0:
                is_contained, _ = is_pattern_contained(itemset, tid, S_new)
                if is_contained:
                    victim_item_utility = calculate_item_utility(victim_item, tid, S_new, utility_table)

                    if victim_item_utility == 0:
                        continue

                    if diff >= victim_item_utility:
                        delete_item(victim_item, tid, S_new)
                        diff -= victim_item_utility
                        modified_sequences.add(tid)
                    else:
                        diu = math.ceil(diff / utility_table[victim_item])
                        current_quantity = len(S_new[victim_item][tid])
                        new_quantity = max(0, current_quantity - diu)
                        decrease_item(victim_item, tid, S_new, utility_table, new_quantity * utility_table[victim_item])
                        diff = 0
                        modified_sequences.add(tid)
            else:
                break

    return S_new, len(modified_sequences)

# 指标计算
def nested_tuple(x):
    if isinstance(x, list):
        return tuple(nested_tuple(i) for i in x)
    return x
def flatten_pattern(pattern):
    return [item for itemset in pattern for item in itemset]
def normalize_pattern(p):
    if isinstance(p, str):
        try:
            p = eval(p)
        except:
            return p

    if isinstance(p, list):
        if p and isinstance(p[0], list):
            flat = []
            for item in p:
                if isinstance(item, list):
                    flat.extend(item)
                else:
                    flat.append(item)
            p = flat
        return str(p)

    return str(p)
def compute_dus(S_original, S_sanitized, utility_table, seq_num):
    """
    计算 DUS (Dataset Utility Similarity) 指标
    """

    def compute_dataset_utility(S_dict, utility_table, seq_num):
        """计算整个数据集的总效用"""
        total_utility = 0.0

        for sid in range(seq_num):
            seq_utility = 0.0
            for item in S_dict:
                if sid < len(S_dict[item]) and S_dict[item][sid]:
                    quantity = len(S_dict[item][sid])  # 该item在该序列中的出现次数
                    external_utility = utility_table.get(item, 1)
                    seq_utility += quantity * external_utility

            total_utility += seq_utility

        return total_utility

    utility_original = compute_dataset_utility(S_original, utility_table, seq_num)
    utility_sanitized = compute_dataset_utility(S_sanitized, utility_table, seq_num)

    dus = utility_sanitized / utility_original if utility_original > 0 else 1.0
    utility_loss = utility_original - utility_sanitized

    return {
        'dus': dus,
        'utility_original': utility_original,
        'utility_sanitized': utility_sanitized,
        'utility_loss': utility_loss,
        'utility_loss_percent': (utility_loss / utility_original * 100) if utility_original > 0 else 0.0
    }
def compute_metrics(sensitive_patterns, haups_before, haups_after):
    """
    计算 HF, MC, AC 指标
    """
    print("\n=== 模式标准化过程 ===")
    sen_normalized = [normalize_pattern(p) for p in sensitive_patterns]
    before_normalized = [normalize_pattern(p) for p in haups_before]
    after_normalized = [normalize_pattern(p) for p in haups_after]

    sen_set = set(sen_normalized)
    before_set = set(before_normalized)
    after_set = set(after_normalized)

    print(f"\n=== 集合统计 ===")
    print(f"敏感模式集合大小: {len(sen_set)}")
    print(f"清洗前HAUP集合大小: {len(before_set)}")
    print(f"清洗后HAUP集合大小: {len(after_set)}")

    sen_in_before = sen_set & before_set
    sen_in_after = sen_set & after_set

    print(f"\n=== 敏感模式分布 ===")
    print(f"敏感模式总数: {len(sen_set)}")
    print(f"敏感模式在清洗前HAUP中的数量: {len(sen_in_before)}")
    print(f"敏感模式在清洗后HAUP中的数量: {len(sen_in_after)}")

    # HF (Hiding Failure)
    if len(sen_in_before) > 0:
        HF = len(sen_in_after) / len(sen_in_before)
    else:
        HF = 0.0

    print(f"\n=== HF 计算 ===")
    print(f"HF = {len(sen_in_after)} / {len(sen_in_before)} = {HF:.4f}")

    # MC (Missing Cost)
    non_sen_before = before_set - sen_set
    non_sen_after = after_set - sen_set
    lost_non_sen = non_sen_before - after_set

    if len(non_sen_before) > 0:
        MC = len(lost_non_sen) / len(non_sen_before)
    else:
        MC = 0.0

    print(f"\n=== MC 计算 ===")
    print(f"清洗前非敏感模式数: {len(non_sen_before)}")
    print(f"清洗后非敏感模式数: {len(non_sen_after)}")
    print(f"丢失的非敏感模式数: {len(lost_non_sen)}")
    print(f"MC = {len(lost_non_sen)} / {len(non_sen_before)} = {MC:.4f}")

    # AC (Artificial Cost)
    new_patterns = after_set - before_set

    if len(after_set) > 0:
        AC = len(new_patterns) / len(after_set)
    else:
        AC = 0.0

    print(f"\n=== AC 计算 ===")
    print(f"清洗后新增模式数: {len(new_patterns)}")
    print(f"清洗后总模式数: {len(after_set)}")
    print(f"AC = {len(new_patterns)} / {len(after_set)} = {AC:.4f}")

    #if len(new_patterns) > 0:
        #print(f"新增模式样例: {list(new_patterns)[:3]}")

    print("\n" + "=" * 50)
    print("==== Metric Summary ====")
    print("=" * 50)
    print(f"敏感模式总数: {len(sen_set)}")
    print(f"  - 清洗前在HAUP中: {len(sen_in_before)}")
    print(f"  - 清洗后在HAUP中: {len(sen_in_after)}")
    print(f"  - 成功隐藏数量: {len(sen_in_before) - len(sen_in_after)}")
    print(f"\n非敏感模式:")
    print(f"  - 清洗前数量: {len(non_sen_before)}")
    print(f"  - 清洗后数量: {len(non_sen_after)}")
    print(f"  - 丢失数量: {len(lost_non_sen)}")
    print(f"  - 新增数量: {len(new_patterns)}")
    print(f"\n性能指标:")
    print(f"  HF (Hiding Failure)  = {HF:.4f}  (越低越好, 0为完美)")
    print(f"  MC (Missing Cost)    = {MC:.4f}  (越低越好, 0为无损失)")
    print(f"  AC (Artificial Cost) = {AC:.4f}  (越低越好, 0为无新增)")
    print("=" * 50)
    return {
        "HF": HF,
        "MC": MC,
        "AC": AC,
        "sensitive_total": len(sen_set),
        "sensitive_before": len(sen_in_before),
        "sensitive_after": len(sen_in_after),
        "sensitive_hidden": len(sen_in_before) - len(sen_in_after),
        "non_sensitive_before": len(non_sen_before),
        "non_sensitive_after": len(non_sen_after),
        "non_sensitive_lost": len(lost_non_sen),
        "patterns_new": len(new_patterns)
    }
def run_sanitization_from_json(json_file, algorithm="SMRF", output_file="privacy_output.json"):
    """
    从挖掘结果JSON文件读取数据,执行清洗算法(SMRF/SLRF/SDIF),
    然后对清洗后的位置字典重新挖掘高平均效用模式。
    """
    print(f"从 {json_file} 读取挖掘结果...")
    with open(json_file, "r", encoding="utf-8") as f:
        mine_cache = json.load(f)

    sensitive_patterns = [
        ['10', '10', '10', '10', '10', '10']

    ]

    S = mine_cache["S"]
    seq_num = mine_cache["seq_num"]
    sort_item = mine_cache["sort_item"]
    utility_table = mine_cache["Utility"]
    minutil = mine_cache["minau"]
    S_original = copy.deepcopy(S)
    original_patterns = [p["pattern"] for p in mine_cache["patterns"]]

    print(f"已加载数据库:序列数={seq_num},项数={len(S)},敏感模式={len(sensitive_patterns)}")
    print(f"原始 AUNP 数量: {len(original_patterns)}")

    non_sensitive_itemsets = [p for p in original_patterns if p not in sensitive_patterns]

    start = time.time()

    if algorithm == "SMRF":
        print("执行 SMRF 清洗中...")
        S_cleaned, modified_count = SMRF_algorithm(S, utility_table, sensitive_patterns, minutil, seq_num, non_sensitive_itemsets)
    elif algorithm == "SLRF":
        print("执行 SLRF 清洗中...")
        S_cleaned, modified_count =SLRF_algorithm (S, utility_table, sensitive_patterns, minutil, seq_num, non_sensitive_itemsets)
    elif algorithm == "SDIF":
        print("执行 SDIF 清洗中...")
        S_cleaned, modified_count=SDIF_algorithm (S, utility_table, sensitive_patterns, minutil, seq_num, non_sensitive_itemsets)
    else:
        raise ValueError("未知算法类型:" + algorithm)

    end = time.time()
    print(f"清洗完成，用时 {end - start:.3f}s")
    print(f"清洗完成，用时 {(end - start) * 1000}ms")


    print(f"修改的序列数: {modified_count}")

    print("\n" + "=" * 70)
    print("=" * 70)
    dus_result = compute_dus(S_original, S_cleaned, utility_table, seq_num)
    print(f"原始数据集总效用: {dus_result['utility_original']:.2f}")
    print(f"清洗后数据集总效用: {dus_result['utility_sanitized']:.2f}")
    print(f"效用损失: {dus_result['utility_loss']:.2f} ({dus_result['utility_loss_percent']:.2f}%)")
    print(f"DUS值: {dus_result['dus']:.4f} ({dus_result['dus'] * 100:.2f}%)")
    print("=" * 70)

    print("对清洗后的位置字典重新挖掘 HAUP ...")

    try:
        from HUP-Miner import PatternMiner
        miner = PatternMiner()
        cleaned_results = miner.mine_patterns_from_S(
            S=S_cleaned,
            seq_num=seq_num,
            sort_item=sort_item,
            utility_dict=utility_table,
            min_utility_threshold=minutil
        )
        print(f"清洗后 AUNP 数量: {cleaned_results['aunp_count']}")
        cleaned_patterns = cleaned_results['aunp_patterns']
    except ImportError:
        print("无法导入HUP-Miner,跳过重新挖掘步骤")
        cleaned_patterns = []

    # 计算指标
    print("计算评估指标 HF / MC / AC ...")
    metrics = compute_metrics(
        sensitive_patterns,
        original_patterns,
        cleaned_patterns
    )
    print(f"DUS值: {dus_result['dus']:.4f} ({dus_result['dus'] * 100:.2f}%)")

    result = {
        "algorithm": algorithm,
        "runtime": end - start,
        #"memory_usage": max(a) - min(a),
        "modified_sequences": modified_count,
        "dus": dus_result,
        "metrics": metrics,
        "haup_before_count": len(original_patterns),
        "haup_after_count": len(cleaned_patterns)
    }

    print("=" * 70)

    return result

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SMRF/SLRF/SDIF privacy preserving algorithms")
    parser.add_argument("--json", type=str, required=True, help="输入挖掘结果JSON文件路径")
    parser.add_argument("--algo", type=str, default="SMRF",
                        choices=["SMRF", "SLRF", "SDIF"], help="选择清洗算法")
    parser.add_argument("--output", type=str, default="privacy_output.json", help="输出文件路径")

    args = parser.parse_args()

    run_sanitization_from_json(args.json, args.algo, args.output)