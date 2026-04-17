import json
import time
import tracemalloc
from HUP-Miner import PatternMiner

from HAUP-Hider import Sanitizer2
#from HAUP2z-Hider import Sanitizer2
#from HAUP4z-Hider import Sanitizer2
#from HAUP5z-Hider import Sanitizer2
#from HAUPd21-Hider import Sanitizer2
#from HAUPd12-Hider import Sanitizer2


def convert_S_to_dataset(S, seq_num):
    """将倒排位置字典 S 转换为 transaction dataset"""
    dataset = []
    for seq_id in range(seq_num):
        transaction = {}
        for item, positions in S.items():
            if seq_id < len(positions) and positions[seq_id]:
                transaction[item] = len(positions[seq_id])
        dataset.append(transaction)
    return dataset
def flatten_pattern(pattern):
    """扁平化 [['a'], ['b']] → ['a','b']"""
    return [x for subset in pattern for x in subset]
def compute_dus(S_original, S_sanitized, external_utilities, seq_num):
    def compute_transaction_utility(transaction, S_dict, seq_id, external_utilities):
        total_utility = 0.0
        for item, internal_utility in transaction.items():
            if S_dict and item in S_dict and seq_id < len(S_dict[item]):
                internal_utility = len(S_dict[item][seq_id])
            external_utility = external_utilities.get(item, 1)
            total_utility += internal_utility * external_utility
        return total_utility

    D_original = convert_S_to_dataset(S_original, seq_num)
    D_sanitized = convert_S_to_dataset(S_sanitized, seq_num)

    utility_original = sum(
        compute_transaction_utility(D_original[i], S_original, i, external_utilities)
        for i in range(seq_num)
    )
    utility_sanitized = sum(
        compute_transaction_utility(D_sanitized[i], S_sanitized, i, external_utilities)
        for i in range(seq_num)
    )

    dus = utility_sanitized / utility_original if utility_original > 0 else 1.0

    return {
        'dus': dus,
        'utility_original': utility_original,
        'utility_sanitized': utility_sanitized,
        'utility_loss': utility_original - utility_sanitized,
        'utility_loss_percent': (
                    (utility_original - utility_sanitized) / utility_original * 100) if utility_original > 0 else 0.0
    }
def compute_metrics(sensitive_patterns, haups_before, haups_after):

    # 辅助函数: 将模式标准化为字符串以便比较
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

    print("\n=== 模式标准化过程 ===")
    sen_normalized = [normalize_pattern(p) for p in sensitive_patterns]
    before_normalized = [normalize_pattern(p) for p in haups_before]
    after_normalized = [normalize_pattern(p) for p in haups_after]

    sen_set = set(sen_normalized)
    before_set = set(before_normalized)
    after_set = set(after_normalized)

    print(f"\n=== 集合统计 ===")
    print(f"敏感模式集合大小: {len(sen_set)}")
    print(sen_set)
    print(f"清洗前HAUP集合大小: {len(before_set)}")
    print(f"清洗后HAUP集合大小: {len(after_set)}")

    sen_in_before = sen_set & before_set  # 敏感模式在清洗前HAUP中的交集
    sen_in_after = sen_set & after_set  # 敏感模式在清洗后HAUP中的交集

    print(f"\n=== 敏感模式分布 ===")
    print(f"敏感模式总数: {len(sen_set)}")
    print(f"敏感模式在清洗前HAUP中的数量: {len(sen_in_before)}")
    print(f"敏感模式在清洗后HAUP中的数量: {len(sen_in_after)}")

    # =================== 计算 HF (Hiding Failure) ===================
    # HF = 清洗后仍存在的敏感模式数 / 清洗前存在的敏感模式数
    if len(sen_in_before) > 0:
        HF = len(sen_in_after) / len(sen_in_before)
    else:
        # 如果清洗前就没有敏感模式，HF = 0 (完美隐藏)
        HF = 0.0

    print(f"\n=== HF 计算 ===")
    print(f"HF = {len(sen_in_after)} / {len(sen_in_before)} = {HF:.4f}")

    # =================== 计算 MC (Missing Cost) ===================
    # MC = 丢失的非敏感模式数 / 清洗前的非敏感模式数
    non_sen_before = before_set - sen_set  # 清洗前的非敏感模式
    non_sen_after = after_set - sen_set  # 清洗后的非敏感模式
    lost_non_sen = non_sen_before - after_set  # 丢失的非敏感模式

    if len(non_sen_before) > 0:
        MC = len(lost_non_sen) / len(non_sen_before)
    else:
        MC = 0.0

    print(f"\n=== MC 计算 ===")
    print(f"清洗前非敏感模式数: {len(non_sen_before)}")
    print(f"清洗后非敏感模式数: {len(non_sen_after)}")
    print(f"丢失的非敏感模式数: {len(lost_non_sen)}")
    print(f"MC = {len(lost_non_sen)} / {len(non_sen_before)} = {MC:.4f}")

    if len(lost_non_sen) > 0:
        print(f"丢失的非敏感模式样例: {list(lost_non_sen)[:3]}")

    # =================== 计算 AC (Artificial Cost) ===================
    # AC = 新增的模式数 / 清洗后的总模式数
    new_patterns = after_set - (after_set & before_set)  # 清洗后新增的模式

    if len(after_set) > 0:
        AC = len(new_patterns) / len(after_set)
    else:
        AC = 0.0

    print(f"\n=== AC 计算 ===")
    print(f"清洗后新增模式数: {len(new_patterns)}")
    print(f"清洗后总模式数: {len(after_set)}")
    print(f"AC = {len(new_patterns)} / {len(after_set)} = {AC:.4f}")

    if len(new_patterns) > 0:
        print(f"新增模式样例: {list(new_patterns)[:3]}")

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
def main(json_file):

    print("\n=== Step 1. 原始数据库挖掘 ===")

    print(f"从 {json_file} 读取挖掘结果...")
    with open(json_file, "r", encoding="utf-8") as f:
        mine_cache = json.load(f)

    S = mine_cache["S"]
    seq_num = mine_cache["seq_num"]
    sort_item = mine_cache["sort_item"]
    utility_dict = mine_cache["Utility"]
    minutil = mine_cache["minau"]

    original_patterns = [p["pattern"] for p in mine_cache["patterns"]]
    print(f"原始 AUNP 数量: {len(original_patterns)}")

    dataset = convert_S_to_dataset(S, seq_num)

    sensitive_patterns = [
        ['10', '10', '10', '10', '10', '10', '10'],  # ": 11627.0,

    ]
    non_sensitive_patterns = [
        p for p in original_patterns if p not in sensitive_patterns
    ]

    print("\n=== Step 2. 清洗阶段 ===")
    sanitizer = Sanitizer2()
    tracemalloc.start()
    start_time = time.time()

    cleaned_S= sanitizer.sanitize_patterns_by_partition(
        sensitive_patterns=sensitive_patterns,
        non_sensitive_patterns=non_sensitive_patterns,
        external_utilities=utility_dict,
        S=S,
        minutil=minutil,
        mine_cache=mine_cache
    )


    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"清洗完成，耗时 {(end_time - start_time)} s")
    print(f"清洗完成，耗时 {((end_time - start_time) * 1000)} ms")
    print(f"Peak memory: {peak / 1024 / 1024:.3f} MB")

    print("\n=== Step 3. 清洗后数据库挖掘 ===")
    miner2 = PatternMiner()
    cleaned_results = miner2.mine_patterns_from_S(
        S=cleaned_S,
        seq_num=seq_num,
        sort_item=sort_item,
        utility_dict=utility_dict,
        min_utility_threshold=minutil
    )

    print(f"清洗后 AUNP 数量: {cleaned_results['aunp_count']}")
    #print(f"清洗后 AUNP: {cleaned_results['aunp_patterns']}")


    compute_metrics(sensitive_patterns, original_patterns, cleaned_results['aunp_patterns'])
    dus_result=compute_dus(S,cleaned_S,utility_dict,seq_num)
    print(f"DUS值: {dus_result['dus']:.4f} ({dus_result['dus'] * 100:.2f}%)")
    print(f"原始数据集总效用: {dus_result['utility_original']:.2f}")
    print(f"清洗后数据集总效用: {dus_result['utility_sanitized']:.2f}")
    print(f"效用损失: {dus_result['utility_loss']:.2f} ({dus_result['utility_loss_percent']:.2f}%)")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HHMS privacy sanitization workflow")
    parser.add_argument("--json", type=str, required=True, help="输入挖掘结果JSON文件路径")
    args = parser.parse_args()
    main(args.json)
