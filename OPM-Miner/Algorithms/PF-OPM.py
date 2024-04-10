# -*-coding:utf-8 -*-
# pip install x -i https://pypi.tuna.tsinghua.edu.cn/simple/

"""
# File       : RNP-OFM.py
# Time       ：2023/12/22 20:40
# Description：使用RNP算法中的位置字典来进行对比，验证二进制位置字典的有效性
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


# 读入原始数据集
def dataRead(f):
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
    global sequence_Num,sequence
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
                series.append('s')
            elif volatility < 0:
                series.append("d")
            else:
                series.append("u")
        sequence.append(series)
        # print(sequence)
    ss = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
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
    # k = -character_Num
    # print(sequence)
    for i in range(variable_Num):
        ss.pop(0)
        ss.pop(0)
        ss.pop(0)
        for j in range(len(sequence[0])):
            if sequence[i][j] == 's':
                sequence[i][j] = ss[0]
                continue
            if sequence[i][j] == 'd':
                sequence[i][j] = ss[1]
                continue
            if sequence[i][j] == 'u':
                sequence[i][j] = ss[2]
                continue
    sequence = [[row[i] for row in sequence] for i in range(len(sequence[0]))]
    # print(sequence)
    ss.clear()


# 计算出现列表的支持度
def support_count(binarylist):
    return len(binarylist)


def Mine_SizeOne():
    global OFP_Sizeone, CanNum,sequence,OFP
    sequence = [sequence]
    OFP=[]
    OFP_Sizeone = []
    CanNum = variable_Num * character_Num
    item=[]
    for i in range(len(sequence)):
        for j in range(len(sequence[i])):
            for k in range(len(sequence[i][j])):
                if [[sequence[i][j][k]]] not in item:
                    item.append([[sequence[i][j][k]]])
    for i in item: #得到频繁单项
        if Support(i) >=minsup:
            OFP_Sizeone.append(i)
            OFP.append(i)
            # print(OFP)
    while OFP_Sizeone != []:
        FP = []
        for i in OFP_Sizeone:
            for j in OFP_Sizeone:
                CanPattern = Join_I(i, j)
                if CanPattern :
                    CanNum += 1
                    # print((PFSupport(CanPattern)))
                    if Support(CanPattern) >= minsup:
                        FP.append(CanPattern)
        if FP != []:
            OFP_Sizeone = copy.deepcopy(FP)
            OFP.extend(FP)
        else:
            break
def Support(pattern):
    global sequence
    sss = copy.deepcopy(sequence)
    supportValue = 0
    for s in sss:
        position = []
        for ks in range(0, len(pattern)):
            position.append([])
        i = 0
        j = len(pattern) - 1
        while i < len(s):
            if set(pattern[j]).issubset(set(s[i])):
                if j == 0:
                    for k in pattern[0]:
                        if k in s[i]:
                            s[i].remove(k)
                    position[j].append(i)
                    j = len(pattern) - 1
                    i += 1
            else:
                if j == 0:
                    i += 1
                    j = len(pattern) - 1
        if i == len(s):
            supportValue += len(position[len(pattern) - 1])
    return supportValue


# 项集模式连接策略
def itemPatternJoin(pattern1, pattern2):
    CanPattern=[]
    suffer = copy.deepcopy(pattern1[0][1:])
    prefix = copy.deepcopy(pattern2[0][:-1])
    if suffer != prefix:
        return False

    CanPattern.extend(pattern1[0])
    CanPattern.append(pattern2[0][-1])
    return [CanPattern]


def Join_I(pattern1, pattern2):
    if len(pattern1[0])==1:
        if pattern1[0][-1] >= pattern2[0][0]:
            return False
    else :
        if pattern1[0][-1] < pattern2[0][0]:
            return False


    return itemPatternJoin(pattern1, pattern2)


def Mine_SizeMore():
    global OFP_num, OFP, CanNum,sequence
    size = 1
    OFP_num = len(OFP)
    # print(OFP)
    print("size {0}: num:{1}  ".format(size, OFP_num))
    while OFP != []:
        FP = []
        for item in OFP:
            for jtem in OFP:
                CanPattern = Join_S(item, jtem)
                if CanPattern :
                    CanNum += 1
                    if PFSupport(CanPattern) >= minsup:
                        # print(CanPattern)
                        FP.append(CanPattern)
        if FP:
            OFP = copy.deepcopy(FP)
            OFP_num += len(FP)
            size += 1
            print("size {0}: num:{1}  ".format(size, support_count(FP)))
            # print(FP)
        else:
            break


def Join_S(pattern1, pattern2):
    CanPattern = []
    suffer = copy.deepcopy(pattern1[1:])
    prefix = copy.deepcopy(pattern2[:-1])
    if suffer != prefix:
        return False

    CanPattern.extend(pattern1)
    CanPattern.append(pattern2[-1])
    return CanPattern

'''判断模式每一个项集是否在序列项集中，即（bc）是否在（abc）中,s是item，p是列表;
如果p=(bc)(c),s中有（bc）,其中的c被先用了，则再次使用的时候这个s中的bc就不满足一次性条件了'''
''''''
def isinitem(s,p):
    i = 0
    j = 0
    while i < len(s) and j<len(p):
        if set(p[j]).issubset(set(s[i])):
            j += 1
        i += 1
    if j == len(p):
        return True
    else:
        return False


def PFSupport(p):
    global sequence,flag,itemset
    itemset = {}
    pos=[]
    sup = 0
    s = sequence[0]
    for i in range(len(p)):
        pos.append([])
        for item in p[i]:
            itemset[str(item)] = [0] * len(s)

    for i in range(0, len(p)):
        for j in range(0, len(s)):
            if isinitem(s[j], p[i]):
                pos[i].append(j)

    i = 0
    f = 0
    b = 0
    while i < len(s):
        j = 0
        while j < len(p) and i < len(s):
            if i in pos[j] and unused(i, p[j]):
                used(i, p[j])
                if f == 0:
                    b = i
                    f = 1
                j += 1
            if j == len(p):
                sup += 1
                if sup>=minsup:
                    return sup
                f = 0
                i = b
            i += 1

    return sup

def unused(i,p):
    global itemset
    for item in p:
        if itemset[item][i]==1:
            return False
    return True

def used(i,p):
    global itemset
    for item in p:
        itemset[item][i]=1


if __name__ == '__main__':
    f = open('F:/Pycharm/PyCharm 2023.1/time series/dataset/datauuu/SDB9')
    minsup = 40
    dataRead(f)
    dataPro()
    old_time = time.time()
    Mine_SizeOne()
    Mine_SizeMore()
    new_time = time.time()

    print("共产生候选模式数量：{0}".format(CanNum))
    print("共产生频繁模式个数：{0}".format(OFP_num))
    print("运行时间为:%.2fs" % (float(new_time - old_time)))
    info = psutil.virtual_memory()
    print('内存使用：%.2f MB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024))




