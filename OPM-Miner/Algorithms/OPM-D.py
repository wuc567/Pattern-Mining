# -*-coding:utf-8 -*-
# pip install x -i https://pypi.tuna.tsinghua.edu.cn/simple/

"""
# File       : OFP-D.py
# Time       ：2023/12/27 16:38
# Description：深度优先生成候选模式，验证模式连接策略高效性
"""

import time
import itertools
import copy
import operator
import memory_profiler
import psutil
import os
import sys

# 维数，本文为三元：u=up,s=stable,d=down
character_Num = 3
# dataset存储整个原始数据集
dataset = []
# 频繁字典
P = {}
minsup = 40

# 读入原始数据集
def dataRead():
    global variable_Num
    f = open('F:/Pycharm/PyCharm 2023.1/time series/dataset/datauuu/SDB9')
    line = f.readline()  # 以行的形式进行读取文件
    while line:
        a = map(float, line.split())
        dataset.append(list(a))
        line = f.readline()
    variable_Num = len(dataset[0])  # 变量数
    f.close()


# 数据预处理，初始化字典
def dataPro():
    global sequence_Num
    sequence = []
    for i in range(variable_Num):
        series = []
        for j in range(len(dataset) - 1):
            try:
                volatility = (float(dataset[j + 1][i] - dataset[j][i]) / dataset[j][i])
            except:
                volatility = 0
            volatility = round(volatility, 2)
            if -0.01 <= volatility < 0.01:
                # if volatility==0:
                series.append("s")
            elif volatility < 0:
                series.append("d")
            else:
                series.append("u")
        sequence.append(series)

    # 初始化字典
    sequence_Num = len(sequence[0])
    for i in range(variable_Num):
        for j in range(sequence_Num):
            if (str([[i + 1, sequence[i][j]]])) not in P.keys():
                P[str([[i + 1, sequence[i][j]]])] = [None] * sequence_Num
            P[str([[i + 1, sequence[i][j]]])][j] = True
    for key in list(P.keys()):
        if support_count(P[key]) < minsup:
            del P[key]


def support_count(binarylist):
    return binarylist.count(True)

def show():
    s = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
          'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
          'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '2', '3', '4', '5', '6', '7', '8', '9', '$', '%', '!', '@',
          '#', '^', '&', '(', ')', '~', '`', '<', '>', '/', '?', ';', ':', '"', '', '', '', '', '', '', '',
          '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
          '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
          '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
          '', '', '', '', '', '', '', '', '', '•', '', '', '', '', '', '', '', '',
          '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
          '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
          '', '', '', '0', 'Ʞ', 'Ɪ', 'Ɬ', 'Ɡ', 'Ɜ', 'Ɦ', 'ꞩ', 'Ꞩ', 'ꞧ', 'Ꞧ', 'ꞥ', 'ꭄ', 'ꭃ', 'ꭂ', 'ꭁ', 'ꭀ', 'ꬿ',
          'ꬾ', 'ꬽ', 'ꬼ', 'ꬻ', 'ꬺ', 'ꬹ', 'ꬸ', 'ꬷ', 'ꬶ', 'ꬵ', 'ꬴ', 'ꬳ', 'ꬲ', 'ꬱ', 'ꬰ', 'ꟿ', 'ꟾ', 'ꟽ', 'ꟼ', 'ꟻ', 'ꟺ', 'ꟹ',
          'ꟸ',
          'ꟷ', 'ꞷ', 'Ꞷ', 'ꞵ', 'Ꞵ', 'Ꭓ', 'Ʝ', 'Ʇ', 'Ꞥ', 'ꞣ', 'Ꞣ', 'ꞡ', 'Ꞡ', 'ꞟ', 'Ꞟ', 'ꞝ', 'Ꞝ',
          'ꞛ', 'Ꞛ', 'ꞙ', 'Ꞙ', 'ꞗ', 'Ꞗ', 'ꞕ', 'ꞔ', 'ꞓ', 'Ꞓ', 'ꞑ', 'Ꞑ', 'ꞏ', 'ꞎ', 'Ɥ', 'ꞌ', 'Ꞌ', 'ꞇ', 'ꞈ', 'Ꞇ', 'ꞅ', 'Ꞅ',
          'ꞃ',
          'Ꞃ', 'ꞁ', 'Ꞁ', 'ꝿ', 'Ꝿ', 'Ᵹ', 'ꝼ', 'Ꝼ', 'ꝺ', 'Ꝺ', 'ꝸ', 'ꝷ', 'ꝶ', 'ꝵ', 'ꝴ', 'ꝳ', 'ꝲ', 'ꝱ', 'ꝰ', 'ꝯ', 'Ꝯ', 'ꝭ',
          'Ꝭ', 'ꝫ',
          'Ꝫ', 'ꝩ', 'Ꝩ', 'ꝧ', 'Ꝧ', 'ꝁ', 'Ꝃ', 'ꝃ', 'Ꝅ', 'ꝅ', 'Ꝇ', 'ꝇ', 'Ꝉ', 'ꝉ', 'Ꝋ', 'ꝋ', 'Ꝍ', 'ꝍ', 'Ꝏ', 'ꝏ', 'Ꝑ', 'ꝑ',
          'Ꝓ', 'ꝓ', 'Ꝕ', 'ꝕ', 'Ꝗ',
          'ꝗ', 'Ꝙ', 'ꝙ', 'Ꝛ', 'ꝛ', 'Ꝝ', 'ꝝ', 'Ꝟ', 'ꝟ', 'Ꝡ', 'ꝡ', 'Ꝣ', 'ꝣ', 'Ꝥ', 'ꝥ', 'Ꝁ', 'ꜿ', 'ꜽ', 'Ꜽ', 'ꜻ', 'Ꜻ', 'ꜹ',
          'Ꜹ', 'ꜷ', 'Ꜷ', 'ꜵ', 'Ꜵ',
          'ꜳ', 'Ꜳ', 'ꜱ', 'ꜰ', 'ꜯ', 'Ꜯ', 'ꜭ', 'Ꜭ', 'ꜫ', 'Ꜫ', 'ꜩ', 'Ꜩ', 'ꜧ', 'Ꜧ', 'ꜥ', 'Ꜥ', 'ꜣ', 'Ꜣ', '꜡', '꜠', 'ꜟ', 'ꜞ',
          'ꜝ', 'ꜜ', '⸧', '⸨', '⸩', '⸪', '⸫',
          '⸬', '⸭', '⸮', 'ⸯ', '⸰', '⸱', '⸲', '⸳', '⸴', '⸵', '⸶', '⸷', '⸸', '⸹', '⸺', '⸼', '⸽', '⸾', '⸿', '⹀', '⹁', '⹂',
          ]
    new_keys = list(P.keys())
    for i in range(len(new_keys)):
        P[s[i]] = P.pop(new_keys[i])
    s.clear()



def Support_I(binarylist1, binarylist2):
    binarylist_new = []
    support = 0

    for i in range(len(binarylist1)):
        if binarylist1[i] and binarylist2[i]:
            binarylist_new.append(True)
            support += 1
        else:
            binarylist_new.append(False)

    return binarylist_new

def Support_S(CanPattern):
    itemset = {}
    oneoff = {}
    binarylists = []  # 存储单项集倒排索引表
    index = []  # 每个倒排表的索引记录
    redundancy = []

    Newcan=CanPattern.split(' - ')
    for i in range(len(Newcan)):
            binarylists.append(P[str(Newcan[i])])
            index.append(0)
            redundancy.append(sequence_Num - minsup)
    for i in range(len(Newcan)):
        for item in Newcan[i]:  # 判断是否有重复项
            if str(item) in itemset:
                oneoff[str(item)] = []
            else:
                itemset[str(item)] = {}
    matchedlist = [None] * sequence_Num

    support = 0
    i = 0

    while index[i] < sequence_Num and redundancy[i] > -1:
        # 为0时不可用，只有为1才可用
        if not binarylists[i][index[i]]:
            index[i] += 1
            continue

        '''
        当前项中的单项集个数和一次性列表中的键个数不同，说明存在重复单项，则需判定一次性条件，
        若当前项中没有重复项，则不必判定
        '''

        if oneoff:
            j = 0
            while j < len(Newcan[i]):
                if str(Newcan[i][j]) in oneoff and index[i] in oneoff[str(Newcan[i][j])]:  # 不满足一次性
                    index[i] += 1
                    redundancy[i] -= 1
                    j = 0
                    if index[i] >= sequence_Num or redundancy[i] <= -1:  # 非频繁提前终止
                        P[str(CanPattern)] = copy.deepcopy(matchedlist)
                        return support
                    continue

                if not binarylists[i][index[i]]:  # 为0
                    index[i] += 1
                    j = 0
                    if index[i] >= sequence_Num or redundancy[i] <= -1:  # 非频繁提前终止
                        P[str(CanPattern)] = copy.deepcopy(matchedlist)
                        return support
                    continue
                j += 1

            # 将匹配的位置写入一次性字典
            for item in Newcan[i]:
                if str(item) in oneoff:
                    oneoff[str(item)].append(index[i])

        index[i] += 1
        i += 1

        if i >= len(Newcan):  # 只有当最后一层匹配成功时，支持度才加1
            support += 1
            matchedlist[index[-1] - 1] = True
            i = 0
        else:
            if index[i] < index[i - 1]:
                oldindex = index[i]
                index[i] = index[i - 1]  # 位索引滑动策略
                redundancy[i] -= support_count(binarylists[i][oldindex:index[i - 1]])

    P[str(CanPattern)] = copy.deepcopy(matchedlist)
    return support


def deepGen(fp, FP, FP1):
    global CanNum
    for item in FP1:  # item: str
        pattern = fp + " - " + item  # S连接**************************************
        CanNum += 1
        if Support_S(pattern) >= minsup:
            FP.append(pattern)
            deepGen(pattern, FP, FP1)
        if fp[-1] < item:  # I连接************************************
            CanNum += 1
            pattern = fp + '' + item
            pattern_array = fp.strip().split(' ')
            f = -1
            for i in range(len(pattern_array)):
                if pattern_array[i] == '-':
                    f = i
            s=''
            for i in range(f + 1, len(pattern_array)):
                matchlist=Support_I(P[item],P[pattern_array[i]])
                s+=pattern_array[i]
            s+=item
            P[s] = copy.deepcopy(matchlist)

            if Support_S(pattern) >= minsup:
                FP.append(pattern)
                deepGen(pattern, FP, FP1)



# 挖掘（长度为1的频繁-》S-连接-》I-连接）
def Min_FP():
    global CanNum,P,FP

    FP = []  # 存储频繁模式
    FP1 = []  # 存储长度为1的频繁模式 用于模式增长 a c
    CanNum = 0

    for i in P:  # a b c d e f
        CanNum += 1
        FP1.append(i)
        FP.append(i)

    for fp in FP1:  # fp: str
        deepGen(fp, FP, FP1)
    P.clear()



if __name__ == '__main__':

        dataRead()
        dataPro()
        show()
        old_time = time.time()
        Min_FP()
        new_time = time.time()
        print("共产生候选模式数量：{0}".format(CanNum))
        print("共产生频繁模式个数：{0}".format(len(FP)))
        print("运行时间为:%.2f s"%(float(new_time - old_time)))
        info = psutil.virtual_memory()
        print('内存使用：%.2f MB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024))

