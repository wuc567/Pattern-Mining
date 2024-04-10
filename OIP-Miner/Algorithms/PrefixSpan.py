import copy     #用与深拷贝
import time
import dataprocess as dp
from memory_profiler import memory_usage

def getElem(dataList):      #求出这个数据集的所有不同的元素
    elem = []
    for i in dataList[:]:
        for j in i[:]:
            for k in j[:]:
                if k not in elem:       #这个元素没有出现过，就添加如这个列表
                    elem.append(k)

    elem = sorted(elem)     #排序
    #print(elem)
    return elem

def deleteNotFreElem(data, notFreElem):     #从数据集中删除出现次数不频繁的元素
    if len(notFreElem) == 0:
        return


    for i in data[:]:
        for j in i[:]:
            for k in j[:]:
                if k in notFreElem:
                    x = data.index(i)
                    y = i.index(j)
                    z = j.index(k)          #上面3行，获取这个元素所在的位置
                    data[ x ][ y ].remove(k)        #获取到位置后，移除这个不频繁的元素
        while [] in i:
            i.remove([])       #要是删除后，某个项变为空列表，就删除这个空列表
    while [] in data:
        data.remove([])        #要是删除后，某个项变为空列表，就删除这个空列表

    #print(data)
    return

def getPrefixData(e, data): #得到前缀投影的数据库
    copyData = list(copy.deepcopy(data))    #要用深拷贝deepcopy，深拷贝是创建一块地址，内容和原来一样，但两个完全没联系
                                  #浅拷贝copy  只是地址不同，但一个变化，另一个可能会变化？在这个里面是
                                                #若列表里全是不可变元素，则浅拷贝和深拷贝差不多
    flage = 0 #一个标志变量                     #但若列表里包含可变元素，如字典，多维列表，等，那浅拷贝就不合适了，得用深拷贝
    for i in copyData[:]:
        for j in i[:]:
            for k in j[:]:
                if len(j) <= 1:     #如果这一行的某一个项，只有 1 个元素，若不相等直接去除就是了
                    if e != k:
                        j.remove(k)     #如果不是e就移除，直到 k==e 时，停止
                    else:
                        j.remove(k)
                        flage = 1   #一个标志变量，如果 k==e ，则设置为 1 ，此时退出循环，加入 下一条 数据，去除它的前缀
                        break
                else:
                    if e != k:
                        j.remove(k)
                    else:
                        j.remove(k)
                        j[0] = '_'+j[0]         #这一行的某一个项的元素个数不是1个，当 k==e 时，去掉k，并且要在前面加下划线 ‘_’
                        flage = 1
                        break
            while [] in i:
                i.remove([])    #在求后缀过程中，某个项集成了空，就删除这个空的，别让它占位置

            if flage == 1:
                flage = 0       #进入下一条数据时，要把它置0
                break
    while [] in copyData:
        copyData.remove([])             #在求后缀过程中，某个项集成了空，就删除这个空的，别让它占位置
    #print(copyData)
    return copyData

#得到elem中每个元素的新的数据集，（就是在这个dataList数据集中，依次去掉每个元素，形成的新的数据集，为了递归往下挖掘）
def getAllPrefixData( elem, prefixE, dataList):
    data1 = list(copy.deepcopy(dataList))   #深拷贝一封数据集
    allPrefixData = []  #是一个四维列表，每一列都是在原来的数据集中，去除prefixE这个前缀后形成的新的数据集

    for e in elem:
        if set('_').issubset(e):        #  例如 _e 和 e 可不是同一个元素，要分开讨论
            temp = useCycleGetPrefixData(e, prefixE, data1)
            allPrefixData.append(temp)
        else:
            temp2 = getPrefixData( e,data1)
            allPrefixData.append( temp2 )   #求出 e 的后缀数据库后，加入这个类别

    return allPrefixData

#求某个前缀的 频繁元素 与 非频繁元素
def useCycleGetFreElem(dataList, prefixE, elem, minsup):     #如果是第一次循环，没有前缀，那么 prefixE就置为 -1

    elemsup = {}    #存放每个不同元素的出现次数，要尤其注意 _e  和 e 的区别
    for e in elem:
        for i in dataList[:]:
            for j in i:
                if set('_').issubset(e):      #  _e  和 e 的区别，   想想下划线是怎么来的，就是某个项集有2个元素及以上时，前缀字母删除后，加的下划线，这个下划线其实就是这个前缀字母
                    temp = e[1]
                    if set([prefixE, temp]).issubset(set(j)):   #当有下划线时，要格外注意，这个时候对 _e 计数，要看当前字面上一个元素是不是前缀元素，如果是，_e加1
                        elemsup[e] = elemsup.get(e, 0) + 1
                if e in j:
                    elemsup[e] = elemsup.get(e, 0) + 1
                    break
    #print(elemsup)
    freElem = []
    notFreElem = []
    global count
    for i in elemsup.keys():
        count += 1
        if elemsup[i] >= minsup:    #分辨频繁元素和非频繁元素
            freElem.append(i)
        else:
            notFreElem.append(i)
    #print(freElem)
    #print(elemsup)
    return freElem, notFreElem

def useCycleGetPrefixData(e,prefixE, data):  #这个是在带前缀的情况下，求某元素的投影
    copyData = list(copy.deepcopy(data))    #要用深拷贝deepcopy，深拷贝是创建一块地址，内容和原来一样，但两个完全没联系

    flage = 0   #标志变量，如果为1，表示循环要进入下一条数据记录
    for i in copyData[:]:
        for j in i[:]:
            if set('_').issubset(e):
                if set([prefixE, e[1]]).issubset(set(j)):   #下划线本来就是一个占位符，表示前缀字母，现在又变回来了了
                    for l in j[:]:
                        if (l == prefixE) or (l == e[1]):   #如果这个 两个字母 整体 在这个项集里，就把这个整体都移除，形成下一个前缀的投影，也就是新的数据记录
                            j.remove(l)
                    break
            for k in j[:]:
                if len(j) <= 1:
                    if e != k:
                        j.remove(k)
                    else:
                        j.remove(k)
                        flage = 1
                        break
                else:
                    if e != k:
                        j.remove(k)
                    else:
                        j.remove(k)
                        j[0] = '_'+j[0]
                        flage = 1
                        break
            while [] in i:
                i.remove([])

            if flage == 1:
                flage = 0
                break
    while [] in copyData:
        copyData.remove([])
    #print(copyData)
    return copyData


def cycleGetFreElem(preFixData, e, minsup):     #递归调用，求出频繁序列
    copyPreFixData = list(copy.deepcopy(preFixData))
    allFreSequence = [  ]    #存放这个项集的所有频繁序列,然后返回

    allElem = getElem(copyPreFixData)  #返回所有 单个 元素
    #print(allElem)
    freElem, notFreElem = useCycleGetFreElem(copyPreFixData, e, allElem, minsup)    #求某个前缀数据库的频繁元素，和GetFreElem基本一样，就是多了个参数
    #print(freElem, notFreElem)
    deleteNotFreElem(copyPreFixData, notFreElem)    #从数据集删除非频繁元素
    thisAllPrefixData = getAllPrefixData(freElem, e, copyPreFixData)    #得到这个元素的投影数据库，这个函数是为了循环专用的函数
    #print(thisAllPrefixData)

    for x in freElem:
        if set('_').issubset(set(x)):   #有下划线就把下划线在换为前缀字母，这个整体是在一起的
            newElem = [     [e , x[1]]    ]
            allFreSequence.append( newElem )    #生成频繁序列
        else:
            temp2 = [[e],[x]]       #没下划线，就分开放，在同一个序列，但是不在同1个项集
            allFreSequence.append( temp2 )      #生成频繁序列，加入

    lengthFreElem = len(freElem)
    for i in range(lengthFreElem):
        temp = cycleGetFreElem(thisAllPrefixData[i], freElem[i], minsup)    #递归调用，求下一个前缀的频繁序列，返回它的频繁序列
        for x in temp:  # x 就是表示它的前缀，是一个序列
            if set('_').issubset(x[0][0]):      #如果有下划线一定在最前面
                t = copy.deepcopy(x)
                t[0] = [e , str(t[0][0])[1] ]   #有下划线就把下划线在换为 前缀字母，这个整体是在一起的
                allFreSequence.append( t )
            else:
                t2 = copy.deepcopy(x)
                t2.insert(0, [e])   #没有下划线，就把前缀放入第一个位置
                allFreSequence.append(t2)

        #allFreElem.append(list(temp))
    #print(allFreSequence)
    return allFreSequence

def prefixSpan():       #prefixSpan流程
    elem = getElem( mydata )  #得到数据集中所有不同的元素
    freElem, notFreElem = useCycleGetFreElem(mydata,'-1', elem, minsup)   #返回的是列表，不含支持度,一个是频繁项，一个是非频繁项，没有前缀就把 prefixE这个变量置为-1
    #print(freElem, notFreElem)         #  ['a', 'b', 'c', 'd', 'e', 'f'] ['g']
    deleteNotFreElem(mydata, notFreElem)      #从数据集中删除不频繁的元素
    #print(dataList)
    allPrefixData = getAllPrefixData(freElem, '-1' , mydata)      #返回每个频繁元素的后缀数据库，用一个4维列表表示
    #print(allPrefixData)

    allListFreSequence = []      #也是收集所有的频繁序列，不过是列表表示，为了输出好看点，特意弄的
    lengthFreElem = len(allPrefixData)
    for x in range(lengthFreElem):
        l = cycleGetFreElem(allPrefixData[x], freElem[x], minsup)   #循环递归，得到频繁序列
        l.insert(0, [[freElem[x]]])     #把当前循环的前缀字母放入列表最前面
        #print(l)
        allfreSequence[freElem[x]] = l
        allListFreSequence.append(l)#收集所有的频繁序列，不过是用列表表示，为了输出好看点，特意弄的，当然你可以不用写

    # for lengthE in range(lengthFreElem):    #这就是一个输出，我为了输出好看一点才加的，嫌麻烦就不用写下面这个循环了
    #     print(freElem[lengthE],'这个前缀的，它的频繁序列见下面--------------->>>>>>>>>>')
    #     for x in allListFreSequence[lengthE]:
    #         print(x)

    #print(allfreSequence)

def ReadFile(file):
    fileresult = dp.operateDataFile(file)
    sdb=fileresult[0]
    itemsetnum=fileresult[1]
    return sdb,itemsetnum

if __name__ == '__main__':
    # readFileName='../SDBdata/E-Shop5000.txt'
    org = ['../SDBdata/Babysale.txt',
           '../SDBdata/E-Shop5000.txt',
           '../SDBdata/OnlineRetail_II_best.txt',
           '../SDBdata/Online.txt',
           '../SDBdata/PM2.5.txt',
           '../SDBdata/Sign.txt',
           '../SDBdata/Leviathan.txt',
           '../SDBdata/BF.txt']
    # org=['../SDBdata/PM2.5.txt']
    sh = [0.083, 0.08, 0.04, 0.022, 0.0324, 0.008, 0.008, 0.014]
    # sh=[0.0324]
    for i in range(len(org)):
        supthreshold=sh[i]
        count = 0
        allfreSequence = {}  # 收集所有的频繁序列
        start = time.time()
        # print(mydata)
        mydata, itemsetnum = ReadFile(org[i])
        minsup = supthreshold * itemsetnum
        # q = prefixSpan( mydata, int(minsup) )
        a=memory_usage(prefixSpan,max_usage=True)
        end = time.time()
        FPcount = 0
        for x in allfreSequence:   #输出
            # print(x,'::', q[x])
            FPcount += len(allfreSequence[x])
        print('支持度：',minsup)
        print('频繁模式数量:' + str(FPcount))
        print('候选模式数量:' + str(count))
        print('运行时间：', end - start, 's')
        print('内存使用：', a, 'Mb')


