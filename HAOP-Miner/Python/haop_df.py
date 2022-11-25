from math import ceil
import time

from numpy import sort
from common import no_que, seqdb, pant_p, readfile, Creat_ptn

compnum = 0
frenum = 0 #compute number and frequents number

def min_freItem(sdb : list, mymap : dict, minsup : int, minunity : float):
    counter = {}
    for db in sdb:
        db : seqdb
        for c in db.S:
            if (c >= 'a' and c<='z') or (c >='A' and c <= 'Z'):
                if c in counter:
                    counter[c] +=  1
                else:
                    counter[c] = 1
    items = []
    frequent = {}
    ks = list(counter.keys())
    for k in sort(ks).tolist():
        hupval : int = mymap[k]
        if counter[k] >= minsup:
            items.append(k)
            if counter[k] * hupval >= minunity:
                frequent[k] = counter[k]
    return items, frequent


def mineFre(frequent: dict, p : str, items: list, mymap : dict, sdb: list, minsup: int):
    global compnum 
    for item in items:
        q = p + item
        ptn_len = len(q)
        compnum += 1
        # num = 0
        hupval = 0
        # int occnum = 0; //the support num of pattern
        rest = 0
        for l in range(len(q)):
            hupval += mymap[q[l]]
        link_pan = Creat_ptn(q)
        num=0
        occnum=0
        for db in sdb:
            db : seqdb
            if len(db.S) > 0:
                if ptn_len > len(db.S):
                    num = 0
                else:
                    occnum = no_que(db.S, link_pan, ptn_len)
        link_pan.clear()
        if occnum>=minsup:
            hupval = occnum*hupval/ len(q)
            if hupval >= minsup * 3:
                frequent[q] = occnum
            mineFre(frequent, q, items, mymap, sdb, minsup)


def haop_df(filename: str, minunity : float):
    sdb = readfile(filename=filename)

    mymap = {
        'a' : 2,
        'g' : 3,
        'c' : 2,
        't' : 3
    }

    minsup = ceil(minunity/3)
    begintime = time.time()

    items, frequent = min_freItem(sdb, mymap, minsup, minunity)
    for item in items:
        mineFre(frequent, item, items, mymap, sdb, minsup)

    elapsed_time = (time.time() - begintime) * 1000 # ms

    return frequent, elapsed_time, compnum

if __name__ == '__main__':
    filename = '../text/AX829174.txt'
    minunity = 3600

    frequent, elapsed_time, compnum = haop_df(filename, minunity)

    print(', '.join(frequent.keys()))
    print(f"The number of frequent patterns: {len(frequent)}")
    print(f"The time-consuming: {elapsed_time} ms.")
    print(f"The number of calculation:{compnum}")



