import re

class processingData(object):
    def read_file(self, readfilename):
        # 读取的文件名字
        # readFileName = "../dateset/demo.txt"
        lines_s = []
        with open(readfilename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                lines_s.append(line.strip())
        f.close()
        return lines_s  # 返回数组

    # 将数组写入文件
    def write_file(self, lines_s, filename):
        with open(filename, 'w') as f:
            for i in range(len(lines_s)):
                f.writelines(str(i) + "\t" + lines_s[i])
                f.write("\n")
    # 项集去重 排序
    # sort_items  去重排序后的项集数组
    # items_no_repeat  存在重复的未排序的项集数组
    def item_sotrd(self, items):
        items_no_repeat = []
        for item in items:
            if item not in items_no_repeat:
                items_no_repeat.append(item)
        # self.write_file(items_no_repeat, 'item_norepeat.txt')
        sort_items = list(sorted(items_no_repeat))
        # 去重排序后的项集
        # print(sort_items)
        # print(type(sort_date))
        return sort_items, items_no_repeat

    # 定义空的数据字典
    '''
    S =
    {
    'a': [[0, 1, 3], [1], [0, 2, 4], [0, 1], [1, 3]],
    'b': [[], [0], [2], [0], [4]],
    'c': [[0, 1, 2, 3, 4], [1, 2], [0, 2, 3, 4, 5], [0, 1, 2, 3], [0, 1, 2, 3, 5]],
    'd': [[], [3], [0], [], [0, 3]],
    'e': [[], [1, 3], [4, 5], [3, 4], [5]],
    'f': [[], [0], [1, 4], [4], []]
    }
    '''

    def item_to_dict(self, sort_items, len_lines, S):
        # sort_items 排序去重之后的项
        # len_lines 序列数
        # S = {}
        for i in sort_items:
            # S[i] = {}
            S[i] = [[] for i in range(len_lines)]
            # S[str(i)]['mul'] = [[] for i in range(len_lines)]
        # print (S)
        return S

    # 替换字符串为项集(按字符串的大小)
    def replace_seq(self, lines_s, sort_item):
        # print(sort_item)
        # print(lines_s)
        flag = 1
        for i in range(len(sort_item)):
            for j in range(len(lines_s)):
                if flag == 1:
                    lines_s[j] = lines_s[j] + " "
                # lines_s[j] = lines_s[j].replace(sort_item[i], str(i))
                p1 = re.compile(" " + sort_item[i] + " ")
                lines_s[j], number = re.subn(p1, " " + str(i) + "* ", lines_s[j])
            # print(lines_s)
            # print(number)
            # print_array(lines_s)
            flag = 0
        for i in range(len(lines_s)):
            lines_s[i] = lines_s[i].replace('*', '')
        return lines_s

    # 分割字符串数组返回[]和[[],[],[]]
    def split_array(self, lines):
        # lines =  0 2 -1 0 2 -1 2 -1 0 2 -1 2
        lines = lines.replace('  ', ' ')
        # print(lines)
        items_array = lines.strip().split(' ')  # 按空格分隔成一个一个的项和-1
        # print(items_array)
        s_array = [[]]  # 二维数组
        i = 0
        for item in items_array:
            if item != '-1':
                s_array[i].append(item)
            else:
                i = i + 1
                s_array.append([])
        # print(s_array)
        return items_array, s_array

    #  lines  0 2 -1 0 2 -1 2 -1 0 2 -1 2
    #  items_array  ['0', '2', '-1', '0', '2', '-1', '2', '-1', '0', '2', '-1', '2']
    #  s_array  [['0', '2'], ['0', '2'], ['2'], ['0', '2'], ['2']]

    def Statistics_items(self, lines, items):
        # lines =  "177 179 410 454 468 470 474 475 513 588 871 872 873 1142 1011 1107  -1 854 854 854  -1 730 761 859 861 864 870 918 919 927  -1 436 1199  -1 859  -1 919  -1 70 153 217 235 255 256 283 318 360 361 376 436 464 464 693 736 736 736 737 751 775 776 777 800 801 871 872 881 888 900 910 916 940 1039 1094 1116  -1 139 262 301 325 452 477 497 711 1034 1097 1099 1179 1107 1154  -1 119 120 121 548 642 691 776 817 837 848 910 911 912 917 919 966 1099 966B  -1 248 362 427 451 460 470 494 495 588 594 595 659 660 662 663 664 665 666 667 679 680 691 691 692 693 694 695 696 699 704 708 708 708 761 775 776 777 778 799 840 841 871 872 873 887 888 909 912 1088 1095 1135  -1 17 43 118 119 190 269 453 529 633 708 708 708 736 784 785 787 826 826 833 863 887 908 920 1096 1096 1011 1011 1041 1055 1055 1060 1130 1157  -1 307 308 715 716 718 819  -1 301 489 1154  -1 34 152 191 238 309 371 471 612 634 635 684 750 759 827 977 1026 1028 1097 1098 1163 975 1030  -1 44 90 104 319 338 373 555 585 634 661 662 665 666 666 667 675 749 1179 13 1062 1107"
        lines = lines.replace('  ', ' ')  # 将两个空格替换成一个空格 所有项之间都保持一个空格
        items_array = lines.strip().split(' ')  # 按空格分隔序列 收集所有的项 包含重复
        for item in items_array:
            if item != '-1' and item not in items:  # 如果项不是项集分隔符并且没有在items中重复就将项保存在items
                items.append(item)
        # print_array(items)
        return items  # 返回不重复的项的集合(无序的 按照在序列中出现先后的顺序)

    # 生成数据字典格式
    def General_Sn(self, lines_s, S):
        # print('&'+str(sort_item))
        # 数据处理后的最终结果
        # itemcount = 0
        for i in range(len(lines_s)):
            # print(lines_s)
            items_array, s_array = self.split_array(lines_s[i])
            # for j in s_array:
            #     itemcount += len(j)
            #  lines_s[i]  0 2 -1 0 2 -1 2 -1 0 2 -1 2
            #  items_array  ['0', '2', '-1', '0', '2', '-1', '2', '-1', '0', '2', '-1', '2']
            #  s_array  [['0', '2'], ['0', '2'], ['2'], ['0', '2'], ['2']]
            sort_item, items_no_repeat = self.item_sotrd(items_array)
            # print('$',sort_item)
            # sort_item 第i条序列去重排序之后的项 ['-1', '0', '2']
            # print(sort_item)
            for item in sort_item:
                if item != '-1':
                    for k in range(len(s_array)):
                        if item in s_array[k]:
                            # index = str(sort_item.index(item))
                            # print(item)
                            # print(i)
                            # print(k)
                            # print('$$$$$$$$$$$$$$$')
                            S[item][i].append(k)
                            # if len(s_array[k]) > 1:
                            #     S[item]['mul'][i].append(k)
        # print(itemcount)
        return S

    def datap(self, readFileName, S):
        # S = {}
        # 读取的文件名字
        # readFileName = "../dataset/online-fin.txt"
        # readFileName = "../dataset/demo/test.txt"
        # 文件读取后的字符串数组 序列集合S
        lines_s = self.read_file(readFileName)
        # print(lines_s)

        # items 项集 统计后的项集(序列中出现的字符集 按照在序列中出现的次序)
        items = []
        for lines in lines_s:
            items = self.Statistics_items(lines, items)
        # print(items)

        # sort_item 排序后的项集字符串数组
        # date_no_repeat 未排序的项 在序列中出现的次序
        sort_item, items_no_repeat = self.item_sotrd(items)
        # 输出 sort_item
        # print_array(sort_item)
        # print_array(items_no_repeat)
        # 将sort_item数组写入文件sort_item.txt
        self.write_file(sort_item, 'sort_item.txt')
        #
        # 替换数据集中的字符串lines_s 替换后的字符串数组
        # print(lines_s)
        # lines_s = self.replace_seq(lines_s, sort_item)
        # print(lines_s)
        # self.write_file(lines_s, "demo2.txt")
        # print(lines_s)
        # print_array(lines_s)
        # print(len(lines_s))
        self.item_to_dict(sort_item, len(lines_s), S)  # 排序后的项 和 序列数
        # print(lines_s)
        self.General_Sn(lines_s, S)
        return len(lines_s), S, sort_item

    def utilityp(self, readFileName, U):
        lines_s = self.read_file(readFileName)
        for lines in lines_s:
            key_value = lines.strip().split(' ')
            U[key_value[0]] = key_value[1]
        # print(U)

    def __del__(self):
        pass
