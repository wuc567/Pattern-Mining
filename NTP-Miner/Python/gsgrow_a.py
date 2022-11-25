import time
from copy import deepcopy
from tkinter import END


class Pos:
    pos = []

    def __init__(self, pos):
        self.pos = pos


class ISupSet:
    id = 0
    poset = []

    def __init__(self, id, poset):
        self.id = id
        self.poset = poset


class Freq_ptn:
    length = 0
    ptn = []

    def __init__(self, length, ptn):
        self.length = length
        self.ptn = ptn


class All_Fre:
    length = 0
    fre = []

    def __init__(self, length, fre):
        self.length = length
        self.fre = fre


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


class GSgrow_a:
    output_filepath = ""
    output_filename = "GSgrow-a-Output.txt"
    mingap, maxgap = 0, 3
    minsup = 50
    s = "hilkmftwv"
    m = "rcqgpsyn"
    w = "adeuox"
    sDB = []
    sub_ptn = []
    eSet = []
    Fre = []
    All_Fre = []
    compnum = 0

    def __init__(self, file_path, output_filepath, strong, middle, week, min_gap, max_gap, min_sup):
        self.sDB = read_file(file_path)
        self.output_filepath = output_filepath
        self.mingap, self.maxgap = min_gap, max_gap
        self.minsup = min_sup
        self.s = strong
        self.m = middle
        self.w = week
        self.sub_ptn = []
        self.eSet = []
        self.Fre = []
        self.All_Fre = []
        self.compnum = 0

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
        for strs in self.sDB:
            for c in strs:
                if self.belong(c, self.s) or self.belong(c, self.m):
                    if counter.get(c):
                        counter[c] = counter[c] + 1
                    else:
                        counter[c] = 1
        for key in counter.keys():
            self.eSet.append(key[0])
        self.eSet = sorted(self.eSet)

    def mineFre(self, support, sDB, P, I):
        Q = []
        if support >= self.minsup:
            fsum = len(self.Fre)
            plen = len(P)
            self.Fre.append(Freq_ptn(plen, deepcopy(P)))
            for t in P:
                Q.append(t)
            for e in self.eSet:
                if len(Q) == len(P):
                    Q.append(e)
                else:
                    Q[len(P)] = e
                self.sub_ptn.clear()
                for k in range(0, len(Q) - 1):
                    # self.sub_ptn.append(self.sub_ptn_struct(Q[k], Q[k + 1], self.mingap, self.maxgap))
                    if k >= len(self.sub_ptn):
                        self.sub_ptn.append(self.sub_ptn_struct(Q[k], Q[k + 1], self.mingap, self.maxgap))
                    else:
                        self.sub_ptn[k].start = Q[k]
                        self.sub_ptn[k].end = Q[k+1]
                        self.sub_ptn[k].min = self.mingap
                        self.sub_ptn[k].max = self.maxgap
                self.compnum += 1
                IPLUS = []
                support = self.INSgrow_Gap(sDB, self.sub_ptn, I, IPLUS)
                self.mineFre(support, sDB, Q, IPLUS)

    def SizeOneSup(self, sDB, P, I):
        support = 0
        if len(P) == 1:
            for i in range(0, len(sDB)):
                for l in range(0, len(sDB[i])):
                    while len(I) < i + 1:
                        I.append(ISupSet(0, []))
                    if sDB[i][l] == P[len(P) - 1]:
                        I[i].poset.append(Pos([l]))
                        I[i].id = i + 1
                        support += 1
        return support

    def next(self, seq, p, maxi, a, b):
        for i in range(max(maxi + 1, a), b + 1):
            if seq[i] == p:
                return i
            else:
                if self.belong(seq[i], self.s):
                    return -1
        return -1

    def INSgrow_Gap(self, sDB, sub_ptn, I, IPLUS):
        support = 0
        p = sub_ptn[len(sub_ptn) - 1].end
        IPLUS.clear()
        for i in I:
            IPLUS.append(deepcopy(i))
        for i in range(0, len(sDB)):
            if len(sDB[i]) > 0:
                for j in range(0, len(IPLUS[i].poset)):
                    apos = IPLUS[i].poset[j]
                    if len(apos.pos) == len(sub_ptn):
                        flag = 0
                        lt = -1
                        maxi = apos.pos[len(apos.pos) - 1]
                        a = maxi + sub_ptn[len(sub_ptn) - 1].min + 1
                        b = maxi + sub_ptn[len(sub_ptn) - 1].max + 1
                        if b > len(sDB[i]) - 1:
                            b = len(sDB[i]) - 1
                        if a > len(sDB[i]):
                            continue
                        if maxi <= b:
                            for h in range(maxi + 1, a):
                                if self.belong(sDB[i][h], self.s):
                                    flag = 1
                                    break
                            if flag == 0:
                                lt = self.next(sDB[i], p, maxi, a, b)
                        if lt != -1 and lt <= b:
                            for m in range(j, -1, -1):
                                if len(apos.pos) < len(IPLUS[i].poset[m].pos) and \
                                        IPLUS[i].poset[m].pos[len(apos.pos)] == lt:
                                    m += 1
                                    break
                                if m == 0:
                                    IPLUS[i].poset[j].pos.append(lt)
                                    support += 1
                                    break
        return support

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

    def output(self):
        output_file = open(self.output_filepath + "/" + self.output_filename, 'w')
        for fre in self.Fre:
            for c in fre.ptn:
                output_file.write(c)
            output_file.write(" ")

    def solve(self, text):
        text.insert(END, "GSgrow-a算法开始运行，请等待...\n")
        text.insert(END, "算法参数：\n")
        text.insert(END, "强字符集：" + self.s + " 中字符集：" + self.m + " 弱字符集：" + self.w + "\n")
        text.insert(END,
                    "mingap:" + str(self.mingap) + " maxgap:" + str(self.maxgap) + " minsup:" + str(self.minsup) + "\n")
        compnum = 0
        f_level = 1
        freArr = []

        begin_time = time.time()

        self.min_freItem()
        self.Fre = []
        for e in self.eSet:
            P = []
            I = []
            P.append(e)
            support = self.SizeOneSup(self.sDB, P, I)
            self.mineFre(support, self.sDB, P, I)
        end_time = time.time()
        time_consuming = end_time - begin_time
        freNum = 0
        text.insert(END, "GSgrow-a算法运行完毕。\n")
        for fre in self.Fre:
            for c in fre.ptn:
                text.insert(END, c)
            text.insert(END, " ")
        text.insert(END, "\nThe number of frequent patterns:" + str(len(self.Fre)) + "\n")
        text.insert(END, "The time-consuming:" + str(time_consuming * 1000) + "ms" + "\n")
        text.insert(END, "The number of calculation:" + str(self.compnum) + "\n")
        self.output()
        text.insert(END, "挖掘结果已写入：" + self.output_filepath + "/" + self.output_filename + "\n")

    def solve_test(self):
        print("GSgrow-a算法开始运行，请等待...")
        print("算法参数：")
        print("强字符集：" + self.s + " 中字符集：" + self.m + " 弱字符集：" + self.w)
        print("mingap:" + str(self.mingap) + " maxgap:" + str(self.maxgap) + " minsup:" + str(self.minsup))
        compnum = 0
        f_level = 1
        freArr = []

        begin_time = time.time()

        self.min_freItem()
        self.Fre = []
        for e in self.eSet:
            P = []
            I = []
            P.append(e)
            support = self.SizeOneSup(self.sDB, P, I)
            self.mineFre(support, self.sDB, P, I)
        end_time = time.time()
        time_consuming = end_time - begin_time
        freNum = 0
        print("GSgrow-a算法运行完毕。\n")
        for fre in self.Fre:
            for c in fre.ptn:
                print(c, end="")
            print(" ", end="")
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
    GSgrow_a(file, s, m, w, min_gap, max_gap, min_sup).solve_test()
    # NTP_Miner("D:\\github\\Pattern-Mining\\NTP-Miner\\NTP-DataSet\\SDB6.txt", "hilkmftwv", "rcqgpsyn", "adeuox", 0, 3, 400).solve_test()