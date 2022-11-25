import copy
import threading
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from typing import TextIO
import operator
import time


class seqdb:
    id = 0
    S = ''

    def __init__(self, id, S):
        self.id = id
        self.S = S


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
    Fre = []

    def __init__(self, length, Fre):
        self.length = length
        self.Fre = Fre


class sub_ptn_struct:
    start = ''
    end = ''
    min = 0
    max = 0

    def __init__(self, start, end, min, max):
        self.start = start
        self.end = end
        self.min = min
        self.max = max


filename = ''
flag = 0
minsup = 0
mingap = 0
maxgap = 0

begin_time = 0
end_time = 0
eSet = []
NumbS = 0
nn = 0
Fre = []
sDB = []
list = []
minsup = 0
sub_ptn = []
compnum = 0
ptn_len = 0
AllFre = []
IPLUS = []


def min_freItem():
    global list
    global NumbS
    global eSet
    global nn
    counter = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0,
               'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0,
               'z': 0}  # 字符集
    for i in range(len(list)):
        for j in range(len(list[i])):
            if (list[i][j].islower() == 1) | (list[i][j].isupper() == 1):
                counter[list[i][j]] = counter[list[i][j]] + 1
    for key, value in counter.items():
        if value > 0:
            nn = nn + 1
            eSet.append(key)
    print(nn)


def SizeOneSup(P, I):
    global NumbS
    global sDB
    plen = len(P)
    support = 0
    if plen == 1:
        for i in range(NumbS):
            for l in range(len(sDB[i].S)):
                I.append(ISupSet(0, []))
                if sDB[i].S[l] == P[plen - 1]:
                    length = len(I[i].poset)
                    I[i].poset.append(Pos([]))
                    I[i].id = sDB[i].id
                    cand = Pos([])
                    cand.pos = [None for v in range(1)]
                    cand.pos[0] = l
                    I[i].poset[length] = cand
                    support = support + 1
    print('支持度为', support)
    return support


def disp_Fre(Fre):
    fsum = len(Fre)
    text01.delete('1.0', 'end')
    print('Fre = {')
    text01.insert('insert', 'Fre = {')
    if fsum > 1:
        for i in range(fsum - 1):
            flen = len(Fre[i].ptn)
            for j in range(flen):
                print(Fre[i].ptn[j])
                var = Fre[i].ptn[j]
                text01.insert('insert', var)
            print(',')
            text01.insert('insert', ',')
    i = i + 1
    if i == fsum - 1:
        flen = len(Fre[i].ptn)
        for j in range(flen):
            print(Fre[i].ptn[j])
            var = Fre[i].ptn[j]
            text01.insert('insert', var)
        print('}')
        text01.insert('insert', '}')
    print('\n')


def imax(x, y):
    if x > y:
        return x
    else:
        return y


def nextt(seq, p, maxx, a, b):
    i = imax(maxx + 1, a)
    flag = False
    while i <= b:
        if seq.S[i] == p:
            flag = True
            break
        i = i + 1
    if flag:
        return i
    else:
        return -1


def INSgrow_Gap(sub_ptn, I):
    global compnum
    global NumbS
    global sDB
    global IPLUS
    compnum = compnum + 1
    support = 0
    global ptn_len
    ptn_len = len(sub_ptn)
    p = sub_ptn[ptn_len - 1].end
    # kk = len(IPLUS)
    # while kk < len(I):
    #     IPLUS.append(ISupSet(0, []))
    #     kk = kk+1
    IPLUS = copy.deepcopy(I)
    # IPLUS = I
    for i in range(0, NumbS):
        if len(sDB[i].S) > 0:
            ptn_len = len(sub_ptn)
            for j in range(0, len(IPLUS[i].poset)):
                apos = Pos([])
                apos = IPLUS[i].poset[j]
                length = len(apos.pos)
                if length == len(sub_ptn):
                    maxx = apos.pos[length - 1]
                    a = 0
                    b = 0
                    l = -1
                    a = maxx + sub_ptn[ptn_len - 1].min + 1
                    b = maxx + sub_ptn[ptn_len - 1].max + 1
                    lens = len(sDB[i].S)
                    if b > lens - 1:
                        b = lens - 1
                    if a > len(sDB[i].S):
                        continue
                    if maxx <= b:
                        l = nextt(sDB[i], p, maxx, a, b)
                    if l != -1 and l <= b:
                        m = j
                        while m >= 0:
                            # if length > 0:
                            #     aa = len(IPLUS[i].poset[m].pos)
                            #     while aa <= length:
                            #         IPLUS[i].poset[m].pos.append(None)
                            #         aa = aa+1
                            # bb = len(IPLUS[i].poset)
                            # while bb <= m:
                            #     IPLUS[i].poset.append(Pos())
                            #     bb = bb+1
                            if length >= len(IPLUS[i].poset[m].pos):
                                if m == 0:
                                    # Iqlen = 0
                                    # for vv in range(len(IPLUS[i].poset[j].pos)):
                                    #     if IPLUS[i].poset[j].pos[vv] is not None:
                                    #         Iqlen = Iqlen+1
                                    IPLUS[i].poset[j].pos.append(l)
                                    # IPLUS[i].poset[j].pos[Iqlen] = l
                                    support = support + 1
                                    break
                            elif IPLUS[i].poset[m].pos[length] == l:
                                m = m + 1
                                break
                            if m == 0:
                                # Iqlen = 0
                                # for vv in range(len(IPLUS[i].poset[j].pos)):
                                #     if IPLUS[i].poset[j].pos[vv] is not None:
                                #         Iqlen = Iqlen+1
                                IPLUS[i].poset[j].pos.append(l)
                                # IPLUS[i].poset[j].pos[Iqlen] = l
                                support = support + 1
                                break
                            m = m - 1
    return support


def mineFre(support, P, I):
    global minsup
    global nn
    global eSet
    global sub_ptn
    global Fre
    global IPLUS
    Q = []
    if support >= minsup:
        fsum = len(Fre)
        plen = len(P)
        if plen == 2:
            lll = 5
        cand = Freq_ptn(0, [])
        cand.length = plen
        # cand.ptn = [None for v in range(plen)]
        cand.ptn = copy.deepcopy(P)
        Fre.append(cand)
        Q = [None for v in range(plen)]
        for t in range(plen):
            Q[t] = P[t]
        Q.append(None)
        for ee in range(nn):
            qlen = len(P) + 1
            Q[qlen - 1] = eSet[ee]
            sub_ptn = []
            for v in range(qlen - 1):
                sub_ptn.append(sub_ptn_struct('', '', 0, 0))
            # sub_ptn = [sub_ptn_struct('', '', 0, 0) for v in range(qlen-1)]
            k = 0
            while k < (qlen - 1):
                cand1 = sub_ptn_struct('', '', 0, 0)
                cand1.start = Q[k]
                cand1.min = mingap
                cand1.max = maxgap
                cand1.end = Q[k + 1]
                sub_ptn[k] = cand1
                k = k + 1
            # k = 0
            # for k in range(qlen - 1):
            #     cand1.start = Q[k]
            #     cand1.min = mingap
            #     cand1.max = maxgap
            #     cand1.end = Q[k + 1]
            #     sub_ptn[k] = cand1
            IPLUS = []
            support = INSgrow_Gap(sub_ptn, I)
            mineFre(support, Q, IPLUS)


def transform(Fre):
    global AllFre
    Fsum = len(Fre)
    if Fsum > 1:
        length = Fre[0].length
        for i in range(Fsum):
            if Fre[i].length > length:
                length = Fre[i].length
    AllFre = [All_Fre(0, []) for v in range(length)]
    for i in range(length):
        AllFre[i].length = i + 1
        AllFre[i].Fre = []
    for i in range(length):
        for j in range(Fsum):
            if Fre[j].length == AllFre[i].length:
                AFlen = len(AllFre[i].Fre)
                # AllFre[i].Fre = [Freq_ptn(0, []) for v in range(AFlen + 1)]
                AllFre[i].Fre.append(Freq_ptn(0, []))
                cand2 = Freq_ptn(0, [])
                cand2.ptn = copy.deepcopy(Fre[j].ptn)
                AllFre[i].Fre[AFlen] = cand2


def disp_AllFre(Fre):
    text01.insert('insert', '\n')
    print('All Frequent Patterns are as follows: ')
    text01.insert('insert', 'All Frequent Patterns are as follows:')
    text01.insert('insert', '\n')
    total = 0
    AFsum = len(AllFre)
    for t in range(AFsum):
        length = AllFre[t].length
        print('The length is ', length)
        text01.insert('insert', 'The length is ')
        text01.insert('insert', length)
        text01.insert('insert', '\n')
        fsum = len(AllFre[t].Fre)
        flen = len(AllFre[t].Fre[0].ptn)
        if flen == 1:
            for i in range(fsum):
                print(AllFre[t].Fre[i].ptn[0])
                text01.insert('insert', AllFre[t].Fre[i].ptn[0])
                text01.insert('insert', '\t')
            total = total + fsum
            text01.insert('insert', '\n')
        elif flen > 1:
            for i in range(fsum):
                for j in range(flen):
                    print(AllFre[t].Fre[i].ptn[j], end='')
                    text01.insert('insert', AllFre[t].Fre[i].ptn[j])
                print('\n')
                text01.insert('insert', '\t')
            total = total + fsum
            text01.insert('insert', '\n')
        print('The Number of Length ', length, 'is', fsum)
        # text01.insert('insert', '\n')
        text01.insert('insert', 'The Number of Length ')
        text01.insert('insert', length)
        text01.insert('insert', ' is ')
        text01.insert('insert', fsum)
        text01.insert('insert', '\n')
    print('The Total of AllFre is ', total)
    text01.insert('insert', 'The Total of AllFre is ')
    text01.insert('insert', total)
    btn04["fg"] = "grey"
    btn05["fg"] = "grey"
    btn06["fg"] = "grey"


def read_file():
    global list
    global NumbS
    global sDB
    f = open(filename)
    NumbS = 0
    line = f.readline()
    while line:
        list.append(line)
        NumbS = NumbS + 1
        line = f.readline()
    f.close()
    sDB = []
    for i in range(1000):
        sDB.append(seqdb(0, ''))
    for j in range(len(list)):
        sDB[j].id = j + 1
        sDB[j].S = list[j]
    print(NumbS)


def select_algorithm():
    global flag
    s = v.get()
    if s == 'SNP-Miner':
        flag = 1
        print('当前选择算法为：' + s)
    elif s == 'SNP-df':
        flag = 2
        print('当前选择算法为：' + s)
    elif s == 'SNP-bf':
        flag = 3
        print('当前选择算法为：' + s)
    elif s == 'SNP-nogap':
        flag = 4
        print('当前选择算法为：' + s)
    elif s == 'SNP-sn':
        flag = 5
        print('当前选择算法为：' + s)
    elif s == 'GSgrow':
        flag = 6
        print('当前选择算法为：' + s)


def select_file():
    global filename
    filename = askopenfilename(title="选择文件", initialdir="D", filetypes=[("文本文档", ".txt")])
    print('选择的文件为：', filename)
    # filename = filename[18:len(filename)]
    show["text"] = filename


def select_save_file(event):
    global save_filename
    save_filename = askdirectory(title="选择文件夹", initialdir='F:')
    print(save_filename)


def save_option(event):
    save_writename = open(save_filename + '/data_mining_result.txt', mode='w')
    result = text01.get("1.0", "end")
    save_writename.write(result)
    save_writename.close()


# 获取输入的阈值
def get_Threshold(event):
    global minsup
    t = entry01.get()
    str_list = ''.join(t)
    minsup = int(str_list)
    print('最小阈值为：', minsup)


def get_Mingap(event):
    global mingap
    t = entry02.get()
    str_list = ''.join(t)
    mingap = int(str_list)
    print('最小间隙为：', mingap)


def get_Maxgap(event):
    btn04["fg"] = "green"
    btn05["fg"] = "green"
    btn06["fg"] = "green"
    global maxgap
    t = entry03.get()
    str_list = ''.join(t)
    maxgap = int(str_list)
    print('最大间隙为：', maxgap)


def run(event):
    global list
    list = []
    global compnum
    compnum = 0
    global NumbS
    NumbS = 0
    global eSet
    eSet = []
    global nn
    nn = 0
    global Fre
    Fre = []
    global sDB
    sDB = []
    global sub_ptn
    sub_ptn = []
    compnum = 0
    global ptn_len
    ptn_len = 0
    global AllFre
    AllFre = []
    global IPLUS
    IPLUS = []
    t1 = threading.Thread(target=run_procedure)
    t1.start()


def run_procedure():
    # for i in range(100):
    #     Fre.append(Freq_ptn(0, []))
    read_file()
    begin_time = time.perf_counter()
    min_freItem()
    for e in range(nn):
        P = []
        P = [None for v in range(1)]
        I = []
        # for i in range(1000):
        #     I.append(ISupSet(0, []))
        P[0] = eSet[e]
        support = SizeOneSup(P, I)
        if e == 1:
            lll = 5
        mineFre(support, P, I)
    end_time = time.perf_counter()
    t = end_time - begin_time
    disp_Fre(Fre)
    transform(Fre)
    disp_AllFre(AllFre)
    print('The number of frequent patterns:', len(Fre))
    print('Time-consuming is : ', t, 's')
    print('The number of calculation: ', compnum)


if __name__ == '__main__':
    root = Tk()
    root.geometry("700x700")
    root.resizable(False, False)
    root.title("GSgrow")
    label00 = Label(root, text="GSgrow", height=2, width=20, fg="blue", bg="green",
                    font=("Times New Roman", 18, "bold", "italic"))
    label00.grid(row=0, column=1)

    label01 = Label(root, text="Choose an algorithm", font=("Times New Roman", 10))
    label01.grid(row=1, column=0, ipadx=0)
    label01["width"] = 22

    label02 = Label(root, text="Choose input file", font=("Times New Roman", 10))
    label02.grid(row=2, column=0, ipadx=0)
    label02["width"] = 22

    label03 = Label(root, text="Min.support", font=("Times New Roman", 10))
    label03.grid(row=3, column=0, ipadx=0)
    label03["width"] = 22

    label04 = Label(root, text="Mingap", font=("Times New Roman", 10))
    label04.grid(row=4, column=0, ipadx=0)
    label04["width"] = 22
    label05 = Label(root, text="Maxgap", font=("Times New Roman", 10))
    label05.grid(row=5, column=0, ipadx=0)
    label05["width"] = 22

    v = StringVar(root)
    v.set("GSgrow")
    om = OptionMenu(root, v, "GSgrow")
    om["width"] = 25
    om.grid(row=1, column=1)

    btn01 = Button(root, text="?", command=select_algorithm, width=5)
    btn01.grid(row=1, column=2)

    btn02 = Button(root, text="...", command=select_file, width=5)
    btn02.grid(row=2, column=2)

    show = Label(root, width=40, height=1, relief="raised")
    show.grid(row=2, column=1)
    show["text"] = "文件名"

    v2 = IntVar()
    v2.set(5000)
    entry01 = Entry(textvariable=v2, width=40)
    entry01.grid(row=3, column=1)

    btn03 = Button(root, text="确定")
    btn03.grid(row=3, column=2)
    btn03["width"] = 5
    btn03.bind("<Button-1>", get_Threshold)

    v3 = IntVar()
    v3.set(0)
    entry02 = Entry(textvariable=v3, width=40)
    entry02.grid(row=4, column=1)

    btn07 = Button(root, text="确定")
    btn07.grid(row=4, column=2)
    btn07["width"] = 5
    btn07.bind("<Button-1>", get_Mingap)

    v4 = IntVar()
    v4.set(30)
    entry03 = Entry(textvariable=v4, width=40)
    entry03.grid(row=5, column=1)

    btn08 = Button(root, text="确定")
    btn08.grid(row=5, column=2)
    btn08["width"] = 5
    btn08.bind("<Button-1>", get_Maxgap)

    btn04 = Button(root, text="Run Algorithm", relief="groove", fg="grey")
    btn04.grid(row=6, column=1)
    btn04["width"] = 20
    btn04.bind("<Button-1>", run)
    text01 = Text(root, width=50, height=20, relief="raised", font=("Times New Roman", 12, "bold", "italic"))
    text01.grid(row=7, column=1)

    btn05 = Button(root, text="选择文件夹", fg="grey", width=10)
    btn05.grid(row=8, column=0)

    btn06 = Button(root, text="保存", fg="grey", width=5)
    btn06.grid(row=8, column=2)

    btn05.bind("<Button-1>", select_save_file)
    btn06.bind("<Button-1>", save_option)

    root.mainloop()
