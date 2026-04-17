# -*- coding: utf-8 -*-
import sys
from copy import deepcopy
from collections import defaultdict
import copy
import math
import time
import json
import tracemalloc


# HHUIF 算法
def HHUIF_position(S, utility_table, sensitive_itemsets, minutil, seqnum):

    S_new = deepcopy(S)

    def calculate_utility(itemset, S_dict, utility_table, seqnum):
        """计算itemset在数据库中的总utility"""
        total_util = 0
        for sid in range(seqnum):
            if all(item in S_dict and len(S_dict[item][sid]) > 0 for item in itemset):
                seq_util = sum(len(S_dict[item][sid]) * utility_table[item]
                               for item in itemset)
                total_util += seq_util
        return total_util

    for idx, s in enumerate(sensitive_itemsets):
        diff = calculate_utility(s, S_new, utility_table, seqnum) - int(minutil)

        iteration = 0
        while diff > 0:
            iteration += 1
            max_utility = -1
            max_item = None
            max_sid = None

            for sid in range(seqnum):
                if all(item in S_new and len(S_new[item][sid]) > 0 for item in s):
                    for item in s:
                        if item not in S_new:
                            continue
                        quantity = len(S_new[item][sid])
                        u = quantity * utility_table[item]
                        if u > max_utility:
                            max_utility = u
                            max_item = item
                            max_sid = sid

            if max_item is None or max_sid is None:
                break

            current_quantity = len(S_new[max_item][max_sid])
            current_utility = current_quantity * utility_table[max_item]

            if current_utility < diff:
                S_new[max_item][max_sid] = []
                diff -= current_utility
                print(f"  迭代#{iteration}: 删除 item={max_item}, seq={max_sid}, "
                      f"quantity={current_quantity}→0, 剩余diff={diff}")
            else:
                quantity_to_remove = math.ceil(diff / utility_table[max_item])
                new_quantity = max(0, current_quantity - quantity_to_remove)
                S_new[max_item][max_sid] = S_new[max_item][max_sid][:new_quantity]
                diff = 0

        final_util = calculate_utility(s, S_new, utility_table, seqnum)

    return S_new

# MSICF 算法
def MSICF_position(S, utility_table, sensitive_itemsets, minutil, seqnum):

    S_new = deepcopy(S)

    def calculate_utility(itemset, S_dict, utility_table, seqnum):
        """计算itemset在数据库中的总utility"""
        total_util = 0
        for sid in range(seqnum):
            if all(item in S_dict and len(S_dict[item][sid]) > 0 for item in itemset):
                seq_util = sum(len(S_dict[item][sid]) * utility_table[item]
                               for item in itemset)
                total_util += seq_util
        return total_util

    conflict_count = {}
    item_in_sets = {}  # 记录每个item出现在哪些敏感itemsets中

    for idx, s in enumerate(sensitive_itemsets):
        for item in s:
            if item not in conflict_count:
                conflict_count[item] = 0
                item_in_sets[item] = []
            conflict_count[item] += 1
            item_in_sets[item].append(idx)

    sorted_items = sorted(conflict_count.items(), key=lambda x: (-x[1], x[0]))

    for item, count in sorted_items:
        for si_idx in item_in_sets[item]:
            s = sensitive_itemsets[si_idx]

            current_util = calculate_utility(s, S_new, utility_table, seqnum)
            diff = current_util - int(minutil)
            if diff <= 0:
                continue
            iteration = 0
            while diff > 0:
                iteration += 1

                max_utility = -1
                max_sid = None

                for sid in range(seqnum):
                    if all(i in S_new and len(S_new[i][sid]) > 0 for i in s):
                        if item in S_new:
                            quantity = len(S_new[item][sid])
                            u = quantity * utility_table[item]
                            if u > max_utility:
                                max_utility = u
                                max_sid = sid

                if max_sid is None or max_utility <= 0:
                    break

                current_quantity = len(S_new[item][max_sid])
                current_utility = current_quantity * utility_table[item]

                if current_utility < diff:
                    S_new[item][max_sid] = []
                    diff -= current_utility
                else:
                    quantity_to_remove = math.ceil(diff / utility_table[item])
                    new_quantity = max(0, current_quantity - quantity_to_remove)
                    S_new[item][max_sid] = S_new[item][max_sid][:new_quantity]
                    diff = 0

            final_util = calculate_utility(s, S_new, utility_table, seqnum)

    return S_new

def compute_dus(S_original, S_sanitized, utility_table, seq_num):
    """
    计算 DUS (Dataset Utility Similarity) 指标
    基于清洗前后的数据集计算效用相似度
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
    """计算 HF, MC, AC 指标"""

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

    sen_normalized = [normalize_pattern(p) for p in sensitive_patterns]
    before_normalized = [normalize_pattern(p) for p in haups_before]
    after_normalized = [normalize_pattern(p) for p in haups_after]

    sen_set = set(sen_normalized)
    before_set = set(before_normalized)
    after_set = set(after_normalized)

    print("指标计算")
    print(f"{'=' * 60}")
    print(f"敏感模式总数: {len(sensitive_patterns)}")
    print(f"清洗前HAUP数量: {len(haups_before)}")
    print(f"清洗后HAUP数量: {len(haups_after)}")

    sen_in_before = sen_set & before_set
    sen_in_after = sen_set & after_set

    print(f"\n敏感模式在清洗前HAUP中: {len(sen_in_before)}")
    print(f"敏感模式在清洗后HAUP中: {len(sen_in_after)}")
    print(f"成功隐藏的敏感模式: {len(sen_in_before) - len(sen_in_after)}")

    # HF (Hiding Failure)
    if len(sen_in_before) > 0:
        HF = len(sen_in_after) / len(sen_in_before)
    else:
        HF = 0.0

    # MC (Missing Cost)
    non_sen_before = before_set - sen_set
    non_sen_after = after_set - sen_set
    lost_non_sen = non_sen_before - after_set

    if len(non_sen_before) > 0:
        MC = len(lost_non_sen) / len(non_sen_before)
    else:
        MC = 0.0

    # AC (Artificial Cost)
    new_patterns = after_set - before_set

    if len(after_set) > 0:
        AC = len(new_patterns) / len(after_set)
    else:
        AC = 0.0

    print(f"\n{'=' * 60}")
    print("性能指标")
    print(f"{'=' * 60}")
    print(f"HF (Hiding Failure)  = {HF:.4f}  ← 越低越好 (0=完美)")
    print(f"MC (Missing Cost)    = {MC:.4f}  ← 越低越好 (0=无损失)")
    print(f"AC (Artificial Cost) = {AC:.4f}  ← 越低越好 (0=无新增)")
    print(f"{'=' * 60}")

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

# 测试函数 - 直接对比两个算法
def compare_algorithms(S, utility_table, sensitive_itemsets, minutil, seqnum):
    """
    直接对比HHUIF和MSICF的差异
    """
    print("\n" + "=" * 80)
    print("开始算法对比测试")
    print("=" * 80)

    # 运行HHUIF
    print("\n" + "=" * 80)
    print("运行 HHUIF 算法")
    print("=" * 80)
    S_hhuif = HHUIF_position(deepcopy(S), utility_table, sensitive_itemsets, minutil, seqnum)

    # 运行MSICF
    print("\n" + "=" * 80)
    print("运行 MSICF 算法")
    print("=" * 80)
    S_msicf = MSICF_position(deepcopy(S), utility_table, sensitive_itemsets, minutil, seqnum)

    # 对比结果
    print("\n" + "=" * 80)
    print("算法结果对比")
    print("=" * 80)

    # 统计修改的位置数量
    modifications_hhuif = 0
    modifications_msicf = 0
    different_modifications = 0

    for item in S:
        for sid in range(seqnum):
            orig_qty = len(S[item][sid])
            hhuif_qty = len(S_hhuif[item][sid]) if item in S_hhuif else 0
            msicf_qty = len(S_msicf[item][sid]) if item in S_msicf else 0

            if orig_qty != hhuif_qty:
                modifications_hhuif += 1
            if orig_qty != msicf_qty:
                modifications_msicf += 1
            if hhuif_qty != msicf_qty:
                different_modifications += 1

    print(f"\nHHUIF 修改的位置数: {modifications_hhuif}")
    print(f"MSICF 修改的位置数: {modifications_msicf}")
    print(f"两者不同的位置数: {different_modifications}")


    return S_hhuif, S_msicf

from HUP-Miner import PatternMiner

def run_sanitization_from_json(json_file, algorithm="HHUIF", cache_path="mine_cache.pkl",
                               output_file="hhms_output.json"):
    """
    从挖掘结果JSON文件读取数据，执行清洗算法（HHUIF或MSICF），
    然后对清洗后的位置字典重新挖掘高平均效用模式。
    """
    miner = PatternMiner()
    print(f"从 {json_file} 读取挖掘结果...")
    with open(json_file, "r", encoding="utf-8") as f:
        mine_cache = json.load(f)

    sensitive_patterns = [

        ['10', '10', '10', '10', '10', '10', '10'],  # ": 11627.0,

    ]

    S = mine_cache["S"]
    S_original = copy.deepcopy(S)
    seq_num = mine_cache["seq_num"]
    sort_item = mine_cache["sort_item"]
    utility_table = mine_cache["Utility"]
    minutil = mine_cache["minau"]
    original_patterns = [p["pattern"] for p in mine_cache["patterns"]]
    print(f"原始 AUNP 数量: {len(original_patterns)}")

    print(f"已加载数据库：序列数={seq_num}，项数={len(S)}，敏感模式={len(sensitive_patterns)}")

    tracemalloc.start()
    start = time.time()
    if algorithm == "HHUIF":
        print("执行 HHUIF 清洗中...")
        S_cleaned =HHUIF_position(S, utility_table, sensitive_patterns, minutil, seq_num)
    elif algorithm == "MSICF":
        print("执行 MSICF 清洗中...")
        S_cleaned = MSICF_position(S, utility_table, sensitive_patterns, minutil, seq_num)
    else:
        raise ValueError("未知算法类型：" + algorithm)
    end = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"清洗完成，用时 {end - start:.3f}s")
    print(f"清洗完成，用时 {(end - start)*1000}ms")
    print(f"占用内存{peak / 1024 / 1024:.3f} MB")

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

    cleaned_results = miner.mine_patterns_from_S(
        S=S_cleaned,
        seq_num=seq_num,
        sort_item=sort_item,
        utility_dict=utility_table,
        min_utility_threshold=minutil
    )
    print(f"清洗后 AUNP 数量: {cleaned_results['aunp_count']}")

    print("计算评估指标 HF / MC / AC ...")
    metrics = compute_metrics(
        sensitive_patterns,
        original_patterns,
        cleaned_results['aunp_patterns']
    )

    result = {
        "algorithm": algorithm,
        "runtime": end - start,
        "metrics": metrics,
        "haup_before": original_patterns,
        "haup_after": cleaned_results['aunp_patterns'],
        "S_cleaned": S_cleaned
    }

    print(f"DUS值: {dus_result['dus']:.4f} ({dus_result['dus'] * 100:.2f}%)")
    print("=" * 70)

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HHMS privacy sanitization workflow")
    parser.add_argument("--json", type=str, required=True, help="输入挖掘结果JSON文件路径")
    parser.add_argument("--algo", type=str, default="HHUIF", choices=["HHUIF", "MSICF"], help="选择清洗算法")
    #parser.add_argument("--cache", type=str, default="mine_cache.pkl", help="mine_cache文件路径")
    #parser.add_argument("--output", type=str, default="hhms_output.json", help="输出文件路径")

    args = parser.parse_args()
    run_sanitization_from_json(args.json, args.algo)