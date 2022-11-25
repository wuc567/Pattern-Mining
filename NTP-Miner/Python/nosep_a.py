import time
from copy import deepcopy
from tkinter import END


class node:
    name = 0
    min_leave, max_leave = 0, 0
    parent = []
    children = []
    used = False
    toleave = False

    def __init__(self):
        pass


class occurrence:
    position = []

    def __init__(self):
        pass


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
def gen_candidate(fre, level):
    candidate = []
    start = 0
    for model in fre:
        R = model[1:level]
        Q = fre[start][0:level - 1]
        if Q != R:
            start = binary_search(fre, R, level)
        if start < 0 or start >= len(fre):
            start = 0
        else:
            Q = fre[start][0:level - 1]
            while Q == R:
                candidate.append(model[0:level] + fre[start][level - 1:level])
                start = start + 1
                if start >= len(fre):
                    start = 0
                    break
                Q = fre[start][0:level - 1]
    print(len(candidate), level, len(fre))
    return candidate


class NOSEP_a:
    output_filepath = ""
    output_filename = "NOSEP-a-Output.txt"
    mingap, maxgap = 0, 3
    minsup = 50
    s = "hilkmftwv"
    m = "rcqgpsyn"
    w = "adeuox"
    sDB = []
    sub_ptn = []
    store = 0
    freArr = []
    candidate = []
    compnum = 0
    frenum = 0

    def __init__(self, file_path, output_filepath, strong, middle, week, min_gap, max_gap, min_sup):
        self.sDB = read_file(file_path)
        self.output_filepath = output_filepath
        self.mingap, self.maxgap = min_gap, max_gap
        self.minsup = min_sup
        self.s = strong
        self.m = middle
        self.w = week
        self.sub_ptn = []
        self.store = 0
        self.freArr = []
        self.candidate = []
        self.compnum = 0
        self.frenum = 0

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
        for i in range(0, len(self.sub_ptn) + 1):
            if i < len(nettree):
                nettree[i].clear()
            else:
                nettree.append([])
        start = [0 for _ in range(len(self.sub_ptn) + 1)]
        for i in range(len(seq)):
            anode = node()
            anode.name = i
            anode.parent = []
            anode.children = []
            anode.min_leave, anode.max_leave = anode.name, anode.name
            anode.used = False
            if self.sub_ptn[0].start == seq[i]:
                anode.toleave = True
                nettree[0].append(deepcopy(anode))
            for j in range(len(self.sub_ptn)):
                if self.sub_ptn[j].end == seq[i]:
                    prev_len = len(nettree[j])
                    if prev_len == 0:
                        break
                    for k in range(start[j], prev_len):
                        if i - nettree[j][k].name - 1 > self.sub_ptn[j].max:
                            start[j] += 1
                    if i - nettree[j][prev_len - 1].name - 1 > self.sub_ptn[j].max:
                        continue
                    if i - nettree[j][start[j]].name - 1 < self.sub_ptn[j].min:
                        continue
                    tlen = len(nettree[j+1])
                    anode.toleave = True
                    nettree[j+1].append(deepcopy(anode))
                    for k in range(start[j], prev_len):
                        if i - nettree[j][k].name - 1 < self.sub_ptn[j].min:
                            break
                        flag = False
                        for f in range(nettree[j][k].name + 1, i):
                            if self.belong(seq[f], self.s):
                                flag = True
                                break
                        if not flag:
                            nettree[j][k].children.append(tlen)
                            nettree[j+1][tlen].parent.append(k)

    def update_nettree(self, nettree):
        for i in range(len(self.sub_ptn)-1, -1, -1):
            for j in range(len(nettree[i])-1, -1, -1):
                flag = True
                size = len(nettree[i][j].children)
                for k in range(size):
                    child = nettree[i][j].children[k]
                    if k == 0:
                        nettree[i][j].min_leave = nettree[i+1][child].min_leave
                    if k == size - 1:
                        nettree[i][j].max_leave = nettree[i+1][child].max_leave
                    if not nettree[i + 1][child].used:
                        flag = False
                nettree[i][j].used = flag
                if flag:
                    nettree[i][j].max_leave = nettree[i][j].name
                    nettree[i][j].min_leave = nettree[i][j].name
                    nettree[i][j].toleave = False

    def update_nettree_pc(self, nettree, occin):
        for level in range(len(self.sub_ptn), 0, -1):
            for position in range(occin.position[level], len(nettree[level])):
                if not nettree[level][position].used:
                    break
                for i in range(len(nettree[level][position].parent)):
                    parent = nettree[level][position].parent[i]
                    cs = len(nettree[level-1][parent].children)
                    if nettree[level-1][parent].used:
                        continue
                    if cs == 1:
                        nettree[level-1][parent].used = True
                        nettree[level-1][parent].toleave = False
                    else:
                        kk = 0
                        while kk < cs:
                            child = nettree[level-1][parent].children[kk]
                            if not nettree[level][child].used:
                                break
                            kk += 1
                        if kk == cs:
                            nettree[level-1][parent].used = True
                            nettree[level-1][parent].toleave = False

    def nonoverlength(self, rest, seq):
        nettree = []
        self.create_nettree(nettree, seq)
        self.update_nettree(nettree)
        self.store = 0
        for position in range(len(nettree[0])):
            if not nettree[0][position].toleave:
                continue
            occin = occurrence()
            occin.position = [0 for _ in range(len(self.sub_ptn) + 1)]
            occin.position[0] = position
            nettree[0][position].used = True
            nettree[0][position].toleave = False
            j = 1
            while j <= len(self.sub_ptn):
                parent = occin.position[j-1]
                cs = len(nettree[j-1][parent].children)
                t = 0
                while t < cs:
                    child = nettree[j-1][parent].children[t]
                    if not nettree[j][child].used:
                        occin.position[j] = child
                        nettree[j][child].used = True
                        nettree[j][child].toleave = False
                        break
                    t += 1
                if t == cs:
                    for kk in range(j):
                        pos = occin.position[kk]
                        nettree[kk][pos].used = False
                        nettree[kk][pos].toleave = True
                    break
                j += 1
            if j == len(self.sub_ptn) + 1:
                self.store += 1
                if self.store > rest:
                    return
                self.update_nettree_pc(nettree, occin)

    def netGap(self, p, rest, seq):
        self.sub_ptn = self.deal_range(p)
        if len(self.sub_ptn) + 1 > len(seq):
            return 0
        self.nonoverlength(rest, seq)
        return self.store

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
        text.insert(END, "NOSEP-a算法开始运行，请等待...\n")
        text.insert(END, "算法参数：\n")
        text.insert(END, "强字符集：" + self.s + " 中字符集：" + self.m + " 弱字符集：" + self.w + "\n")
        text.insert(END,
                    "mingap:" + str(self.mingap) + " maxgap:" + str(self.maxgap) + " minsup:" + str(self.minsup) + "\n")
        compnum = 0
        f_level = 1
        freArr = []

        begin_time = time.time()

        fre = self.min_freItem()
        candidate = gen_candidate(fre, f_level)
        freArr.append(fre)
        while len(candidate) != 0:
            next_fre = []
            for i in range(len(candidate)):
                occnum = 0
                rest = 0
                p = candidate[i]
                self.compnum += 1
                for t in range(len(self.sDB)):
                    rest = self.minsup - occnum
                    if len(self.sDB[t]) > 0:
                        occnum += self.netGap(p, rest, self.sDB[t])
                    if occnum >= self.minsup:
                        next_fre.append(p)
                        break
                # print(p, ":", occnum)
            f_level += 1
            candidate.clear()
            fre = next_fre
            freArr.append(fre)
            candidate = gen_candidate(fre, f_level)

        end_time = time.time()
        time_consuming = end_time - begin_time
        freNum = 0
        text.insert(END, "NOSEP-a算法运行完毕。\n")
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
        text.insert(END, "The number of calculation:" + str(self.compnum) + "\n")
        self.output(freArr)
        text.insert(END, "挖掘结果已写入：" + self.output_filepath + "/" + self.output_filename + "\n")

    def solve_test(self):
        print("NOSEP-a算法开始运行，请等待...")
        print("算法参数：")
        print("强字符集：" + self.s + " 中字符集：" + self.m + " 弱字符集：" + self.w)
        print("mingap:" + str(self.mingap) + " maxgap:" + str(self.maxgap) + " minsup:" + str(self.minsup))
        compnum = 0
        f_level = 1
        freArr = []

        begin_time = time.time()

        fre = self.min_freItem()
        candidate = gen_candidate(fre, f_level)
        freArr.append(fre)
        while len(candidate) != 0:
            next_fre = []
            for i in range(len(candidate)):
                occnum = 0
                rest = 0
                p = candidate[i]
                self.compnum += 1
                for t in range(len(self.sDB)):
                    rest = self.minsup - occnum
                    if len(self.sDB[t]) > 0:
                        occnum += self.netGap(p, rest, self.sDB[t])
                    if occnum >= self.minsup:
                        next_fre.append(p)
                        break
                # print(p, ":", occnum)
            f_level += 1
            candidate.clear()
            fre = next_fre
            freArr.append(fre)
            candidate = gen_candidate(fre, f_level)

        end_time = time.time()
        time_consuming = end_time - begin_time
        freNum = 0
        print("NOSEP-a算法运行完毕。")
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
        print("The number of calculation:" + str(self.compnum))


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
    NOSEP_a(file, s, m, w, min_gap, max_gap, min_sup).solve_test()
    # NTP_Miner("D:\\github\\Pattern-Mining\\NTP-Miner\\NTP-DataSet\\SDB6.txt", "hilkmftwv", "rcqgpsyn", "adeuox", 0, 3, 400).solve_test()
