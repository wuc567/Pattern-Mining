import re
import random

SEG = [0.2, 0.5, 0.8]
# SEG = [0.25, 0.55, 0.75]
# SEG = [0.15, 0.45, 0.85]
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

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split()
                if len(parts) == 2:
                    key = str(parts[0])
                    value = float(parts[1])
                    weights[key] = value

    return weights


def generate_char_weights(interest_file):
    # chars = 'abcdef'
    # weights = {c: random.uniform(0, 1) for c in chars}
    # weights={'a':0.3865,'b':0.4998,'c':0.1434,'d':0.4488,'e':0.7733}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.75, 'I': 0.85}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.74, 'I': 0.7}
    # weights = {'C': 0.25, 'e': 0.45, 'F': 0.55, 'g': 0.65, 'h': 0.7, 'I': 0.68}
    # weights = {'a': 0.45, 'b': 0.35, 'c': 0.6, 'd': 0.7, 'e': 0.66, 'f': 0.6}

    # weights = {'a': 0.45, 'b': 0.35, 'c': 0.6, 'd': 0.7, 'e': 0.66}
    # weights = {'a': 0.66, 'b': 0.45, 'c': 0.75, 'd': 0.55, 'e': 0.35}

    # file_path = "../../datasets/SDB1_interest.txt"
    # file_path = "../../datasets/SDB2_interest.txt"
    # file_path = "../../datasets/SDB3_interest.txt"
    # file_path = "../../datasets/SDB4_interest.txt"
    # file_path = "../../datasets/SDB5_interest.txt"
    # file_path = "../../datasets/SDB6_interest.txt"
    # file_path = "../../datasets/SDB7_interest.txt"
    # file_path = "../../datasets/SDB8_interest.txt"

    weights = read_weights_file(interest_file)

    return weights


def classify_characters(weights):
    """根据权重和隶属函数对字符分类"""
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

    strong_chars = [c for c, cat in char_category.items() if cat == 'Strong']
    medium_chars = [c for c, cat in char_category.items() if cat == 'Medium']
    weak_chars = [c for c, cat in char_category.items() if cat == 'Weak']


    jz_m = max((max_strong_val + max_weak_val) / 2, max_strong_val)
    jz_s = max_strong_val

    print("\n模糊强项:", strong_chars)
    print("模糊中项:", medium_chars)
    print("模糊弱项:", weak_chars)
    print("=" * 60)
    return char_membership, char_category, jz_s, jz_m


class processingData(object):
    def read_file(self, readfilename):
        lines_s = []
        with open(readfilename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                lines_s.append(line.strip())
        return lines_s

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
        s_array = [[]]  # 二维数组
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


    def General_Sn(self, lines_s, S):
        original_sequences = []
        valid_chars = []

        for i in range(len(lines_s)):
            items_array, s_array = self.split_array(lines_s[i])
            original_sequences.append(s_array)
            sort_item, items_no_repeat = self.item_sotrd(items_array)

            for c in sort_item:
                if c != '-1' and char_category[c] in ['Strong', 'Medium'] and c not in valid_chars:
                    valid_chars.append(c)

            for item in valid_chars:
                if item != '-1':
                    for k in range(len(s_array)):
                        if item in s_array[k]:
                            S[item][i].append(k)
        return S, original_sequences, sorted(valid_chars)

    def datap(self, readFileName, S,interest_file):
        lines_s = self.read_file(readFileName)

        items = []
        for lines in lines_s:
            items = self.Statistics_items(lines, items)

        sort_item, items_no_repeat = self.item_sotrd(items)

        self.write_file(sort_item, '../demo1/sort_item.txt')

        self.item_to_dict(sort_item, len(lines_s), S)

        weights = generate_char_weights(interest_file)
        char_membership, char_category, jz_s, jz_m = classify_characters(weights)

        S, original_sequences, sm_item = self.General_Sn(lines_s, S)

        return len(lines_s), S, sm_item, original_sequences, char_membership, char_category, jz_m, weights

    def utilityp(self, readFileName, U):
        lines_s = self.read_file(readFileName)
        for lines in lines_s:
            key_value = lines.strip().split(' ')
            U[key_value[0]] = key_value[1]

    def __del__(self):
        pass
