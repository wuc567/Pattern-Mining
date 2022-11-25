from math import ceil
import time

from numpy import sort
from common import no_que, seqdb, pant_p, readfile, Creat_ptn

# frequent pattern and its support
frequent = {} # string : int

def min_freItem(sdb : list, mymap : dict, upminsup : int, minunity : float):
    counter = {}
    for db in sdb:
        db : seqdb
        for c in db.S:
            if (c >= 'a' and c<='z') or (c >='A' and c <= 'Z'):
                if c in counter:
                    counter[c] +=  1
                else:
                    counter[c] = 1
    
    freArr = [[]]
    canArr = [[]]
    ks = list(counter.keys())
    for k in sort(ks).tolist():
        hupval : int = mymap[k]
        if counter[k] >= upminsup:
            if counter[k] * hupval >= minunity:
                freArr[0].append(k)
            canArr[0].append(k)
    return freArr, canArr

def gen_candidate(level : int, canArr: list):
    candidate = []
    sz = len(canArr[level-1])
    for k in range(sz):
        Q = canArr[level-1][k]
        for i in range(len(canArr[0])):
            cand = Q + canArr[0][i]
            candidate.append(cand)

    return candidate

def haop_bf(filename: str, minunity : float):
    sdb = readfile(filename=filename)

    mymap = {
        'a' : 2,
        'g' : 3,
        'c' : 2,
        't' : 3
    }

    upminsup = ceil(minunity/3)
    begintime = time.time()
    freArr, canArr = min_freItem(sdb, mymap, upminsup, minunity)
    f_level = 1

    candidate = gen_candidate(f_level, canArr)
    compnum = 0
    while len(candidate) != 0:
        if len(freArr) <= f_level:
            freArr.append([])
        if len(canArr) <= f_level:
            canArr.append([])
        for p in candidate:
            num = 0
            occnum = 0 #the support num of pattern
            # rest = 0
            compnum += 1
            ptn_len = len(p)
            hupval=0
            for s in range(ptn_len):
                hupval += mymap[p[s]]
            link_pan = Creat_ptn(p)
            for db in sdb:
                db : seqdb
                if len(db.S) > 0:
                    s_length = len(db.S)
                    if ptn_len > s_length:
                        num = 0
                    else:
                        num += no_que(db.S, link_pan, ptn_len)

            link_pan.clear()
            occnum=num
            if occnum>=upminsup:
                hupval = occnum*hupval/ len(p)
                if hupval >= minunity:
                    freArr[f_level].append(p)
                canArr[f_level].append(p)
        f_level += 1
        candidate.clear()
        candidate = gen_candidate(f_level, canArr)

    elapsed_time = (time.time() - begintime) * 1000 # ms

    return f_level, freArr, elapsed_time, compnum


if __name__ == '__main__':
    filename = '../text/AX829174.txt'
    minunity = 3600
    f_level, freArr, elapsed_time, compnum = haop_bf(filename, minunity)

    frenum = 0
    for i in range(f_level):
        print(', '.join(freArr[i]))
        frenum += len(freArr[i])
    
    print(f'The time-consuming:{elapsed_time} ms.')
    print(f'总数为: {frenum}')
    print(f'总数为: {compnum}')