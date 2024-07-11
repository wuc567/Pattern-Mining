import random

import Pdata
pdata = Pdata.processingData()
filelist = [
    '1.txt',
    '5.txt',
    '10.txt',
    '50.txt',
    '100.txt',
    '500.txt',
    '1000.txt',
    '5000.txt',
    'SDB1.txt',
    'SDB2.txt',
    'SDB3.txt',
    'SDB4.txt',
    'SDB5.txt',
    'SDB6.txt',
    'SDB7.txt',
    'SDB8.txt',
]

utility = {}
if __name__ == '__main__':
    for i in filelist:
        lines = pdata.read_file('../data/'+i)
        for j in lines:
            strlist = j.split(' ')
            for k in strlist:
                if k in utility.keys() or k == '-1':
                    continue
                else:
                    n = random.randint(1, 10)
                    utility[k] = n
        # 创建并写入txt
        filename = '../data/utility/'+i.replace('.txt', '_utility.txt')
        with open(filename, 'w+') as f:
            for k, v in utility.items():
                print(k, v)
                f.writelines(k + ' ' + str(v))
                if k != list(utility.keys())[-1]:
                    f.write('\n')
        f.close()
        utility = {}

