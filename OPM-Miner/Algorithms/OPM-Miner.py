# -*-coding:utf-8 -*-
# pip install x -i https://pypi.tuna.tsinghua.edu.cn/simple/

"""
# File       : OFP-Miner.py
# Time       ：2023/12/22 17:54
# Description： 主算法
"""

import time
import itertools
import copy
import operator
import memory_profiler
import psutil
import os
import sys

from memory_profiler import profile

# 维数，本文为三元：u=up,s=stable,d=down
character_Num = 3
# 支持度阈值

# dataset存储整个原始数据集
dataset = []
# 频繁字典
dic = {}


# 读入原始数据集
def dataRead(f):
    global variable_Num
    line = f.readline()  # 以行的形式进行读取文件
    while line:
        a = map(float, line.split())
        dataset.append(list(a))
        line = f.readline()
    variable_Num = len(dataset[0])  # 变量数
    # print(variable_Num)
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
                # print(volatility)
            except:
                volatility = 0
            volatility = round(volatility, 2)
            if -0.01 <= volatility < 0.01:
            # if volatility==0:
                series.append("s")
            elif volatility<0:
                series.append("d")
            else :
                series.append("u")
        sequence.append(series)


    #初始化字典
    sequence_Num = len(sequence[0])
    # print(sequence_Num)
    for i in range(variable_Num):
        for j in range(sequence_Num):
            if (str([[i+1,sequence[i][j]]])) not in dic.keys():
                dic[str([[i+1,sequence[i][j]]])] = [None] * sequence_Num
            dic[str([[i+1,sequence[i][j]]])][j] = True



#计算二进制出现列表的支持度
def support_count(binarylist):
    return binarylist.count(True)


def Mine_SizeOne():
    global  OFP_Sizeone,CanNum
    OFP_Sizeone=[]
    CanNum = 0
    # print(dic)
    # 计算每个项的支持度,得到频繁Sizeone模式
    for key in list(dic.keys()):
        if support_count(dic[key])>= minsup:
            OFP_Sizeone.append(eval(key))  # Sizeone频繁模式列表
            # print("{0}:{1}".format(key, support_count(dic[key])))
        else:
            del dic[key]
    # print(dic)
    while OFP_Sizeone!=[]:
        FP = []
        for item in OFP_Sizeone:
            for jtem in OFP_Sizeone:
                CanPattern = Join_I(item, jtem)
                if CanPattern :
                    CanNum += 1
                    support,binarylist = Support_I(dic[str(item)],dic[str(jtem)])
                    if support >= minsup:
                        FP.append(CanPattern)
                        dic[str(CanPattern)] = copy.deepcopy(binarylist)
                        # print("{0}:{1}".format(CanPattern,support_count(dic[str(CanPattern)])))

        if FP!=[]:
            # print(1)
            OFP_Sizeone=copy.deepcopy(FP)
        else:
            break


#项集模式连接策略
def itemPatternJoin(pattern1,pattern2):
    CanPattern=[]

    suffer = copy.deepcopy(pattern1[1:])
    prefix = copy.deepcopy(pattern2[:-1])
    if suffer != prefix:
        return False

    CanPattern.extend(pattern1)
    CanPattern.append(pattern2[-1])
    return CanPattern



def Join_I(pattern1, pattern2):
    # 两个项集的最后一项要保证第一个的变量小于第二个
    if pattern1[-1][0] >= pattern2[-1][0]:
        return False
    else:
        return itemPatternJoin(pattern1, pattern2)


def Support_I(binarylist1, binarylist2):
    binarylist_new = []
    support=0

    for i in range(len(binarylist1)):
        if binarylist1[i] and binarylist2[i]:
            binarylist_new.append(True)
            support+=1
        else:
            binarylist_new.append(False)

    return support,binarylist_new


def Mine_SizeMore():
    global  OFP_num, OFP,CanNum
    size = 1
    OFP_num = len(dic)
    # for i in dic.keys():
    #     print("{0} : {1}".format(i, support_count(dic[i])))
    # print(dic.keys())
    # print("size {0}: num:{1}  ".format(size, OFP_num))
    OFP = [[eval(x)] for x in dic.keys()]  # 升维

    while OFP!=[] :
        # print(CanNum)
        FP = []
        for item in OFP:
            for jtem in OFP:
                CanPattern = Join_S(item, jtem)
                if CanPattern :
                    CanNum += 1
                    if Support_S(CanPattern) >= minsup:
                        FP.append(CanPattern)
                        # print("{0}:{1}".format(CanPattern, Support_S(CanPattern)))

        if FP:
            OFP = copy.deepcopy(FP)
            OFP_num +=len(FP)
            size+=1
            print("size {0}: num:{1}  ".format(size, len(FP)))
        else:
            break


def Join_S(pattern1, pattern2):
    return itemPatternJoin(pattern1, pattern2)


def Support_S(CanPattern):
    # print(CanPattern)
    itemset = {}  # 存储所有项，判断重复性
    oneoff = {} #一次性字典，存储重复项信息
    binarylists = []  # 存储单项集倒排索引表
    index = []  # 每个倒排表的索引记录
    redundancy = []

    for i in range(len(CanPattern)):
        binarylists.append(dic[str(CanPattern[i])])
        index.append(0)
        redundancy.append((support_count(binarylists[i])) - minsup)

        for item in CanPattern[i]:  # 判断是否有重复项
            if str(item) in itemset:
                oneoff[str(item)] = []
            else:
                itemset[str(item)]={}


    support = 0
    i = 0

    while index[i] < sequence_Num and redundancy[i] > -1:
        #为0时不可用，只有为1才可用
        if not binarylists[i][index[i]]:
            index[i] += 1
            continue

        '''
        存在重复项，则需判定一次性条件，
        不存在重复项，则不必判定
        '''
        if oneoff:
            j = 0
            while j < len(CanPattern[i]):
                if str(CanPattern[i][j]) in oneoff and index[i] in oneoff[str(CanPattern[i][j])]: #不满足一次性
                    index[i] += 1
                    redundancy[i] -= 1
                    j = 0
                    if index[i] >= sequence_Num or redundancy[i] <= -1:  #非频繁提前终止
                        return support
                    continue

                if not binarylists[i][index[i]]: #为0
                    index[i] += 1
                    j = 0
                    if index[i] >= sequence_Num or redundancy[i] <= -1: #非频繁提前终止
                        return support
                    continue
                j += 1

            # 将匹配的位置写入一次性字典
            for item in CanPattern[i]:
                if str(item) in oneoff:
                    oneoff[str(item)].append(index[i])

        index[i] += 1
        i += 1

        if i >= len(CanPattern):  # 只有当最后一层匹配成功时，支持度才加1
            support += 1
            # if support >= minsup:  #频繁提前终止
            #     return support
            i = 0
        else:
            if index[i] < index[i - 1]:
                oldindex = index[i]
                index[i] = index[i - 1]  #位索引滑动策略
                redundancy[i] -= support_count(binarylists[i][oldindex:index[i - 1]])
    return support




if __name__ == '__main__':
    # fn = [['F:/Pycharm/PyCharm 2023.1/time series/dataset/SDB1'],
    #       ['F:/Pycharm/PyCharm 2023.1/time series/dataset/SDB2'],
    #       ['F:/Pycharm/PyCharm 2023.1/time series/dataset/SDB3'],
    #       ['F:/Pycharm/PyCharm 2023.1/time series/dataset/SDB4'],
    #       ['F:/Pycharm/PyCharm 2023.1/time series/dataset/SDB5'],
    #       ['F:/Pycharm/PyCharm 2023.1/time series/dataset/SDB6'],
    #       ['F:/Pycharm/PyCharm 2023.1/time series/dataset/SDB7'],
    #       ['F:/Pycharm/PyCharm 2023.1/time series/dataset/SDB8'],
    #      ]
    # sup = [6500,140,805,3700,81,12300,17,820]
    # for i in range(0,len(fn)):
    #     f=open(fn[i][0])
    #     minsup=sup[i]
    #     print(i+1)
    f = open('F:/Pycharm/PyCharm 2023.1/time series/dataset/datauuu/SDB1')
    minsup =4300
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

