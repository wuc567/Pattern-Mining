import threading
from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from typing import TextIO
import operator
import time

minsup = 0
sequence_num = 0  # 序列长度
sigmasize = 0  # 字符集的长度
sigma = []
compnum = 0
frenum = 0
list = []  # 序列列表
len_seq = []
SeqDB = [[] for _ in range(100)]
freArr = [[] for _ in range(100)]
f_level = 1
begin_time = 0
end_time = 0
filename = ''
flag = 0  # 算法选择标志
level = 1
save_filename = ''


class node:
    name = 0
    min_leave = 0
    max_leave = 0
    parent = []
    children = []
    used = False
    toleave = False

    def __init__(self, name, min_leave, max_leave, parent, children, used, toleave):
        self.name = name
        self.min_leave = min_leave
        self.max_leave = max_leave
        self.parent = parent
        self.children = children
        self.used = used
        self.toleave = toleave


class percharsequence:
    store = []
    len = 0

    def __init__(self, store):
        self.store = store
        self.len = len(store)


class sorted_incomplete_nettree:
    name = ''
    pos_sup = 0
    intree = []

    def __init__(self, name, pos_sup, intree):
        self.name = name
        self.pos_sup = pos_sup
        self.intree = intree


def calculate_intree(ic_ntree, next_level, position, sid):
    size = len(ic_ntree)
    store = []
    store = SeqDB[position][sid].store
    ch_size = len(store)
    # print(size, ch_size)
    k = 0
    for j in range(size):
        parent = ic_ntree[j]
        while k < ch_size:
            child = store[k]
            if child > parent:
                next_level.append(child)
                k = k + 1
                break
            k += 1
        if k == ch_size:
            break


def calculate_intreeone(ic_ntree, next_level, position, sid):
    size = len(ic_ntree)
    # ic_ntree为第position位字符在第sid个序列中出现的位置集合
    store = []
    # store存储的是第position位字符在第sid个序列中的位置集合
    store = SeqDB[position][sid].store
    ch_size = len(store)
    # print(size, ch_size)
    k = 0
    for j in range(size):
        parent = ic_ntree[j]
        while k < ch_size:
            child = store[k]
            if child == parent + 1:
                next_level.append(child)
                k = k + 1
                break
            k += 1
        if k == ch_size:
            break


def other_level(sub_pattern, position, pattern):
    pattern.intree.clear()
    occnum = 0
    # print(position)
    for sid in range(sequence_num):
        # current_len = len_seq[sid]
        atree = percharsequence([])
        if flag == 4:
            calculate_intreeone(sub_pattern.intree[sid].store, atree.store, position, sid)
        else:
            calculate_intree(sub_pattern.intree[sid].store, atree.store, position, sid)
        atree.len = len(atree.store)
        # print(atree.len)
        occnum = occnum + atree.len
        pattern.intree.append(atree)
    # print(occnum)
    return occnum


def binary_search(level, cand, low, high):
    if low > high:
        return -1
    while low <= high:
        mid = (low + high) // 2
        # result = operator.eq(cand, freArr[level - 1][mid].name[0:level - 1])
        if cand == freArr[level - 1][mid].name[0:level - 1]:
            slow = low
            shigh = mid
            # flag = -1
            if cand == freArr[level - 1][low].name[0: level - 1]:
                start = low
            else:
                while slow < shigh:
                    start = (slow + shigh) // 2
                    # sresult = operator.eq(cand, freArr[level - 1][start].name[0:level - 1])
                    if cand == freArr[level - 1][start].name[0:level - 1]:
                        shigh = start
                        # flag = 0
                    else:
                        slow = start + 1
                start = slow
            return start
        elif cand < freArr[level - 1][mid].name[0:level - 1]:
            high = mid - 1
        else:
            low = mid + 1
    return -1


def gen_candidateone(level):
    global compnum
    global minsup
    global sigmasize
    global sigma
    size = len(freArr[level])
    for k in range(size):
        Q = freArr[level][k].name
        for i in range(len(freArr[0])):
            cand = sorted_incomplete_nettree('', 0, [])
            compnum = compnum + 1
            cand.name = Q
            cand.name = cand.name + freArr[0][i].name
            for t in range(sigmasize):
                if freArr[0][i].name[0] == sigma[t]:
                    position = t
                    break
            cand.pos_sup = other_level(freArr[level][k], position, cand)
            if cand.pos_sup >= minsup:
                freArr[level + 1].append(cand)


def gen_candidate(level):
    global compnum
    size = len(freArr[level - 1])
    start = 0
    for i in range(size):
        Q = ''
        R = ''
        R = freArr[level - 1][i].name[1:level]
        Q = freArr[level - 1][start].name[0:level - 1]
        if Q != R:
            start = binary_search(level, R, 0, size - 1)
        if start < 0 | start >= size:
            start = 0
        else:
            Q = freArr[level - 1][start].name[0:level - 1]
            while Q == R:
                compnum = compnum + 1
                cand = sorted_incomplete_nettree('', 0, [])
                cand.name = freArr[level - 1][i].name[0:level]
                cand.name = cand.name + freArr[level - 1][start].name[level - 1:level]
                global sigmasize
                global sigma
                for t in range(sigmasize):
                    if freArr[level - 1][start].name[level - 1] == sigma[t]:
                        position = t
                        break
                cand.pos_sup = other_level(freArr[level - 1][i], position, cand)
                if cand.pos_sup >= minsup:
                    freArr[level].append(cand)
                start = start + 1
                if start >= size:
                    start = 0
                    break
                Q = freArr[level - 1][start].name[0:level - 1]


def first_level(position, pattern):
    occnum = 0
    for sid in range(sequence_num):
        # storeS = []
        # storeS = SeqDB[position][sid].store
        pattern.intree = SeqDB[position]
        occnum = occnum + len(pattern.intree[sid].store)
    return occnum


def dealingfirstlevel(freArr):
    # global freArr
    global compnum
    for i in range(sigmasize):
        current_pattern = sorted_incomplete_nettree('', 0, [])
        compnum = compnum + 1
        current_pattern.name = sigma[i]
        current_pattern.pop_sup = first_level(i, current_pattern)
        if current_pattern.pop_sup >= minsup:
            # print(current_pattern.pop_sup)
            freArr[0].append(current_pattern)


def mineFre(subp):
    global compnum
    for e in range(len(freArr[0])):
        cand = sorted_incomplete_nettree('', 0, [])
        cand.name = subp.name + freArr[0][e].name
        compnum = compnum + 1
        for t in range(sigmasize):
            if freArr[0][e].name[0] == sigma[t]:
                position = t
                break
        cand.pos_sup = other_level(subp, position, cand)
        if cand.pos_sup >= minsup:
            freArr[level].append(cand)
            mineFre(cand)


def store_into_vec():
    global list
    global len_seq
    # print(list)
    for sid in range(sequence_num):
        # temp = [percharsequence]
        # a = percharsequence([])
        # temp = [a for x in range(0, 100)]
        temp = []
        for i in range(100):
            temp.append(percharsequence([]))
        ss = ''
        current_sequence = percharsequence([])
        current_sequence.len = len(list[sid])
        len_seq.append(current_sequence.len)
        ss = list[sid]
        b = percharsequence([])
        for i in range(current_sequence.len):
            for j in range(sigmasize):
                if ss[i] == sigma[j]:
                    temp[j].store.append(i)
                    break
        for i in range(sigmasize):
            temp[i].len = len(temp[i].store)
            SeqDB[i].append(temp[i])


def min_sigma():
    global sequence_num
    global sigmasize
    global sigma
    global list
    counter = {'a': 0, 'b': 0, 'c': 0, 'd': 0, 'e': 0, 'f': 0, 'g': 0, 'h': 0, 'i': 0, 'j': 0, 'k': 0, 'l': 0, 'm': 0,
               'n': 0, 'o': 0, 'p': 0, 'q': 0, 'r': 0, 's': 0, 't': 0, 'u': 0, 'v': 0, 'w': 0, 'x': 0, 'y': 0,
               'z': 0}  # 字符集
    for i in range(len(list)):
        for j in range(len(list[i])):
            if (list[i][j].islower() == 1) | (list[i][j].isupper() == 1):
                counter[list[i][j]] = counter[list[i][j]] + 1
    for key, value in counter.items():
        if value > 0:
            sigmasize = sigmasize + 1
            sigma.append(key)
    print(sigmasize)


def read_file():
    global list
    global sequence_num
    global sigmasize
    global filename
    f = open(filename)
    sequence_num = 0
    line = f.readline()
    while line:
        # print(line)
        list.append(line)
        sequence_num = sequence_num + 1
        # print(len(line))
        line = f.readline()
    f.close()
    print(sequence_num)


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


def select_file():
    global filename
    filename = askopenfilename(title="选择文件", initialdir="D", filetypes=[("文本文档", ".txt")])
    print(filename)
    # filename = filename[18:len(filename)]
    show["text"] = filename


def select_save_file(event):
    global save_filename
    save_filename = askdirectory(title="选择文件夹", initialdir='F:')
    print(save_filename)


def save_option(event):
    save_writename = open(save_filename + '/mining_result.txt', mode='w')
    result = text01.get("1.0", "end")
    save_writename.write(result)
    save_writename.close()


# 获取输入的阈值
def get_Threshold(event):
    btn04["fg"] = "green"
    btn05["fg"] = "green"
    btn06["fg"] = "green"
    global minsup
    t = entry01.get()
    str_list = ''.join(t)
    minsup = int(str_list)
    print(minsup)


def run(event):
    global sequence_num
    sequence_num = 0
    global sigma
    sigma = []
    global list
    list = []
    global len_seq
    len_seq = []
    global sigmasize
    sigmasize = 0
    global f_level
    f_level = 1
    global frenum
    frenum = 0
    global SeqDB
    SeqDB = [[] for _ in range(100)]
    global freArr
    freArr = [[] for _ in range(100)]
    global level
    level = 1
    global compnum
    compnum = 0
    t1 = threading.Thread(target=run_procedure)
    t1.start()


def run_procedure():
    global frenum
    global begin_time
    global end_time
    global flag
    read_file()
    min_sigma()
    store_into_vec()
    begin_time = time.perf_counter()
    dealingfirstlevel(freArr)
    global f_level
    if flag == 1 or flag == 4:
        f_level = 1
        gen_candidate(f_level)
        while len(freArr[f_level]) != 0:
            f_level = f_level + 1
            gen_candidate(f_level)
    elif flag == 3:
        f_level = 0
        gen_candidateone(f_level)
        f_level = f_level + 1
        while len(freArr[f_level]) != 0:
            gen_candidateone(f_level)
            f_level = f_level + 1
    elif flag == 2:
        for e in range(len(freArr[0])):
            mineFre(freArr[0][e])
    end_time = time.perf_counter()
    # print(f_level)
    if flag == 1 or flag == 4 or flag == 3:
        for i in range(f_level):
            for j in range(len(freArr[i])):
                print(freArr[i][j].name + '     ', end="")
                frenum = frenum + 1
            print()
        print('\n')
        print('The number of frequent patterns:', frenum, '\n')
        print('The time-consuming:', end_time - begin_time, '\n')
        print('The number of calculation:', compnum, '\n')
    elif flag == 2:
        for i in range(2):
            for j in range(len(freArr[i])):
                print(freArr[i][j].name + '     ', end="")
                frenum = frenum + 1
        print('\n')
        print('The number of frequent patterns:', frenum, '\n')
        print('The time-consuming:', end_time - begin_time, '\n')
        print('The number of calculation:', compnum, '\n')
    for i in range(sigmasize):
        print(sigma[i], '\t')
    text01.delete("1.0", "end")
    if flag == 1 or flag == 4 or flag == 3:
        for i in range(f_level):
            for j in range(len(freArr[i])):
                var = freArr[i][j].name + '  ',
                text01.insert('insert', var)
            text01.insert('insert', '\n')
        text01.insert('insert', '\n')
        ss = 'The number of frequent patterns: '
        text01.insert('insert', ss)
        text01.insert('insert', frenum)
        text01.insert('insert', '\n')
        ss1 = 'The number of calculation: '
        text01.insert('insert', ss1)
        text01.insert('insert', compnum)
        text01.insert('insert', '\n')
        ss2 = 'The time-consuming: '
        text01.insert('insert', ss2)
        ee = (end_time - begin_time) * 1000
        ee1 = str(ee)
        text01.insert('insert', ee1)
        text01.insert('insert', 'ms')
        text01.insert('insert', '\n')
    elif flag == 2:
        for i in range(2):
            for j in range(len(freArr[i])):
                var = freArr[i][j].name + '  ',
                text01.insert('insert', var)
            text01.insert('insert', '\n')
        text01.insert('insert', '\n')
        ss = 'The number of frequent patterns: '
        text01.insert('insert', ss)
        text01.insert('insert', frenum)
        text01.insert('insert', '\n')
        ss1 = 'The number of calculation: '
        text01.insert('insert', ss1)
        text01.insert('insert', compnum)
        text01.insert('insert', '\n')
        ss2 = 'The time-consuming: '
        text01.insert('insert', ss2)
        ee = (end_time - begin_time) * 1000
        ee1 = str(ee)
        text01.insert('insert', ee1)
        text01.insert('insert', 'ms')
        text01.insert('insert', '\n')


if __name__ == '__main__':
    root = Tk()
    root.geometry("700x600")
    root.resizable(False, False)
    root.title("SNP-Miner")
    label00 = Label(root, text="SNP-Miner", height=2, width=20, fg="blue", bg="green",
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

    v = StringVar(root)
    v.set("SNP-Miner")
    om = OptionMenu(root, v, "SNP-nogap", "SNP-Miner", "SNP-bf", "SNP-df")
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
    v2.set(4300)
    entry01 = Entry(textvariable=v2, width=40)
    entry01.grid(row=3, column=1)

    btn03 = Button(root, text="确定")
    btn03.grid(row=3, column=2)
    btn03["width"] = 5
    btn03.bind("<Button-1>", get_Threshold)
    btn04 = Button(root, text="Run Algorithm", relief="groove", fg="grey")
    btn04.grid(row=4, column=1)
    btn04["width"] = 20
    btn04.bind("<Button-1>", run)
    text01 = Text(root, width=50, height=20, relief="raised", font=("Times New Roman", 12, "bold", "italic"))
    text01.grid(row=5, column=1)

    btn05 = Button(root, text="选择文件夹", fg="grey", width=10)
    btn05.grid(row=6, column=0)

    btn06 = Button(root, text="保存", fg="grey", width=5)
    btn06.grid(row=6, column=2)

    btn05.bind("<Button-1>", select_save_file)
    btn06.bind("<Button-1>", save_option)

    root.mainloop()
