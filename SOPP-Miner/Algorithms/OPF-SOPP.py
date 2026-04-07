import math
import os
import statistics
import threading
import tracemalloc
from typing import List, Dict, Tuple

import numpy as np
from zmq.utils import monitor

try:
    import psutil
except ImportError:  # pragma: no cover - fallback when psutil is unavailable
    psutil = None


class MemoryLogger:
    _instance = None

    def __init__(self):
        self.max_memory = 0.0


    # def get_max_memory(self) -> float:
    #     return self.max_memory


# Global variables mirroring the Java implementation
minsup: float = 0.0
# Fmap maps a pattern string to [position list, [support], [group]]
Fmap: Dict[str, List[List[float]]] = {}
k: float = 0.0
E_CONST = math.e
S: List[float] = []
length: int = 0

# threshold for SOPP evaluation and counter for qualifying patterns
maxsta: float = 2.0
sopp_num = 0

# cand_num counts how many candidate patterns have been generated
cand_num = 2
# fre_num accumulates discovered frequent patterns across iterations
fre_num = 0
# fre_number tracks newly found frequent patterns within one iteration
fre_number = 0

element_num = 0
contrast_num = 0
# forgetting weights for each position in the sequence
# forget_mech: List[float] = []
# record of all frequent patterns with their support
allfrepattern: Dict[str, float] = {}


class LNode:
    def __init__(self, data: float = 0.0):
        self.data: float = data
        self.next: 'LNode | None' = None

def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / (1024 * 1024)
    return memory_usage_mb

def read_file(path: str, min_support: float = 4.0, max_sta: float = 2.0):
    global minsup, length, k, maxsta, sopp_num, fre_num, fre_number, cand_num
    global element_num, contrast_num
    # reset global state for a fresh run
    S.clear()
    Fmap.clear()
    allfrepattern.clear()
    sopp_num = 0
    fre_num = 0
    fre_number = 0
    cand_num = 2
    element_num = 0
    contrast_num = 0
    minsup = min_support
    maxsta = max_sta
    with open(path, "r") as br:
        for line in br:
            for token in line.strip().split():
                if token:
                    S.append(float(token))
    length = len(S)
    k = 1.0 / length
    memory_before = get_memory_usage()
    find()
    find_m()
    memory_after = get_memory_usage()
    print("内存",memory_after-memory_before)

def find():
    global cand_num
    cand_num = 2  # start with two length-2 candidates: [1,2] and [2,1]
    Z, Z2 = [], []  # position lists for the initial patterns
    i, j = 0, 1
    Cd = [1, 2]
    Cd2 = [2, 1]
    f1 = f2 = 0.0
    while j < length:
        if S[j] > S[i]:
            Z.append(j + 1.0)
            # print(111,f1)
            f1 += 1
            # print(222,f1)
        elif S[j] < S[i]:
            Z2.append(j + 1.0)
            f2 += 1
        i += 1
        j += 1
    judge_fre(Cd, Z, f1, 1)
    judge_fre(Cd2, Z2, f2, 3)


def judge_fre(Cd: List[int], Z: List[float], sup_num: float, group: int):
    global fre_number, sopp_num
    if sup_num >= minsup:
        fre_number += 1
        # Z stores the 1-indexed positions of pattern occurrences
        Fmap[str(Cd)] = [Z, [sup_num], [float(group)]]
        allfrepattern[str(Cd)] = sup_num
        if len(Z) > 1:
            diffs = [Z[i + 1] - Z[i] for i in range(len(Z) - 1)]
            mu = statistics.mean(diffs)
            if mu > 0:
                sta = np.std(diffs) / mu
                if sta <= maxsta:
                    sopp_num += 1


def find_m():
    global fre_num, fre_number, Fmap, contrast_num
    if fre_number > 0:
        # If only one initial pattern is frequent we cannot continue merging.
        if '[1, 2]' not in Fmap or '[2, 1]' not in Fmap:
            fre_num += fre_number  # accumulate frequent pattern count
            fre_number = 0
            return

        fre_num += fre_number  # accumulate frequent pattern count
        fre_number = 0
        sorted_data = sorted(Fmap.items(), key=lambda e: e[1][1][0], reverse=True)
        flag = Fmap['[1, 2]'][1][0] > Fmap['[2, 1]'][1][0]
        Fmap = {}
        Lb1: List[LNode] = []
        suffset: List[float] = []
        for key, value in sorted_data:
            Lb1.append(get_LNode(value[0]))
            suffset.append(value[1][0])
        if flag:
            for idx1, (key1, val1) in enumerate(sorted_data):
                P = string_to_array(key1)
                PNode = get_LNode(val1[0])
                group = int(val1[2][0])
                for i, (key2, val2) in enumerate(sorted_data):
                    if PNode.data >= minsup and suffset[i] >= minsup:
                        QNode = Lb1[i]
                        Q = string_to_array(key2)
                        pattern_fusion(P, PNode, Q, QNode, group, suffset, i)
                    group += 1
        else:
            for idx1, (key1, val1) in enumerate(sorted_data):
                P = string_to_array(key1)
                PNode = get_LNode(val1[0])
                group = int(val1[2][0]) + 1
                for i, (key2, val2) in enumerate(sorted_data):
                    if PNode.data >= minsup and suffset[i] >= minsup:
                        QNode = Lb1[i]
                        Q = string_to_array(key2)
                        pattern_fusion(P, PNode, Q, QNode, group, suffset, i)
                    group -= 1
    while fre_number > 0:
        fre_num += fre_number  # accumulate frequent pattern count
        fre_number = 0
        sorted_data = sorted(Fmap.items(), key=lambda e: e[1][1][0], reverse=True)
        G1, G2 = [], []
        for entry in sorted_data:
            grp = int(entry[1][2][0])
            if grp in (1, 2):
                G1.append(entry)
            else:
                G2.append(entry)
        Fmap = {}
        Lb1 = [get_LNode(v[0]) for _, v in G1]
        Lb2 = [get_LNode(v[0]) for _, v in G2]
        suffset1 = [v[1][0] for _, v in G1]
        suffset2 = [v[1][0] for _, v in G2]
        for key1, val1 in sorted_data:
            P = string_to_array(key1)
            PSuf = P[1:]
            PNode = get_LNode(val1[0])
            group = int(val1[2][0])
            if group in (1, 3):
                for i, (key2, val2) in enumerate(G1):
                    if PNode.data >= minsup and suffset1[i] >= minsup:
                        Q = string_to_array(key2)
                        QPre = Q[:-1]
                        contrast_num += 1
                        if get_order(PSuf) == get_order(QPre):
                            QNode = Lb1[i]
                            pattern_fusion(P, PNode, Q, QNode, group, suffset1, i)
            else:
                for i, (key2, val2) in enumerate(G2):
                    if PNode.data >= minsup and suffset2[i] >= minsup:
                        Q = string_to_array(key2)
                        QPre = Q[:-1]
                        contrast_num += 1
                        if get_order(PSuf) == get_order(QPre):
                            QNode = Lb2[i]
                            pattern_fusion(P, PNode, Q, QNode, group, suffset2, i)


def pattern_fusion(P: List[int], PNode: LNode, Q: List[int], QNode: LNode, group: int,
                   suffset: List[float], index: int):
    global cand_num
    slen = len(P)
    if P[0] == Q[-1]:
        Cd = [0] * (slen + 1)
        Cd2 = [0] * (slen + 1)
        Cd[0] = P[0]
        Cd2[0] = P[0] + 1
        Cd[slen] = Cd2[0]
        Cd2[slen] = Cd[0]
        for t in range(1, slen):
            if P[t] > Q[slen - 1]:
                Cd[t] = P[t] + 1
                Cd2[t] = P[t] + 1
            else:
                Cd[t] = P[t]
                Cd2[t] = P[t]
        cand_num += 2
        grow_base_p2(slen, QNode, PNode, Cd, Cd2, group, suffset, index)
    elif P[0] < Q[-1]:
        Cd = [0] * (slen + 1)
        Cd[0] = P[0]
        Cd[slen] = Q[slen - 1] + 1
        for t in range(1, slen):
            if P[t] > Q[slen - 1]:
                Cd[t] = P[t] + 1
            else:
                Cd[t] = P[t]
        cand_num += 1
        grow_base_p1(QNode, PNode, Cd, group, suffset, index)
    else:
        Cd = [0] * (slen + 1)
        Cd[0] = P[0] + 1
        Cd[slen] = Q[slen - 1]
        for t in range(slen - 1):
            if Q[t] > P[0]:
                Cd[t + 1] = Q[t] + 1
            else:
                Cd[t + 1] = Q[t]
        cand_num += 1
        grow_base_p1(QNode, PNode, Cd, group, suffset, index)


def grow_base_p2(slen: int, qNode: LNode, pNode: LNode, Cd: List[int], Cd2: List[int],
                 group: int, suffset: List[float], index: int):
    global element_num
    Z, Z2 = [], []
    p, q = pNode, qNode
    f1 = f2 = 0.0
    while p.next and q.next:
        if q.next.data == p.next.data + 1:
            lst = int(q.next.data)
            fri = lst - slen
            if S[lst - 1] > S[fri - 1]:
                Z.append(q.next.data)
                f1 += 1
            elif S[lst - 1] < S[fri - 1]:
                Z2.append(q.next.data)
                f2 += 1
            p.next = p.next.next
            q.next = q.next.next
        elif p.next.data < q.next.data:
            p = p.next
        else:
            q = q.next
        element_num += 1
    pNode.data -= len(Z) + len(Z2)
    suffset[index] -= f1 + f2
    judge_fre(Cd, Z, f1, group)
    judge_fre(Cd2, Z2, f2, group)


def grow_base_p1(qNode: LNode, pNode: LNode, Cd: List[int], group: int,
                 suffset: List[float], index: int):
    global element_num
    Z = []
    p, q = pNode, qNode
    f = 0.0
    while p.next and q.next:
        if q.next.data == p.next.data + 1:
            Z.append(q.next.data)
            f += 1
            p.next = p.next.next
            q.next = q.next.next
        elif p.next.data < q.next.data:
            p = p.next
        else:
            q = q.next
        element_num += 1
    pNode.data -= len(Z)
    suffset[index] -= f
    judge_fre(Cd, Z, f, group)


def get_order(seq: List[int]) -> List[int]:
    arr = seq[:]
    temp = sorted(arr)
    order = [0] * len(arr)
    for j in range(len(arr)):
        min_val = float('inf')
        idx = 0
        for i in range(len(arr)):
            if arr[i] < min_val:
                min_val = arr[i]
                idx = i
        arr[idx] = float('inf')
        order[idx] = j + 1
    return order


def string_to_array(key: str) -> List[int]:
    key = key.strip()[1:-1]
    if not key:
        return []
    return [int(x.strip()) for x in key.split(',')]


def get_LNode(lst: List[float]) -> LNode:
    head = LNode(float(len(lst)))
    curr = head
    for val in lst:
        node = LNode(val)
        curr.next = node
        curr = node
    return head


def result(time_spent: float):
    with open('SOPP_Miner.txt', 'a') as writer:
        writer.write(str(time_spent) + '\n')
        #MemoryLogger.get_instance().check_memory()
        # writer.write(str(MemoryLogger.get_instance().get_max_memory()) + '\n')
        writer.write(str(fre_num) + '\n')
        writer.write(str(cand_num) + '\n')
        writer.write(str(element_num) + '\n')
        writer.write(str(contrast_num) + '\n')
        writer.write('-----------------\n')


def read_file1(filepath: str):
    global S, fre_num, fre_number, Fmap, length, k
    S = []
    fre_num = 0
    fre_number = 0
    Fmap = {}
    with open(filepath, 'r') as br:
        for line in br:
            tokens = [t for t in line.strip().split(',') if t]
            S.extend(map(float, tokens))
    S = S[:2180]
    length = len(S)
    k = 1.0 / length
    find()
    find_m()


def write(filepath: str, mapping: Dict[str, float]):
    with open(filepath, 'w') as writer:
        for pattern, occur in mapping.items():
            writer.write(pattern.replace(',', '.') + ',' + str(occur) + '\n')


def get_files(path: str) -> List[str]:
    files = []
    for root, _, filenames in os.walk(path):
        for f in filenames:
            files.append(os.path.join(root, f))
    return files
def print_cost_time(seconds):
    print("时间",seconds)
    print("候选",cand_num)
    print("频繁",fre_num)
    print(sopp_num)
    # print(element_num)
    # print(contrast_num)
    # MemoryLogger.get_instance().check_memory()

def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_usage_mb = process.memory_info().rss / (1024 * 1024)
    return memory_usage_mb

if __name__ == '__main__':
    # Simple command line interface to run the miner on a dataset.
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Run SOPP miner on a numeric dataset.")
    parser.add_argument(
        "dataset",
        nargs="?",
        #default="/Users/zyj/Desktop/SOPP-Miner/Datasets/SDB3.1-3.10/SDB3_1000KB.txt",
        default="/Users/zyj/Desktop/SOPP-Miner/Datasets/SDB3_2000KB.txt",
        help="Path to a whitespace separated list of numbers (default: sample_data.txt)",
    )
    parser.add_argument(
        "--minsup", type=float, default=50.0, help="Minimum support threshold"
    )
    parser.add_argument(
        "--maxsta",
        type=float,
        default=1,
        help="Threshold for SOPP stability evaluation",
    )
    args = parser.parse_args()

    start = time.perf_counter()
    time1=time.time()
    read_file(args.dataset, args.minsup, args.maxsta)
    duration = time.perf_counter() - start
    print_cost_time(duration)
    time2 = time.time()
    print(time2-time1)
