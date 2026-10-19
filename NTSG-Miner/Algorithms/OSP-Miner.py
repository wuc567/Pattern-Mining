import operator
import argparse
from pathlib import Path
import sys
sys.setrecursionlimit(1000000)
import time
import copy
try:
    from memory_profiler import memory_usage
except ImportError:
    memory_usage = None


class Item():
    def __init__(self,dataitems):
        self.data=dataitems


class Candilist():
    def __init__(self,dataitems):
        self.data=dataitems
        self.sup =0
        self.prefix=[]
        self.suffer=[]


candione={}

candi=[]

FPItem=[]

FP=[]

minsup = None
DATASET_PATH = None

Nextlist=[]

Next={}

seqs=[]
strong = set()
weak = set()

twolist=[]

twoitems=[]

def conseqs():
    with open(DATASET_PATH, 'r', encoding='utf-8-sig') as f:
        lines = [line.strip() for line in f if line.strip()]

    # A FASTA record can occupy multiple physical lines.
    if any(line.startswith('>') for line in lines):
        records = []
        current = []
        for line in lines:
            if line.startswith('>'):
                if current:
                    records.append(''.join(current))
                    current = []
            else:
                current.append(line)
        if current:
            records.append(''.join(current))
        lines = records

    for line in lines:
        tokens = line.split()
        if '-1' in tokens or '-2' in tokens:
            seq = []
            itemset = []
            for token in tokens:
                if token == '-1':
                    if itemset:
                        seq.append(Item(itemset))
                        itemset = []
                elif token == '-2':
                    if itemset:
                        seq.append(Item(itemset))
                        itemset = []
                    if seq:
                        seqs.append(seq)
                        seq = []
                else:
                    itemset.append(token)
            if itemset:
                seq.append(Item(itemset))
            if seq:
                seqs.append(seq)
        else:

            symbols = ''.join(tokens)
            if symbols:
                seqs.append([Item([character]) for character in symbols])


def preandsuf(p):
    if len(p.data)!=1:
        tp = copy.deepcopy(p.data)
        p.prefix=copy.deepcopy(p.data[0:-1])
        p.suffer=copy.deepcopy(p.data[1:])
        tp[0].pop(0)
        if len(tp[0])!=0:
            p.suffer.insert(0,tp[0])
        tp[-1].pop(-1)
        if len(tp[-1]) != 0:
            p.prefix.append(tp[-1])
    else:
        p.prefix.append(copy.deepcopy(p.data[0][0:-1]))
        p.suffer.append(copy.deepcopy(p.data[0][1:]))


def onepattern(seqs):
    candiones={}
    i=0
    while i<len(seqs):
        j=0
        while j<len(seqs[i]):
            k=0
            while k<len(seqs[i][j].data):
                if seqs[i][j].data[k] not in candiones.keys():
                    candiones[seqs[i][j].data[k]] = 1
                    candi.append(Candilist([seqs[i][j].data[k]]))
                else:
                    candiones[seqs[i][j].data[k]] = candiones.get(seqs[i][j].data[k]) + 1
                if seqs[i][j].data[k] not in Next.keys():
                    Next[seqs[i][j].data[k]] = [j]
                else:
                     Next[seqs[i][j].data[k]].append(j)
                k+=1
            j+=1
        Nextlist.append(copy.deepcopy(Next))
        Next.clear()
        i+=1
    candione=dict(sorted(candiones.items(),key=lambda x:x[1]))
    for key in sorted(list(candione.keys())):
        if key in strong and candione[key] >= minsup:
            temp = Candilist(key.split(","))
            temp.sup = candione[key]
            FPItem.append(temp)
        else:
            for index in Nextlist:
                index.pop(key, None)
            candione.pop(key)
    
    
    sort_item=list(candione.keys())
    sort_item.sort()
    i = 0
    while i < len(sort_item):
        temp = Candilist([str(sort_item[i])])
        temp.sup = candione.get(str(sort_item[i]))
        FP.append(temp)
        i += 1


def sortitem(items):
    sort_item=[]
    for x in items:
        sort_item.append(int(x))
    sort_item.sort()
    return sort_item


def one_to_two():
    i=0
    while i<len(FP):
        tp=copy.deepcopy(FP[i].data)
        j=0
        while j<len(FP):
            ad=copy.deepcopy(FP[j].data)
            tmp=[]
            if i<j:
                tmp.append(tp+ad)
                candi.append(Candilist(tmp))
                twoitems.append(Candilist(tmp))
                tmp=[]
            tmp.append(tp)
            tmp.append(ad)
            candi.append(Candilist(tmp))
            twoitems.append(Candilist(tmp))
            j+=1
        i+=1


def sorilink():
    i=0
    while i<len(FP):
        preandsuf(FP[i])
        i+=1
    for i in range(len(FP)):
        for j in range(len(FP)):
            if operator.eq(FP[i].prefix,FP[j].suffer):
                tmp = copy.deepcopy(FP[j].data)
                if len(FP[i].data[-1]) == 1:
                    tmp.append(FP[i].data[-1])
                else:
                    tmp[-1].append(FP[i].data[-1][-1])
                candi.append(Candilist(tmp))
    FP.clear()


def isweak(s,beg,end):
    i=beg+1
    while i<end:
        j=0
        while j<len(s[i].data):
            if s[i].data[j] not in weak:
                    return False
            j+=1
        i+=1
    if i==end:
        return True


def twoindexlist(seqs,twoitems):

    out = 0
    n=0
    while n<len(seqs):
        oneseqtwoitem = {}
        m=0
        while m<len(twoitems):
            p=twoitems[m]
            idx=[]
            que=[]
            i = 0
            while i < len(p.data):
                j = 0
                while j < len(p.data[i]):
                    if p.data[i][j] in Nextlist[n].keys():
                        temp = copy.deepcopy(Nextlist[n].get(p.data[i][j]))
                        que.append(temp)
                    else:
                        que = []
                        out=1
                        break
                    j += 1
                i += 1
            if out==1:
                out=0
                m+=1
                continue
            f = 0
            s = 0
            if len(p.data)!=1:
                while 1:
                    while f<len(que[0]) and s<len(que[1]) and que[0][f]>=que[1][s]:
                        s+=1
                    if f<len(que[0]) and s<len(que[1]):
                        if isweak(seqs[n],que[0][f],que[1][s]):
                            idx.append([que[0][f],que[1][s]])
                            f+=1
                            s+=1
                        else:
                            f+=1
                    else:
                        break
            else:
                while f<len(que[0]) and s<len(que[1]):
                    if que[0][f]==que[1][s]:
                        idx.append([que[0][f]])
                        f += 1
                        s += 1
                    elif que[0][f]>que[1][s]:
                        s+=1
                    else:
                        f+=1
            if len(idx)!=0:
                oneseqtwoitem[str(p.data)]=idx
            m+=1
        twolist.append(copy.deepcopy(oneseqtwoitem))
        n+=1


def splitpattern(p):
    pre=[]
    i=0
    f = p.data[0][0]
    k=0
    s = ''
    temp = []
    while i<len(p.data):
        j=0
        while j<len(p.data[i]) and i<len(p.data):
            if j+1<len(p.data[i]):
                s=p.data[i][j+1]
                temp.append(f)
                temp.append(s)
                pre.append([temp])
            else:
                if i+1>=len(p.data):
                    break
                s=p.data[i+1][0]
                temp.append([f])
                temp.append([s])
                pre.append(temp)
            f = s
            k += 1
            if k==1:
                k=0
                s = ''
                temp = []
            j+=1
        i+=1
    return pre

def searchfirst(pre,que,n,num,useflag):
    i=0
    while i<len(que):
        if que[i][0]==num:
            if len(pre[n])==1:
                if pre[n][0][-1] not in useflag.keys():
                    return que[i][-1]
                elif que[i][-1] not in useflag.get(pre[n][0][-1]):
                    return que[i][-1]
            else:
                if pre[n][-1][0] not in useflag.keys():
                    return que[i][-1]
                elif que[i][-1] not in useflag.get(pre[n][-1][0]):
                    return que[i][-1]
            break
        i+=1
    return None


def splitlist(twolist,n,pre,p):
    que=[]
    usesup=[]
    useflag={}
    i=0
    while i<len(pre):
        if str(pre[i]) in twolist[n].keys():
            que.append(twolist[n].get(str(pre[i])))
        else:
            return 0
        i+=1
    
    i=0
    while i<len(que[0]):
        if pre[0][0][0] in useflag.keys() and que[0][i][0] in useflag.get(pre[0][0][0]):
            i+=1
            continue
        usesup.append(que[0][i][0])
        num=searchfirst(pre,que[0],0,que[0][i][0],useflag)
        usesup.append(num)
        j=1
        while j<len(que):
            num=searchfirst(pre,que[j],j,num,useflag)
            if num==None:
                usesup.clear()
                break
            else:
                usesup.append(num)
            j+=1
        if j == len(que):
            p.sup+=1
            m=len(p.data)-1
            while m>=0:
                n=len(p.data[m])-1
                while n>=0:
                    if p.data[m][n] not in useflag.keys():
                        useflag[p.data[m][n]]=[usesup.pop()]
                    else:
                        useflag[p.data[m][n]].append(usesup.pop())
                    n-=1
                m-=1
            usesup.clear()
        i+=1


def fretwo(seqs,twoitems,twolist):
    i=0
    while i<len(twoitems):
        if len(twoitems[i].data)==1:
            f=twoitems[i].data[0][0]
            s=twoitems[i].data[0][1]
        else:
            f=twoitems[i].data[0][0]
            s = twoitems[i].data[1][0]
        if f==s:
            flag=1
        else:
            flag=0
        j=0
        while j<len(seqs):
            useflag=[]
            if str(twoitems[i].data) in twolist[j].keys():
                if flag==0:
                    twoitems[i].sup+=len(twolist[j].get(str(twoitems[i].data)))
                else:
                    temp=twolist[j].get(str(twoitems[i].data))
                    m=0
                    while m<len(temp):
                        n=0
                        while n<len(temp[m]):
                            if temp[m][n] not in useflag:
                                useflag.append(temp[m][n])
                            else:
                                break
                            n+=1
                        if n==2:
                            twoitems[i].sup+=1
                        m+=1
            j+=1
        i+=1
    i=0

    while i<len(twoitems):
        if twoitems[i].sup>=minsup:
            FP.append(twoitems[i])
            FPItem.append(twoitems[i])
        i+=1

def mainfun():
    conseqs()
    candinum=[]
    starttime=time.time()
    onepattern(seqs)#0->1
    one_to_two()
    twoindexlist(seqs,twoitems)
    FP.clear()
    fretwo(seqs,twoitems,twolist)
    candinum.append(len(candi))
    sorilink()#2->3
    candinum.append(len(candi))
    FP.clear()
    while 1 :
        cannum = candinum.pop(0)
        i = cannum
        while i < len(candi):
            p = candi[i]
            pre = splitpattern(p)
            j = 0
            while j < len(seqs):
                splitlist(twolist,j,pre,p)
                j += 1
            if candi[i].sup >= minsup:
                FP.append(candi[i])
                FPItem.append(candi[i])
            i += 1
        sorilink()
        FP.clear()
        if cannum == len(candi):
            break
        else:
            candinum.append(len(candi))
    endtime = time.time()
    
    i = 0
    while i < len(FPItem):
        print(str(FPItem[i].data) + ":" + str(FPItem[i].sup))
        i += 1
    print("endtime:"+str(endtime-starttime))
    print("Frequent pattern result set: "+str(len(FPItem)))
    print("Candidate pattern: "+str(len(candi)))
def resolve_dataset_path(user_value):
    path = Path(user_value.strip().strip('"').strip("'")).expanduser()
    candidates = [path] if path.is_absolute() else [Path.cwd() / path, Path(__file__).resolve().parent / path]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate.resolve())
    return None


def prompt_for_configuration():
    print('\nOSP-Miner: enter experiment settings.')
    print('Enter the dataset filename or its full path.')
    while True:
        entered_path = input('Dataset file: ').strip()
        found = resolve_dataset_path(entered_path) if entered_path else None
        if found:
            break
        print('Dataset not found. Please enter a valid filename or path.')

    while True:
        entry = input('Minimum support: ').strip()
        try:
            chosen_minsup = int(entry)
            if chosen_minsup > 0:
                break
        except ValueError:
            pass
        print('Minimum support must be a positive integer.')

    while True:
        strong_text = input('Strong characters: ').strip()
        weak_text = input('Weak characters: ').strip()
        if not strong_text or not weak_text:
            print('Both character sets are required.')
        elif not set(strong_text).isdisjoint(weak_text):
            print('Strong and weak character sets must not overlap.')
        else:
            return found, chosen_minsup, strong_text, weak_text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OSP-Miner for character and SPMF-like data')
    parser.add_argument('--data', help='Dataset filename or path')
    parser.add_argument('--minsup', type=int, help='Absolute minimum support')
    parser.add_argument('--strong', help='Strong-character set')
    parser.add_argument('--weak', help='Weak-character set')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        DATASET_PATH, minsup, strong_text, weak_text = prompt_for_configuration()
    else:
        if any(value is None for value in (args.data, args.minsup, args.strong, args.weak)):
            parser.error('Specify --data, --minsup, --strong, and --weak together.')
        DATASET_PATH = resolve_dataset_path(args.data)
        if DATASET_PATH is None:
            parser.error('Dataset not found: ' + args.data)
        minsup, strong_text, weak_text = args.minsup, args.strong, args.weak

    strong = set(strong_text)
    weak = set(weak_text)
    if minsup <= 0:
        parser.error('Minimum support must be a positive integer.')
    if not strong or not weak:
        parser.error('Both character sets are required.')
    if not strong.isdisjoint(weak):
        parser.error('Strong and weak character sets must not overlap.')

    print('\nDataset:', DATASET_PATH)
    print('Strong:', ''.join(sorted(strong)))
    print('Weak:', ''.join(sorted(weak)))
    print('MinSup:', minsup)
    print('Mining started...\n', flush=True)
    if memory_usage is None:
        mainfun()
        print('Memory usage: unavailable (install memory_profiler to enable).')
    else:
        maxusage = memory_usage((mainfun), max_usage=True)
        print(str(maxusage) + ' Mb')
