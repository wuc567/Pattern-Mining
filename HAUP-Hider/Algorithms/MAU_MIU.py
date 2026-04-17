# -*- coding: utf-8 -*-
import sys
from copy import deepcopy
import copy
import math
import time
import json
from collections import defaultdict
import tracemalloc


def calculate_item_utility(item, sid, S_dict, utility_table):
    """计算某个item在某个sequence中的utility"""
    if item not in S_dict or len(S_dict[item][sid]) == 0:
        return 0
    return len(S_dict[item][sid]) * utility_table[item]


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
                        break

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


def build_index_table(sensitive_patterns, S_dict, seqnum):
    """
    构建索引表:每个敏感序列模式对应哪些sequences包含它
    """
    index_table = {}
    for pattern in sensitive_patterns:
        index_table[tuple(pattern)] = []
        for sid in range(seqnum):
            is_contained, _ = is_pattern_contained(pattern, sid, S_dict)
            if is_contained:
                index_table[tuple(pattern)].append(sid)
    return index_table


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


# MSU-MAU 算法
def MSU_MAU_position(S, utility_table, sensitive_itemsets, minutil, seqnum):
    """
    Maximum Sensitive Utility-MAximum item Utility (MSU-MAU) Algorithm
    """
    S_new = deepcopy(S)
    modified_sequences = set()

    index_table = build_index_table(sensitive_itemsets, S_new, seqnum)

    sorted_shuis = sorted(sensitive_itemsets, key=lambda x: len(x), reverse=True)

    iteration = 0
    while sorted_shuis:
        iteration += 1
        current_shui = sorted_shuis[0]

        current_utility = calculate_total_utility(current_shui, S_new, utility_table, seqnum)
        du = current_utility - int(minutil) + 1

        if du <= 0:
            sorted_shuis.remove(current_shui)
            continue

        projected_sids = index_table.get(tuple(current_shui), [])
        if not projected_sids:
            sorted_shuis.remove(current_shui)
            continue

        max_seq_utility = -1
        victim_sid = None
        for sid in projected_sids:
            seq_util = calculate_sequence_utility(sid, S_new, utility_table)
            if seq_util > max_seq_utility:
                max_seq_utility = seq_util
                victim_sid = sid

        if victim_sid is None:
            sorted_shuis.remove(current_shui)
            continue

        max_item_utility = -1
        victim_item = None
        for item in current_shui:
            if item in S_new and len(S_new[item][victim_sid]) > 0:
                item_util = calculate_item_utility(item, victim_sid, S_new, utility_table)
                if item_util > max_item_utility:
                    max_item_utility = item_util
                    victim_item = item

        if victim_item is None:
            sorted_shuis.remove(current_shui)
            continue

        if max_item_utility < du:
            current_quantity = len(S_new[victim_item][victim_sid])
            delete_item(victim_item, victim_sid, S_new)
            modified_sequences.add(victim_sid)
        else:
            current_quantity = len(S_new[victim_item][victim_sid])
            target_utility = max_item_utility - du
            decrease_item(victim_item, victim_sid, S_new, utility_table, target_utility)
            modified_sequences.add(victim_sid)
            new_quantity = len(S_new[victim_item][victim_sid])

        index_table = build_index_table(sorted_shuis, S_new, seqnum)

        current_utility_after = calculate_total_utility(current_shui, S_new, utility_table, seqnum)
        if current_utility_after < int(minutil):
            sorted_shuis.remove(current_shui)

    return S_new, len(modified_sequences)


# MSU-MIU 算法
def MSU_MIU_position(S, utility_table, sensitive_itemsets, minutil, seqnum):
    """
    Maximum Sensitive Utility-MInimum item Utility (MSU-MIU) Algorithm
    """
    S_new = deepcopy(S)
    modified_sequences = set()

    for idx, current_shui in enumerate(sensitive_itemsets):

        current_utility = calculate_total_utility(current_shui, S_new, utility_table, seqnum)
        du = current_utility - int(minutil) + 1

        if du <= 0:
            continue

        index_table = build_index_table([current_shui], S_new, seqnum)
        projected_sids = index_table.get(tuple(current_shui), [])

        if not projected_sids:
            continue

        sid_utility_pairs = [(sid, calculate_sequence_utility(sid, S_new, utility_table))
                             for sid in projected_sids]
        sid_utility_pairs.sort(key=lambda x: x[1], reverse=True)
        sorted_sids = [sid for sid, _ in sid_utility_pairs]

        for victim_sid in sorted_sids:
            current_utility = calculate_total_utility(current_shui, S_new, utility_table, seqnum)
            du = current_utility - int(minutil) + 1

            if du <= 0:
                break
            min_item_utility = float('inf')
            victim_item = None
            for item in current_shui:
                if item in S_new and len(S_new[item][victim_sid]) > 0:
                    item_util = calculate_item_utility(item, victim_sid, S_new, utility_table)
                    if item_util < min_item_utility:
                        min_item_utility = item_util
                        victim_item = item

            if victim_item is None:
                continue

            if min_item_utility < du:
                current_quantity = len(S_new[victim_item][victim_sid])
                delete_item(victim_item, victim_sid, S_new)
                modified_sequences.add(victim_sid)
            else:
                current_quantity = len(S_new[victim_item][victim_sid])
                target_utility = min_item_utility - du
                decrease_item(victim_item, victim_sid, S_new, utility_table, target_utility)
                modified_sequences.add(victim_sid)
                new_quantity = len(S_new[victim_item][victim_sid])

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


# 主函数:从JSON读取并执行清洗
def run_sanitization_from_json(json_file, algorithm="MSU-MAU", output_file="msu_output.json"):
    """
    从挖掘结果JSON文件读取数据,执行清洗算法(MSU-MAU或MSU-MIU),
    然后对清洗后的位置字典重新挖掘高平均效用模式。
    """
    print(f"从 {json_file} 读取挖掘结果...")

    with open(json_file, "r", encoding="utf-8") as f:
        mine_cache = json.load(f)

    sensitive_patterns = [

        ['10', '10', '10', '10', '10', '10', '10'],  # ": 11627.0,
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

    # 执行清洗
    #tracemalloc.start()
    start = time.time()

    if algorithm == "MSU-MAU":
        print("执行 MSU-MAU 清洗中...")
        S_cleaned, modified_count = MSU_MAU_position(S, utility_table, sensitive_patterns, minutil, seq_num)

    elif algorithm == "MSU-MIU":
        print("执行 MSU-MIU 清洗中...")
        S_cleaned, modified_count =MSU_MIU_position(S, utility_table, sensitive_patterns, minutil, seq_num)


    else:
        raise ValueError("未知算法类型:" + algorithm)

    end = time.time()
    print(f"清洗完成，用时 {end - start:.3f}s")

    print(f"修改的序列数: {modified_count}")
    print("\n" + "=" * 70)
    print("计算 DUS (Dataset Utility Similarity) 指标")
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

    # 输出结果
    result = {
        "algorithm": algorithm,
        "runtime": end - start,
        "modified_sequences": modified_count,
        "metrics": metrics,
        "haup_before_count": len(original_patterns),
        "haup_after_count": len(cleaned_patterns)
    }

    print("=" * 70)
    print(f"DUS值: {dus_result['dus']:.4f} ({dus_result['dus'] * 100:.2f}%)")
    return result

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MSU-MAU/MSU-MIU privacy sanitization")
    parser.add_argument("--json", type=str, required=True, help="输入挖掘结果JSON文件路径")
    parser.add_argument("--algo", type=str, default="MSU-MAU",
                        choices=["MSU-MAU", "MSU-MIU"], help="选择清洗算法")
    parser.add_argument("--output", type=str, default="msu_output.json", help="输出文件路径")

    args = parser.parse_args()

    run_sanitization_from_json(args.json, args.algo, args.output)