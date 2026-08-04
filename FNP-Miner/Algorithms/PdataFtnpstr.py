import re
import bisect

SEG = [0.2, 0.5, 0.8]

char_category = {}

char_membership = {}


def strong_membership(x, seg):
    a, m, b = seg
    if x <= m:
        return 0
    elif m < x < b:
        return (x - m) / (b - m)
    else:
        return 1


def medium_membership(x, seg):
    a, m, b = seg
    if x <= a or x >= b:
        return 0
    elif m < x < b:
        return (b - x) / (b - m)
    else:
        return (x - a) / (m - a)


def weak_membership(x, seg):
    a, m, b = seg
    if x >= m:
        return 0
    elif a < x < m:
        return (m - x) / (m - a)
    else:
        return 1


def read_weights_file(file_path):
    weights = {}

    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        # 按行读取并处理
        for line in file:
            # 去除换行符并分割行内容
            line = line.strip()
            if line:  # 跳过空行
                parts = line.split()
                if len(parts) == 2:  # 确保每行有两个元素
                    key = str(parts[0])  # 键转换为字符串格式
                    value = float(parts[1])  # 值转换为整数
                    weights[key] = value

    return weights


def generate_char_weights(interest_file):
    """为每个可能字符（a - f 示例，可扩展）随机生成权重"""
    # chars = 'abcdef'
    # weights = {c: random.uniform(0, 1) for c in chars}
    # weights={'a':0.3865,'b':0.4998,'c':0.1434,'d':0.4488,'e':0.7733}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.75, 'I': 0.85}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.74, 'I': 0.7}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.7, 'I': 0.68}

    # file_path = "../datasets/SDB1_interest.txt"
    # file_path = "../datasets/SDB2_interest.txt"
    # file_path = "../datasets/SDB3_interest.txt"
    # file_path = "../datasets/SDB4_interest.txt"
    # file_path = "../datasets/SDB5_interest.txt"
    # file_path = "../datasets/SDB6_interest.txt"
    # file_path = "../datasets/SDB7_interest.txt"
    # file_path = "../datasets/SDB8_interest.txt"
    ##JL
    # file_path = "../datasets/SDB1_u_interest.txt"
    # file_path = "../datasets/SDB2_u_interest.txt"
    # file_path = "../datasets/SDB3_u_interest.txt"
    # file_path = "../datasets/SDB4_u_interest.txt"

    weights = read_weights_file(interest_file)

    return weights


def classify_characters(weights):
    max_strong_val = 0
    max_weak_val = 0
    for c, w in weights.items():
        strong_val = strong_membership(w, SEG)
        medium_val = medium_membership(w, SEG)
        weak_val = weak_membership(w, SEG)

        max_strong_val = max(strong_val, max_strong_val)
        max_weak_val = max(weak_val, max_weak_val)

        char_membership[c] = {
            'Strong': strong_val,
            'Medium': medium_val,
            'Weak': weak_val
        }
        if weak_val >= medium_val and weak_val > strong_val:
            char_category[c] = 'Weak'
        elif medium_val >= strong_val and medium_val > weak_val:
            char_category[c] = 'Medium'
        else:
            char_category[c] = 'Strong'

    print("\n字符权重和分类结果:")
    print("=" * 60)
    print(f"{'字符':<5}{'权重':<10}{'模糊强隶属度':<15}{'模糊中隶属度':<15}{'模糊弱隶属度':<15}{'分类'}")
    print("-" * 60)
    for c in sorted(weights.keys()):
        print(
            f"{c:<5}{weights[c]:<10.4f}{char_membership[c]['Strong']:<15.4f}{char_membership[c]['Medium']:<15.4f}{char_membership[c]['Weak']:<15.4f}{char_category[c]}")

    strong_chars = [c for c, cat in char_category.items() if cat == 'Strong']
    medium_chars = [c for c, cat in char_category.items() if cat == 'Medium']
    weak_chars = [c for c, cat in char_category.items() if cat == 'Weak']

    jz_m = max((max_strong_val + max_weak_val) / 2, max_strong_val)
    jz_s = max_strong_val

    print("\n模糊强项:", strong_chars)
    print("模糊中项:", medium_chars)
    print("模糊弱项:", weak_chars)
    print("=" * 60)
    return char_membership, char_category, jz_s, jz_m, strong_chars


class processingData(object):
    def read_file(self, readfilename):
        lines_s = []
        with open(readfilename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                lines_s.append(line.strip())
        return lines_s  # 返回数组

    # 将数组写入文件
    def write_file(self, lines_s, filename):
        with open(filename, 'w') as f:
            for i in range(len(lines_s)):
                f.writelines(str(i) + "\t" + lines_s[i])
                f.write("\n")

    def item_sotrd(self, items):
        items_no_repeat = []
        for item in items:
            if item not in items_no_repeat:
                items_no_repeat.append(item)

        sort_items = list(sorted(items_no_repeat))
        return sort_items, items_no_repeat

    # 定义空的数据字典
    '''
    S =
    {
    'a': [[0, 1, 3], [1], [0, 2, 4], [0, 1], [1, 3]],
    'b': [[], [0], [2], [0], [4]],
    'c': [[0, 1, 2, 3, 4], [1, 2], [0, 2, 3, 4, 5], [0, 1, 2, 3], [0, 1, 2, 3, 5]],
    'd': [[], [3], [0], [], [0, 3]],
    'e': [[], [1, 3], [4, 5], [3, 4], [5]],
    'f': [[], [0], [1, 4], [4], []]
    }
    '''

    def item_to_dict(self, sort_items, len_lines, S):
        for i in sort_items:
            S[i] = [[] for i in range(len_lines)]
        return S

    def replace_seq(self, lines_s, sort_item):
        flag = 1
        for i in range(len(sort_item)):
            for j in range(len(lines_s)):
                if flag == 1:
                    lines_s[j] = lines_s[j] + " "
                p1 = re.compile(" " + sort_item[i] + " ")
                lines_s[j], number = re.subn(p1, " " + str(i) + "* ", lines_s[j])
            flag = 0
        for i in range(len(lines_s)):
            lines_s[i] = lines_s[i].replace('*', '')
        return lines_s

    def split_array(self, lines):
        lines = lines.replace('  ', ' ')
        items_array = lines.strip().split(' ')
        s_array = [[]]
        i = 0
        for item in items_array:
            if item != '-1':
                s_array[i].append(item)
            else:
                i = i + 1
                s_array.append([])
        return items_array, s_array

    def Statistics_items(self, lines, items):
        lines = lines.replace('  ', ' ')
        items_array = lines.strip().split(' ')
        for item in items_array:
            if item != '-1' and item not in items:
                items.append(item)
        return items


def General_Se(self, lines_s):
    sequences = []
    valid_chars = []

    for i in range(len(lines_s)):
        items_array, s_array = self.split_array(lines_s[i])

        sequences.append(s_array)
        sort_item, items_no_repeat = self.item_sotrd(items_array)

        for c in sort_item:
            if c != '-1' and char_category[c] in ['Strong', 'Medium'] and c not in valid_chars:
                valid_chars.append(c)

    return sequences, valid_chars


def build_pl_map(self, sequences, S, sm_chars, strong_chars):
    num_seqs = len(sequences)

    strong_pos = []
    for seq_num in range(num_seqs):
        itemsets = sequences[seq_num]
        s_pos = []
        for itemset_idx, itemset in enumerate(itemsets):
            if any(char in itemset for char in strong_chars):
                s_pos.append(itemset_idx)
        strong_pos.append(s_pos)

    char_info = {}
    for seq_num in range(num_seqs):
        itemsets = sequences[seq_num]
        for itemset_idx, itemset in enumerate(itemsets):
            for char in itemset:
                if char in sm_chars:
                    if char not in char_info:
                        char_info[char] = [[] for _ in range(num_seqs)]
                    char_info[char][seq_num].append(itemset_idx)

    result = {}
    for char in sorted(sm_chars):
        for seq_num in range(num_seqs):
            pos_list = char_info[char][seq_num]
            if not pos_list:
                continue
            s_pos = strong_pos[seq_num]
            seq_tuples = []
            for pos in pos_list:
                idx = bisect.bisect_right(s_pos, pos)
                next_s_pos = s_pos[idx] if idx < len(s_pos) else None
                seq_tuples.append((pos, next_s_pos))
            S[char][seq_num] = seq_tuples
    return S


def datap(self, readFileName, S, interest_file):
    lines_s = self.read_file(readFileName)

    items = []
    for lines in lines_s:
        items = self.Statistics_items(lines, items)

    sort_item, items_no_repeat = self.item_sotrd(items)
    weights = generate_char_weights(interest_file)
    char_membership, char_category, jz_s, jz_m, strong_item = classify_characters(weights)

    self.item_to_dict(sort_item, len(lines_s), S)  # 排序后的项 和 序列数

    sequences, sm_item = self.General_Se(lines_s)

    S = self.build_pl_map(sequences, S, sm_item, strong_item)

    return sequences, len(lines_s), S, sm_item, char_membership, char_category, jz_m, weights


def utilityp(self, readFileName, U):
    lines_s = self.read_file(readFileName)
    for lines in lines_s:
        key_value = lines.strip().split(' ')
        U[key_value[0]] = key_value[1]


def __del__(self):
    pass
