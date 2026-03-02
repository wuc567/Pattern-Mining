#coding=utf-8
def operateDataFile(fn):  # 处理序列数据库
    global sequenceid
    dataTableTemp = []
    itemlst=[]
    with open(fn, 'r') as f2:
        sequenceid = 0
        itemsetnum=0
        for sequence in f2.readlines():
            dataTableTemp.append([])
            sequence = sequence.split("\n")[0]
            sequenceL = sequence.split("-1")
            itemsetid = 0
            for itemset in sequenceL[0:-1]:
                dataTableTemp[sequenceid].append([])
                itemsetL = itemset.split(" ")
                for item in itemsetL:
                    if item and item != " " and item!="-2":
                        dataTableTemp[sequenceid][itemsetid].append(item)
                        itemlst.append(item)
                # if dataTableTemp[sequenceid][itemsetid] == []:
                #     dataTableTemp[sequenceid].pop(itemsetid)
                else:
                    itemsetnum += 1
                itemsetid += 1
            sequenceid += 1
    return dataTableTemp,itemsetnum

# 存储各编号在各序列各项集中出现的位置
# 例如字符‘10002’在第一个序列第二、三个项集中出现，且在第二个序列第一个项集中出现，
# 则记录为{"10002":{"1":[2,3], "2": [1]}}
def operateDataFile1(fn):  # 处理序列数据库
    global sequenceId
    dataTableTemp = {}
    itemSetnum=0
    sequenceId = 0  # 纪录序列号
    with open(fn, 'r') as f2:
        for sequence in f2.readlines():
            string = ""  # 用于记录读取出的字符串
            itemSetsId = 0  # 纪录项号 项号从0开始
            # sequenceIdString = str(sequenceId) + ""  # 用于将序列号改成字符串类型
            for letter in sequence:
                # 各编号数据之间用空格间隔
                if letter != " " and string != "-1":
                    string += letter
                elif string == "-1":  # 判断该数据是否为"-1"，如果是，代表该多项集结束
                    string = ""
                    itemSetsId += 1
                    itemSetnum+=1
                elif string == "-2":
                    break
                    # 如果字符k不是空格则继续扫描j，字符串str也不是“-1”，继续扫描字符串， 并将字符k加入字符串str中
                elif letter == " ":
                    item=string
                    if item not in dataTableTemp.keys():
                        dataTableTemp[item] = {}
                    if sequenceId not in dataTableTemp[item].keys():
                        dataTableTemp[item][sequenceId] = [[itemSetsId]]
                    else:
                        if itemSetsId not in dataTableTemp[item][sequenceId][0]:
                            dataTableTemp[item][sequenceId][0].append(itemSetsId)
                    string = ""
            sequenceId = sequenceId + 1  # 每扫描f2文件一行，代表一个序列，并且序列号+1
    return dataTableTemp,itemSetnum


def operateDataFile2(fn):
    # global sequenceid
    n=0
    sequenceid = 0
    dataTableTemp = {}
    seqnum={}
    seqnum1=0
    with open(fn, 'r') as f2:
        itemsetnum=0
        for sequence in f2.readlines():
            seqnum1+=1
            sequence = sequence.split("\n")[0]
            sequenceL = sequence.split("-1")
            itemsetnum+=len(sequenceL)-1
            seqnum[sequenceid]=len(sequenceL)-1
            for i in range(len(sequenceL)-1):
                itemsetL = sequenceL[i].split(" ")
                for item in itemsetL:
                    if item and item != " " and item != "-2":
                        tmp=item
                        n+=1
                        if tmp not in dataTableTemp.keys():
                            dataTableTemp[tmp] = {}
                        if sequenceid not in dataTableTemp[tmp].keys():
                            dataTableTemp[tmp][sequenceid] = [i]
                        else:
                            if i not in dataTableTemp[tmp][sequenceid]:
                                dataTableTemp[tmp][sequenceid].append(i)
            sequenceid+=1
    return dataTableTemp,itemsetnum,seqnum1,n,len(dataTableTemp.keys())


if __name__ == '__main__':
    str1 = "../data/exam.txt"
    # str2 = "../data/exam1.txt"
    # a = operateDataFile(str1)
    # b = operateDataFile1(str1)
    c = operateDataFile2(str1)
    # d=operateDataFile2(str2)
    # print(a)
    # print('-------------------------------------------------------------------------------------------------------------')
    # print(b)
    # print('-------------------------------------------------------------------------------------------------------------')
    print(c)
    # print(d)
