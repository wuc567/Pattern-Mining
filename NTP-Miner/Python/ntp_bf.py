import time
from tkinter import END


def binary_search2(fre, cand, level):
    low, high = 0, len(fre) - 1
    if low > high:
        return -1
    while low <= high:
        mid = int((low + high) / 2)
        if cand == fre[mid][0:level - 1]:
            slow, shigh = low, mid
            if cand == fre[low][0:level - 1]:
                return low
            else:
                while slow < shigh:  # 此处二分有修改
                    smid = int((slow + shigh) / 2)
                    if cand == fre[smid][0:level - 1]:
                        shigh = smid
                    else:
                        slow = smid + 1
                if slow < 0 or slow >= len(fre):
                    slow = 0
                return slow
        elif cand < fre[mid][0:level - 1]:
            high = mid - 1
        else:
            low = mid + 1
    return -1


def binary_search(fre, cand, level):
    low, high = 0, len(fre) - 1
    if low > high:
        return -1
    while low < high:
        mid = int((low + high) / 2)
        if cand <= fre[mid][0:level - 1]:
            high = mid
        else:
            low = mid + 1
    if cand == fre[low][0:level - 1]:
        return low
    elif low + 1 < len(fre) and cand == fre[low + 1][0:level - 1]:
        return low + 1
    else:
        return -1


def read_file(file_path):
    file = open(file_path, 'r')
    return file.readlines()


# 通过模式连接生成候选模式
def gen_candidate(fre, level, fre0):
    candidate = []
    for i in fre:
        for j in fre0:
            cand = i[0:level] + j
            candidate.append(cand)
    return candidate


class NTP_bf:
    output_filepath = ""
    output_filename = "NTP-bf-Output.txt"
    mingap, maxgap = 0, 3
    minsup = 50
    s = "hilkmftwv"
    m = "rcqgpsyn"
    w = "adeuox"
    sDB = []
    sub_ptn = []

    def __init__(self, file_path, output_filepath, strong, middle, week, min_gap, max_gap, min_sup):
        self.sDB = read_file(file_path)
        self.output_filepath = output_filepath
        self.mingap, self.maxgap = min_gap, max_gap
        self.minsup = min_sup
        self.s = strong
        self.m = middle
        self.w = week

    class sub_ptn_struct:
        start = ''
        end = ''
        min, max = 0, 0

        def __init__(self, start, end, min, max):
            self.start = start
            self.end = end
            self.min = min
            self.max = max

    def min_freItem(self):
        counter = {}
        fre = []
        for strs in self.sDB:
            for c in strs:
                if self.belong(c, self.s) or self.belong(c, self.m):
                    if counter.get(c):
                        counter[c] = counter[c] + 1
                    else:
                        counter[c] = 1
        for key in counter.keys():
            if counter[key] >= self.minsup:
                fre.append(key)
        return sorted(fre)

    def deal_range(self, pattern):
        sub_ptn = []
        if len(pattern) == 1:
            sub_ptn.append(self.sub_ptn_struct(pattern[0], "", 0, 0))
        for i in range(0, len(pattern) - 1):
            sub_ptn.append(self.sub_ptn_struct(pattern[i], pattern[i + 1], self.mingap, self.maxgap))
        return sub_ptn

    def create_nettree(self, nettree, seq):
        occurnum = 0
        for i in range(0, len(self.sub_ptn) + 1):
            nettree.append([])
        for i in range(0, len(seq) - len(self.sub_ptn)):
            if seq[i] != self.sub_ptn[0].start:
                continue
            nettree[0].append(i)
            occurnum = occurnum + self.create_subnettree(nettree, seq, i, 2)
        return occurnum

    def create_subnettree(self, nettree, seq, parent, L):
        if L > len(self.sub_ptn) + 1:
            return 1
        for i in range(parent + 1, parent + self.sub_ptn[L - 2].min + 1):
            if self.belong(seq[i], self.s):
                return 0
        for i in range(parent + self.sub_ptn[L - 2].min + 1, parent + self.sub_ptn[L - 2].max + 2):
            # print(i, len(seq), parent)
            if i >= len(seq):
                break
            if seq[i] == self.sub_ptn[L - 2].end:
                k = len(nettree[L - 1])
                flag = -1
                for j in range(k):
                    if i == nettree[L - 1][j]:
                        flag = j
                        break
                if flag == -1:
                    nettree[L - 1].append(i)
                    if self.create_subnettree(nettree, seq, i, L + 1):
                        return 1
            if not self.belong(seq[i], self.m) and not self.belong(seq[i], self.w):
                break
        return 0

    def belong(self, ch, str):
        for c in str:
            if ch == c:
                return True
        return False

    def output(self, freArr):
        output_file = open(self.output_filepath + "/" + self.output_filename, 'w')
        for fre in freArr:
            strArr = ""
            for strs in fre:
                strArr += strs + " "
            output_file.write(strArr + "\n")

    def solve(self, text):
        text.insert(END, "NTP_bf算法开始运行，请等待...\n")
        text.insert(END, "算法参数：\n")
        text.insert(END, "强字符集：" + self.s + " 中字符集：" + self.m + " 弱字符集：" + self.w + "\n")
        text.insert(END,
                    "mingap:" + str(self.mingap) + " maxgap:" + str(self.maxgap) + " minsup:" + str(self.minsup) + "\n")
        compnum = 0
        f_level = 1
        freArr = []

        begin_time = time.time()
        fre = self.min_freItem()
        freArr.append(fre)
        candidate = gen_candidate(fre, f_level, freArr[0])
        while len(candidate) != 0:
            next_fre = []
            for p in candidate:
                occnum = 0
                compnum = compnum + 1
                for strs in self.sDB:
                    if len(strs) > 0:
                        self.sub_ptn = self.deal_range(p)
                        num = 0
                        if len(self.sub_ptn) + 1 > len(strs):
                            num = 0
                        else:
                            nettree = []
                            num = self.create_nettree(nettree, strs)
                        occnum += num
                    if occnum >= self.minsup:
                        next_fre.append(p)
                        break
            f_level += 1
            freArr.append(next_fre)
            candidate = gen_candidate(next_fre, f_level, freArr[0])
            # print(next_fre, f_level, len(candidate))

        end_time = time.time()
        time_consuming = end_time - begin_time
        freNum = 0
        text.insert(END, "NTP_bf算法运行完毕。\n")
        for fre in freArr:
            strArr = ""
            for strs in fre:
                # print(str, end=" ")
                strArr += strs + " "
                freNum += 1
            text.insert(END, strArr + "\n")
        # print("The number of frequent patterns:", freNum, "\n")
        # print("The time-consuming:", time_consuming * 1000, "ms\n")
        # print("The number of calculation:", compnum, "\n")
        text.insert(END, "The number of frequent patterns:" + str(freNum) + "\n")
        text.insert(END, "The time-consuming:" + str(time_consuming * 1000) + "ms" + "\n")
        text.insert(END, "The number of calculation:" + str(compnum) + "\n")
        self.output(freArr)
        text.insert(END, "挖掘结果已写入：" + self.output_filepath + "/" + self.output_filename + "\n")

    def solve_test(self):
        print("NTP_bf算法开始运行，请等待...")
        print("算法参数：")
        print("强字符集：" + self.s + " 中字符集：" + self.m + " 弱字符集：" + self.w)
        print("mingap:" + str(self.mingap) + " maxgap:" + str(self.maxgap) + " minsup:" + str(self.minsup))
        compnum = 0
        f_level = 1
        freArr = []

        begin_time = time.time()
        fre = self.min_freItem()
        freArr.append(fre)
        candidate = gen_candidate(fre, f_level, freArr[0])
        while len(candidate) != 0:
            next_fre = []
            for p in candidate:
                occnum = 0
                compnum = compnum + 1
                for strs in self.sDB:
                    if len(strs) > 0:
                        self.sub_ptn = self.deal_range(p)
                        num = 0
                        if len(self.sub_ptn) + 1 > len(strs):
                            num = 0
                        else:
                            nettree = []
                            num = self.create_nettree(nettree, strs)
                        occnum += num
                    if occnum >= self.minsup:
                        next_fre.append(p)
                        break
            f_level += 1
            freArr.append(next_fre)
            candidate = gen_candidate(next_fre, f_level, freArr[0])
            # print(next_fre, f_level, len(candidate))

        end_time = time.time()
        time_consuming = end_time - begin_time
        freNum = 0
        print("NTP_bf算法运行完毕。")
        for fre in freArr:
            strArr = ""
            for strs in fre:
                # print(str, end=" ")
                strArr += strs + " "
                freNum += 1
            print(strArr)
        # print("The number of frequent patterns:", freNum, "\n")
        # print("The time-consuming:", time_consuming * 1000, "ms\n")
        # print("The number of calculation:", compnum, "\n")
        print("The number of frequent patterns:" + str(freNum))
        print("The time-consuming:" + str(time_consuming * 1000) + "ms")
        print("The number of calculation:" + str(compnum))


if __name__ == '__main__':
    print("请输入输入源文件名（包含路径）：")
    file = input()
    print("请输入强字符集：")
    s = input()
    print("请输入中字符集：")
    m = input()
    print("请输入弱字符集：")
    w = input()
    print("请输入min_gap：")
    min_gap = input()
    print("请输入max_gap：")
    max_gap = input()
    print("请输入min_sup：")
    min_sup = input()
    NTP_bf(file, s, m, w, min_gap, max_gap, min_sup).solve_test()
    # NTP_Miner("D:\\github\\Pattern-Mining\\NTP-Miner\\NTP-DataSet\\SDB6.txt", "hilkmftwv", "rcqgpsyn", "adeuox", 0, 3, 400).solve_test()
