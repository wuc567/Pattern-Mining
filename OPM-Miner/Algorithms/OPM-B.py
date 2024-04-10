# -*-coding:utf-8 -*-
# pip install x -i https://pypi.tuna.tsinghua.edu.cn/simple/

"""
# File       : OPM-B.py
# Time       ：2023/12/26 22:08
# Description：广度优先生成候选模式，验证模式连接策略高效性
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
minsup = 2

# 读入原始数据集
def dataRead():
    f = open('F:/Pycharm/PyCharm 2023.1/time series/dataddd/3h8l')
    global variable_Num
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
          'ꟸ', 'ꟷ', 'ꞷ', 'Ꞷ', 'ꞵ', 'Ꞵ', 'Ꭓ', 'Ʝ', 'Ʇ', 'Ꞥ', 'ꞣ', 'Ꞣ', 'ꞡ', 'Ꞡ', 'ꞟ', 'Ꞟ', 'ꞝ', 'Ꞝ',
          'ꞛ', 'Ꞛ', 'ꞙ', 'Ꞙ', 'ꞗ', 'Ꞗ', 'ꞕ', 'ꞔ', 'ꞓ', 'Ꞓ', 'ꞑ', 'Ꞑ', 'ꞏ', 'ꞎ', 'Ɥ', 'ꞌ', 'Ꞌ', 'ꞇ', 'ꞈ', 'Ꞇ', 'ꞅ', 'Ꞅ',
          'ꞃ', 'Ꞃ', 'ꞁ', 'Ꞁ', 'ꝿ', 'Ꝿ', 'Ᵹ', 'ꝼ', 'Ꝼ', 'ꝺ', 'Ꝺ', 'ꝸ', 'ꝷ', 'ꝶ', 'ꝵ', 'ꝴ', 'ꝳ', 'ꝲ', 'ꝱ', 'ꝰ', 'ꝯ', 'Ꝯ',
          'ꝭ',
          'Ꝭ', 'ꝫ', 'Ꝫ', 'ꝩ', 'Ꝩ', 'ꝧ', 'Ꝧ', 'ꝁ', 'Ꝃ', 'ꝃ', 'Ꝅ', 'ꝅ', 'Ꝇ', 'ꝇ', 'Ꝉ', 'ꝉ', 'Ꝋ', 'ꝋ', 'Ꝍ', 'ꝍ', 'Ꝏ', 'ꝏ',
          'Ꝑ',
          'ꝑ', 'Ꝓ', 'ꝓ', 'Ꝕ', 'ꝕ', 'Ꝗ', 'ꝗ', 'Ꝙ', 'ꝙ', 'Ꝛ', 'ꝛ', 'Ꝝ', 'ꝝ', 'Ꝟ', 'ꝟ', 'Ꝡ', 'ꝡ', 'Ꝣ', 'ꝣ', 'Ꝥ', 'ꝥ', 'Ꝁ',
          'ꜿ', 'ꜽ',
          'Ꜽ', 'ꜻ', 'Ꜻ', 'ꜹ', 'Ꜹ', 'ꜷ', 'Ꜷ', 'ꜵ', 'Ꜵ', 'ꜳ', 'Ꜳ', 'ꜱ', 'ꜰ', 'ꜯ', 'Ꜯ', 'ꜭ', 'Ꜭ', 'ꜫ', 'Ꜫ', 'ꜩ', 'Ꜩ', 'ꜧ',
          'Ꜧ', 'ꜥ', 'Ꜥ', 'ꜣ', 'Ꜣ',
          '꜡', '꜠', 'ꜟ', 'ꜞ', 'ꜝ', 'ꜜ', '⸧', '⸨', '⸩', '⸪', '⸫', '⸬', '⸭', '⸮', 'ⸯ', '⸰', '⸱', '⸲', '⸳', '⸴', '⸵', '⸶',
          '⸷', '⸸', '⸹', '⸺', '⸼',
          '⸽', '⸾', '⸿', '⹀', '⹁', '⹂', '⸥', '⸤', '⸣', '⸢', '⸠', '⸟', '⸞', '⸝', '⸜', '⸛', '⸙', '⸚', '⸘', '⸖', '⸕', '⸔',
          '⸓', '⸒', '⸑', '⸐', '⸏',
          '⸎', '⸍', '⸌', '⸋', '⸊', '⸉', '⸈', 'Ⱨ', 'ⱬ', 'Ɑ', 'Ɱ', 'Ɐ', 'Ɒ', 'ⱱ', 'Ⱳ', 'ⱳ', 'ⱴ', 'Ⱶ', 'ⱶ', 'ⱷ', 'ⱸ', 'ⱹ',
          'ⱺ', 'ⱻ', 'ⱼ',
          'ⱽ', 'Ȿ', 'Ɀ', '⸀', '⸁', '⸂', '⸃', '⸄', '⸅', '⸆', '⸇', 'ⱦ', 'ⱥ', 'Ɽ', 'Ᵽ', 'Ɫ', 'ⱡ', 'Ⱡ', '♯', '♫', '♪', '♦',
          '♥', '♣', '♠', '♂',
          '♀', '☼', '☻', '☺', '◦', '◙', '◘', '●', '◌', '○', '◊', '◄', '▼', '►', '▲', '▬', '▫', '▪', '╖', '╗', '╘', '╙',
          '╚', '╛', '╜', '╝',
          '╞', '╟', '╠', '╡', '╢', '╣', '╤', '╥', '╦', '╧', '╨', '╩', '╪', '╫', '╬', '▀', '▄', '█', '▌', '▐', '░', '▒',
          '▓', '■', '□',
          '╕', '╔', '╓', '╒', '║', '═', '┼', '┴', '┬', '┤', '├', '┘', '└', '┐', '┌', '│', '─', '⌡', '⌠', '⌐', '⌂', '≥',
          '≤', '≡', '≠', '≈',
          '∫', '∩', '∟', '∞', '√', '∙', '∕', 'ⅷ', 'ⅸ', 'ⅹ', 'ⅺ', 'ⅻ', 'ⅼ', 'ⅽ', 'ⅾ', 'ⅿ', 'ↀ', 'ↁ', 'ↂ', 'Ↄ', 'ↄ', 'ↅ',
          'ↆ', 'ↇ',
          'ↈ', '↉', '↊', '↋', '←', '↑', '→', '↓', '↔', '↕', '∂', '∆', '∏', '∑', '−', 'ⅶ', 'ⅵ', 'ⅴ', '↨', 'ⅳ', 'ⅲ', 'ⅱ',
          'ⅰ',
          'Ⅻ', 'Ⅺ', 'Ⅹ', 'Ⅸ', 'Ⅷ', 'Ⅶ', 'Ⅵ', 'Ⅴ', 'Ⅳ', 'Ⅲ', 'Ⅱ', 'Ⅰ', '⅟', '⅞', '⅝', '⅜', '⅛', '⅚', '⅙', '⅘', '⅗', '⅖',
          'ℵ', 'ℶ',
          'ℷ', 'ℸ', 'ℹ', '℺', '℻', 'ℼ', 'ℽ', 'ℾ', 'ℿ', '⅀', '⅁', '⅂', '⅃', '⅄', 'ⅅ', 'ⅆ', 'ⅇ', 'ⅈ', 'ⅉ', '⅊', '⅋', '⅌',
          '⅍', 'ⅎ', '⅏',
          '⅐', '⅑', '⅒', '⅓', '⅔', '⅕', 'ℴ', 'ℳ', 'Ⅎ', 'ℱ', 'ℰ', 'ℯ', '℮', 'ℭ', 'ℬ', 'Å', 'K', '℩', 'ℨ', '℧', 'Ω', '℥',
          'ℤ', '℣',
          '™', '℡', '℠', '℟', '℞', 'ℝ', 'ℜ', 'ℛ', 'ℚ', 'ℙ', '℘', '℗', '№', 'ℕ', '℔', '₴', '₵', '₶', '₷', '₸', '₹', '₺',
          '₻', '₼', '₽',
          '₾', '₿', '⃰', '℀', '℁', 'ℂ', '℃', '℄', '℅', '℆', '℈', '℉', 'ℊ', 'ℋ', 'ℌ', 'ℍ', 'ℎ', 'ℏ', 'ℐ', 'ℑ', 'ℒ', 'ℓ',
          '₳', '₲', '₱',
          '₰', '₯', '₮', '₭', '€', '₫', '₪', '₩', '₨', '₧', '₦', '₥', '₤', '₣', '₢', '₡', '₠', 'ₜ', 'ₛ', 'ₚ', 'ₙ', 'ₘ',
          'ₗ', 'ₕ', 'ₔ''ₓ', 'ₒ', 'ₑ',
          'ₐ', '⁰', 'ⁱ', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹', '⁺', '⁻', '⁼', '⁽', '⁾', 'ⁿ', '₀', '₁', '₂', '₃', '₄', '₅', '₆',
          '₇', '₈', '₉', '₊', '₋',
          '₌', '₍', '₎', '⁞', '⁝', '⁜', '⁛', '⁚', '⁙', '⁘', '⁗', '⁖', '⁕', '⁔''⁓', '⁒', '⁑', '⁐', '⁏', '⁎', '⁍', '⁌',
          '⁋', '⁊', '‰', '‱',
          '′', '″', '‴', '‵', '‶', '‷', '‸', '‹', '›', '※', '‼', '‽', '‾', '‿', '⁀', '⁁', '⁂', '⁃', '⁄', '⁅', '⁆', '⁇',
          '⁈', '⁉',
          '․', '‣', '‡', '†', '‟', '„', '”', '“', '‛', '‚', '’', '‘', '‗', '‖', '―', '–', '‒', '῾', '', '´', 'ῼ', 'Ώ',
          'Ὼ', 'Ό', 'Ὸ',
          'ῷ', 'ῶ', 'ῴ', 'ῳ', 'ῲ', '`', '΅', '῭', 'Ῥ', 'Ύ', 'Ὺ', 'Ῡ', 'Ῠ', 'ῧ', 'ῦ', 'ῥ', 'ῤ', 'ΰ', 'ι', '᾿', '῀', '῁',
          'ῂ', 'ῃ', 'ῄ', 'ῆ',
          'ῇ', 'Ὲ', 'Έ', 'Ὴ', 'Ή', 'ῌ', '῍', '῎', '῏', 'ῐ', 'ῑ', 'ῒ', 'ΐ', 'ῖ', 'ῗ', 'Ῐ', 'Ῑ', 'Ὶ', 'Ί', '῝', '῞', '῟',
          'ῠ', 'ῡ', 'ῢ', '᾽',
          'ᾼ', 'Ά', 'Ὰ', 'Ᾰ', 'ᾷ', 'ᾶ', 'ᾴ', 'ᾳ', 'ᾲ', 'ᾱ', 'ᾰ', 'ᾯ', 'ᾮ', 'ᾭ', 'ᾬ', 'ᾫ', 'ᾪ', 'ᾩ', 'ᾨ', 'ᾧ', 'ᾦ', 'ᾥ',
          'ᾤ', 'ᾣ', 'ᾢ', 'ᾡ',
          'ᾠ', 'ᾟ', 'ᾞ', 'ᾝ', 'ᾜ', 'ό', 'ὺ', 'ύ', 'ὼ', 'ώ', 'ᾀ', 'ᾁ', 'ᾂ', 'ᾃ', 'ᾄ', 'ᾅ', 'ᾆ', 'ᾇ', 'ᾈ', 'ᾉ', 'ᾊ', 'ᾋ',
          'ᾌ', 'ᾍ', 'ᾎ', 'ᾏ',
          'ᾐ', 'ᾑ', 'ᾒ', 'ᾓ', 'ᾔ', 'ᾕ', 'ᾖ', 'ᾗ', 'ᾘ', 'ᾙ', 'ᾚ', 'ᾛ', 'ὸ', 'ί', 'ὶ', 'ή', 'ὴ', 'έ', 'ὲ', 'ά', 'ὰ', 'Ὧ',
          'Ὦ', 'Ὥ', 'Ὤ', 'Ὣ',
          'ὦ', 'ὥ', 'ὤ', 'ὣ', 'ὢ', 'ὡ', 'ὠ', 'Ὗ', 'Ὕ', 'Ὓ', 'Ὑ', 'ὗ', 'ὖ', 'ὕ', 'Ἧ', 'ἰ', 'ἲ', 'ἶ',
          ]
    new_keys = list(P.keys())
    for i in range(len(new_keys)):
        P[s[i]] = P.pop(new_keys[i])
    s.clear()

# 挖掘（长度为1的频繁-》S-连接-》I-连接）
def Min_FP(P, minsup):
    global CanNum, FP
    FP = []  # 存储频繁模式
    FP1 = []  # 存储长度为1的频繁模式 用于模式增长 a c
    CanNum = 0

    for i in P:
        FP1.append(i)
        FP.append(i)
    # print(len(FP))
    # print(len(FP1))
    # print(FP1)

    for fp in FP:
        # print(CanNum)
        for item in FP1:
            # print(FP1)
            pattern = fp + " - " + item  # S连接**************************************
            CanNum += 1
            if Support_S(pattern) >= minsup:
                FP.append(pattern)

            if FP1.index(fp[-1]) < FP1.index(item):  # I连接************************************
                # print(fp[-1])
                pattern = fp + '' + item
                # print(pattern)
                CanNum += 1
                if ' - ' not in fp:
                    support, Slist = Support_I(P[fp], P[item])
                    P[str(pattern)] = copy.deepcopy(Slist)
                    if support >= minsup:
                        FP.append(pattern)
                else:
                    if Support_S(pattern) >= minsup:
                        FP.append(pattern)

    P.clear()



def Support_I(binarylist1, binarylist2):
    binarylist_new = []
    support = 0

    for i in range(len(binarylist1)):
        if binarylist1[i] and binarylist2[i]:
            binarylist_new.append(True)
            support += 1
        else:
            binarylist_new.append(False)

    return support, binarylist_new


def Support_S(CanPattern):
    itemset = {}
    oneoff = {}
    binarylists = []  # 存储单项集倒排索引表
    index = []  # 每个倒排表的索引记录
    redundancy = []

    Newcan = CanPattern.split(' - ')

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
    itemset.clear()

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



if __name__ == '__main__':
    dataRead()
    dataPro()
    show()
    old_time = time.time()
    Min_FP(P, minsup)
    new_time = time.time()
    print("共产生候选模式数量：{0}".format(CanNum))
    print("共产生频繁模式个数：{0}".format(len(FP)))
    print(FP)
    print("运行时间为:%.2fs" % (float(new_time - old_time)))
    info = psutil.virtual_memory()
    print('内存使用：%.2f MB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024))
