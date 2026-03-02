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

variable_Num=0
dataset = []
txt = ""

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
    global txt
    sequence = []
    for j in range(len(dataset) - 1):
        for i in range(variable_Num):
            try:
                volatility = (float(dataset[j + 1][i] - dataset[j][i]) / dataset[j][i])
                # print(volatility)
            except:
                volatility = 0
            volatility = round(volatility, 2)
            if -0.01 <= volatility < 0.01:
            # if volatility==0:
                txt += " "+str(i+1)+"s"
                #series.append("s")
            elif volatility<0:
                #series.append("d")
                txt += " "+str(i+1)+"d"
            else:
                #series.append("u")
                txt += " "+str(i+1)+"u"
        txt = txt + " -1"
        #sequence.append(series)









if __name__ == '__main__':
    f = open('SDB8')
    dataRead(f)
    dataPro()
    with open('SDB8-syb.txt', 'w') as f:
        f.write(txt)
    #print(txt, file=f)
    #f.write("覆盖写入")


