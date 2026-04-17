
import copy
import math
import sys
import json
import os
from collections import defaultdict
import Pdata


class PatternMiner:
    def __init__(self):
        self.CanNum = 0
        self.SItem = {}
        self.SItems = {}
        self.S = {}
        self.sort_item = []
        self.SeqNum = 0
        self.Utility = {}
        self.AUNP = []
        self.minsup = 0
        self.minau = 0
        self.pdata = Pdata.processingData()

        # 中间结果存储
        self.ItemS_map = {}      # pattern_str -> 每序列的路径列表
        self.support = {}        # 支持度
        self.util_map = {}       # 效用
        self.mine_result_file = None

    def campute_PreSuf(self, pattern):
        if len(pattern[0]) > 1:
            if str(pattern[0][0]) not in self.SItem:
                self.SItem[str(pattern[0][0])] = {}
            self.SItem[str(pattern[0][0])][str(pattern[0][1])] = ''
        else:
            if str(pattern[0][0]) not in self.SItems:
                self.SItems[str(pattern[0][0])] = {}
            self.SItems[str(pattern[0][0])][str(pattern[1][0])] = ''

    # MODIFIED: Matching_I 和 Matching_S 返回完整路径而非末项位置
    def Matching_I(self, list1, list2):
        """
        I型连接：同一项集内匹配（交集）。保留路径结构。
        list1, list2: [[路径1], [路径2], ...] 每个路径为 [pos]
        """
        list3 = [[] for _ in range(self.SeqNum)]
        count = 0
        for i in range(self.SeqNum):
            for pos_tuple1 in list1[i]:
                last_pos1 = pos_tuple1[-1]  # 获取最后一个位置

                for pos_tuple2 in list2[i]:
                    pos2 = pos_tuple2[0] if isinstance(pos_tuple2, tuple) else pos_tuple2

                    if last_pos1 == pos2:
                        list3[i].append(pos_tuple1)
                        break

            count += len(list3[i])

        return count, list3

    def Matching_S(self, list1, list2):
        """
        S-extension (序列扩展)
        list1: 前缀模式的位置信息
        list2: 后缀模式的位置信息
        返回: 出现次数和新的位置信息
        使用flag确保无重叠匹配
        """
        list3 = [[] for _ in range(self.SeqNum)]
        count = 0
        flag = 0

        for i in range(self.SeqNum):
            for j in range(len(list1[i])):
                if flag == len(list2[i]):
                    break

                pos_tuple1 = list1[i][j]
                if isinstance(pos_tuple1, tuple):
                    last_pos1 = pos_tuple1[-1]
                else:
                    last_pos1 = pos_tuple1

                for k in range(flag, len(list2[i])):
                    pos_tuple2 = list2[i][k]
                    if isinstance(pos_tuple2, tuple):
                        if len(pos_tuple2) == 1:
                            pos2 = pos_tuple2[0]
                        else:
                            pos2 = pos_tuple2[-1]
                    else:
                        pos2 = pos_tuple2

                    if pos2 > last_pos1:  # 确保后面的位置在前面之后
                        if isinstance(pos_tuple1, tuple):
                            new_tuple = pos_tuple1 + (pos2,)
                        else:
                            new_tuple = (pos_tuple1, pos2)

                        list3[i].append(new_tuple)
                        count += 1
                        flag = k + 1
                        break
                    if k == len(list2[i]) - 1:
                        flag = len(list2[i])
            flag = 0

        return count, list3

    # 单项模式初始化为路径 [ [pos] ]
    def Mine_ItemS(self, FP, ItemS):
        for i in self.sort_item:
            self.CanNum += 1
            count = 0
            ItemS[str([i])] = [[] for k in range(self.SeqNum)]

            for j in range(self.SeqNum):
                for pos in self.S[i][j]:
                    ItemS[str([i])][j].append((pos,))
                count += len(ItemS[str([i])][j])

            if count >= int(self.minsup):
                p = []
                p.append(i)
                FP.append([p])
                self.compute_utility([p], count)
            else:
                del ItemS[str([i])]

    # 两项模式：基于路径扩展
    def two_len(self, FP, ItemS):
        twoLenPattern = []
        Item = copy.deepcopy(FP)

        for pre in range(len(Item)):
            for suf in range(pre + 1, len(Item)):
                t = copy.deepcopy(Item[pre][0])
                t.append(Item[suf][0][0])
                p = [t]
                self.CanNum += 1
                pre_key = str([Item[pre][0][0]])
                suf_key = str([Item[suf][0][0]])
                count, ItemS[str(p)] = self.Matching_I(ItemS[pre_key], ItemS[suf_key])
                if count >= int(self.minsup):
                    FP.append(p)
                    self.campute_PreSuf(p)
                    twoLenPattern.append(p)
                    self.compute_utility(p, count)
                else:
                    del ItemS[str(p)]
        for m in Item:
            pre = copy.deepcopy(m)
            for n in Item:
                suf = copy.deepcopy(n)
                p = [pre[0], suf[0]]
                self.CanNum += 1
                pre_key = str([m[0][0]])
                suf_key = str([n[0][0]])
                count, ItemS[str(p)] = self.Matching_S(ItemS[pre_key], ItemS[suf_key])
                if count >= int(self.minsup):
                    FP.append(p)
                    self.campute_PreSuf(p)
                    twoLenPattern.append(p)
                    self.compute_utility(p, count)
                else:
                    del ItemS[str(p)]
        return twoLenPattern

    # 长模式：递推扩展路径
    def more_len(self, FP, ItemS, ExpSet):
        while ExpSet != []:
            temp = ExpSet[:]
            ExpSet = []

            for m in temp:
                suf = copy.deepcopy(m)
                suf[0].pop(0)

                if suf[0] == []:
                    sufstr = str(suf[1:])
                else:
                    sufstr = str(suf)

                for n in temp:
                    pre = copy.deepcopy(n)
                    pre[-1].pop(-1)

                    if pre[-1] == []:
                        prestr = str(pre[:-1])
                    else:
                        prestr = str(pre)

                    if sufstr == prestr:
                        if len(n[-1]) == 1:
                            if str(m[0][0]) in self.SItems.keys():
                                if str(n[-1][0]) in self.SItems[str(m[0][0])].keys():
                                    pattern = copy.deepcopy(m)
                                    pattern.append(n[-1])
                                    self.CanNum += 1
                                    last_item_key = str([n[-1][0]])
                                    count, ItemS[str(pattern)] = self.Matching_S(
                                        ItemS[str(pattern[:-1])], ItemS[last_item_key])
                                    if count >= int(self.minsup):
                                        FP.append(pattern)
                                        self.compute_utility(pattern, count)
                                        ExpSet.append(pattern)
                                    else:
                                        del ItemS[str(pattern)]
                        else:
                            pattern = copy.deepcopy(m)
                            pattern[-1].append(n[-1][-1])

                            if len(pattern) > 1:
                                if str(pattern[-1][-1]) in self.SItems[str(pattern[0][0])].keys():
                                    self.CanNum += 1
                                    last_item_key = str([pattern[-1][-1]])
                                    count, ItemS[str(pattern)] = self.Matching_S(
                                        ItemS[str(pattern[:-1])], ItemS[last_item_key])
                                    if count >= int(self.minsup):
                                        FP.append(pattern)
                                        ExpSet.append(pattern)
                                        self.compute_utility(pattern, count)
                                    else:
                                        del ItemS[str(pattern)]
                            else:
                                if str(pattern[-1][-1]) in self.SItem[str(pattern[0][0])].keys():
                                    self.CanNum += 1
                                    last_item_key = str([n[-1][-1]])
                                    count, ItemS[str(pattern)] = self.Matching_I(
                                        ItemS[str(m)], ItemS[last_item_key])
                                    if count >= int(self.minsup):
                                        FP.append(pattern)
                                        ExpSet.append(pattern)
                                        self.compute_utility(pattern, count)
                                    else:
                                        del ItemS[str(pattern)]

    def getUtility(self, utilityFileName):
        maxau = 0
        lines = self.pdata.read_file(utilityFileName)
        for line in lines:
            parts = line.split(' ')
            if len(parts) >= 2:
                self.Utility[parts[0]] = int(parts[1])
                if int(parts[1]) > maxau:
                    maxau = int(parts[1])
        if maxau > 0:
            self.minsup = math.ceil(int(self.minau) / maxau)

    def compute_utility(self, pattern, count):
        pattern_str = str(pattern)
        au = 0
        pattern_len = 0
        for itemset in pattern:
            for item in itemset:
                pattern_len += 1
                au += self.Utility.get(str(item), 0)
        if pattern_len > 0:
            au = au * count / pattern_len
            if au >= int(self.minau):
                self.AUNP.append(pattern)
                print(f"pattern:{pattern},PAU:{au}")
                self.util_map[pattern_str] = au
                self.support[pattern_str] = int(count)

    def Miner(self):
        FP = []
        ItemS = {}
        self.Mine_ItemS(FP, ItemS)
        twoLenPattern = self.two_len(FP, ItemS)
        self.more_len(FP, ItemS, twoLenPattern)


        self.ItemS_map = {}

        def flatten_pattern(p):
            if len(p) == 1 and isinstance(p[0], list):
                return flatten_pattern(p[0])
            elif all(isinstance(x, list) and len(x) == 1 for x in p):
                return [x[0] for x in p]
            else:
                return [item if isinstance(item, str) else flatten_pattern(item) for item in p]

        for key, value in ItemS.items():
            try:
                p_obj = eval(key)

                if isinstance(p_obj, list) and len(p_obj) == 1 and not isinstance(p_obj[0], list):
                    new_key = key
                elif isinstance(p_obj, list) and all(isinstance(x, list) and len(x) == 1 for x in p_obj):
                    flat_items = [x[0] for x in p_obj]
                    new_key = str(flat_items)
                else:
                    flat_p = flatten_pattern(p_obj)
                    new_key = str(flat_p)

                self.ItemS_map[new_key] = value

            except Exception as e:
                print(f"Warning: Could not process key {key}: {e}")
                self.ItemS_map[key] = value


    def mine_patterns(self, dataset_path, min_utility_threshold, utility_file_path=None, save_mine_path=None):

        def flatten_pattern(p):
            if len(p) == 1 and isinstance(p[0], list):
                return flatten_pattern(p[0])
            elif all(isinstance(x, list) and len(x) == 1 for x in p):
                return [x[0] for x in p]
            else:
                return [item if isinstance(item, str) else flatten_pattern(item) for item in p]

        self.__init__()
        self.minau = min_utility_threshold
        self.SeqNum, self.S, self.sort_item = self.pdata.datap(dataset_path, self.S)

        if utility_file_path is None:
            last_index = dataset_path.rindex(".")
            dataFileName = dataset_path[0:last_index]
            last_index = dataFileName.rindex("/")
            utility_file_path = dataFileName[0:last_index] + "/utility" + dataFileName[last_index:] + "_utility.txt"

        self.getUtility(utility_file_path)
        self.Miner()

        if save_mine_path is None:
            base = dataset_path
            try:
                last_index = base.rindex(".")
                base_no_ext = base[:last_index]
            except ValueError:
                base_no_ext = base
            save_mine_path = base_no_ext + "_mine_results.json"

            patterns_info = []
            pattern_ItemS = {}
            for p in self.AUNP:
                flat_p=flatten_pattern(p)
                p_str = str(flat_p)
                info = {
                    "pattern": p_str,
                    "support": int(self.support.get(str(p), 0)),
                    "utility": float(self.util_map.get(str(p), 0.0))
                }
                patterns_info.append(info)
                occ_info = []

                pattern_positions = self.ItemS_map.get(p_str, [])
                for seq_id in range(self.SeqNum):
                    if seq_id < len(pattern_positions) and pattern_positions[seq_id]:
                        occ_info.append({
                            "seq": seq_id,
                            "positions": pattern_positions[seq_id]
                        })

                pattern_ItemS[p_str] = occ_info

            flattened_util_map = {}
            flattened_support_map = {}
            for p_str, val in self.util_map.items():
                try:
                    p_obj = eval(p_str)
                    flat_p = flatten_pattern(p_obj)
                    flattened_util_map[str(flat_p)] = val
                except Exception:
                    flattened_util_map[p_str] = val

            for p_str, val in self.support.items():
                try:
                    p_obj = eval(p_str)
                    flat_p = flatten_pattern(p_obj)
                    flattened_support_map[str(flat_p)] = val
                except Exception:
                    flattened_support_map[p_str] = val

            mine_results = {
                "seq_num": self.SeqNum,
                "S": self.S,
                "sort_item": self.sort_item,
                "Utility": self.Utility,
                "minau": self.minau,
                "minsup": self.minsup,
                "patterns": patterns_info,
                "pattern_ItemS": pattern_ItemS,
                "util_map": flattened_util_map,
                "support_map": flattened_support_map
            }

            with open(save_mine_path, "w", encoding="utf-8") as f:
                json.dump(mine_results, f, ensure_ascii=False, indent=2)
            self.mine_result_file = save_mine_path



        self.AUNP = [flatten_pattern(p) for p in self.AUNP]

        return {
            'aunp_count': len(self.AUNP),
            'aunp_patterns': self.AUNP,
            'mine_result_file': self.mine_result_file
        }

    def mine_patterns_from_S(self, S, seq_num, sort_item, utility_dict, min_utility_threshold):
        """直接从S结构进行挖掘"""
        # 重置状态
        self.__init__()

        # 设置参数
        self.S = S
        self.SeqNum = seq_num
        self.sort_item = sort_item
        self.Utility = utility_dict
        self.minau = min_utility_threshold

        # 计算minsup
        maxau = max(utility_dict.values()) if utility_dict else 1
        self.minsup = math.ceil(int(min_utility_threshold) / maxau) if maxau > 0 else 0

        # 执行挖掘
        self.Miner()

        def flatten_pattern(p):
            if len(p) == 1 and isinstance(p[0], list):
                return flatten_pattern(p[0])
            elif all(isinstance(x, list) and len(x) == 1 for x in p):
                return [x[0] for x in p]
            else:
                return [item if isinstance(item, str) else flatten_pattern(item) for item in p]


        self.after_AUNP = [flatten_pattern(p) for p in self.AUNP]

        # 返回结果
        return {
            'aunp_count': len(self.after_AUNP),
            'aunp_patterns': self.after_AUNP
        }

def run_pattern_mining(dataset_path, min_utility_threshold, utility_file_path=None):
    miner = PatternMiner()
    return miner.mine_patterns(dataset_path, min_utility_threshold, utility_file_path)



if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python pattern_mining.py <dataset_path> <min_utility_threshold> [utility_file_path]")
        sys.exit(1)
    dataset_path = sys.argv[1]
    min_utility = sys.argv[2]
    utility_file = sys.argv[3] if len(sys.argv) > 3 else None
    results = run_pattern_mining(dataset_path, min_utility, utility_file)
    print(f"Number of AUNP: {results['aunp_count']}")
    print(f"AUNP patterns: {results['aunp_patterns']}")
