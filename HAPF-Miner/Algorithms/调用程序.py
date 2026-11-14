import subprocess
import re
import sys

# 你的原程序文件名
program_file = r"E:\PythonProject\HAFP-Miner\CoNR-HAPF(调用程序）.py"

peak_usages = []
running_times = []
candidate_nums = []
sup_counts = []
matching_counts = []

for i in range(5):
    print(f"\n========== 第 {i + 1} 次运行 ==========")

    result = subprocess.run(
        [sys.executable, program_file],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    output = result.stdout
    print(output)

    # 提取 Peak Usage
    peak_match = re.search(
        r"Peak Usage\s*:\s*([\d.]+)\s*MB",
        output
    )

    # 提取 running time
    time_match = re.search(
        r"running time\s*:\s*([\d.]+)\s*秒",
        output
    )

    # 提取生成候选模式数量
    can_match = re.search(
        r"生成候选模式数量[：:]\s*(\d+)",
        output
    )

    # 提取支持度计算次数
    sup_match = re.search(
        r"支持度计算次数[：:]\s*(\d+)",
        output
    )

    # 提取模式匹配次数
    matching_match = re.search(
        r"模式匹配次数[：:]\s*(\d+)",
        output
    )

    if (
        peak_match
        and time_match
        and can_match
        and sup_match
        and matching_match
    ):
        peak_usages.append(float(peak_match.group(1)))
        running_times.append(float(time_match.group(1)))
        candidate_nums.append(int(can_match.group(1)))
        sup_counts.append(int(sup_match.group(1)))
        matching_counts.append(int(matching_match.group(1)))

    else:
        print("本次结果提取失败，请检查原程序打印格式是否一致。")

        if not peak_match:
            print("未提取到 Peak Usage")

        if not time_match:
            print("未提取到 running time")

        if not can_match:
            print("未提取到生成候选模式数量")

        if not sup_match:
            print("未提取到支持度计算次数")

        if not matching_match:
            print("未提取到模式匹配次数")

        print("错误信息：")
        print(result.stderr)


print("\n========== 5 次运行统计结果 ==========")

if peak_usages:
    print(
        f"Peak Usage 平均值："
        f"{sum(peak_usages) / len(peak_usages):.2f} MB"
    )

if running_times:
    print(
        f"running time 平均值："
        f"{sum(running_times) / len(running_times):.4f} 秒"
    )

if candidate_nums:
    print(
        f"生成候选模式数量平均值："
        f"{sum(candidate_nums) / len(candidate_nums):.2f}"
    )

if sup_counts:
    print(
        f"支持度计算次数平均值："
        f"{sum(sup_counts) / len(sup_counts):.2f}"
    )

if matching_counts:
    print(
        f"模式匹配次数平均值："
        f"{sum(matching_counts) / len(matching_counts):.2f}"
    )