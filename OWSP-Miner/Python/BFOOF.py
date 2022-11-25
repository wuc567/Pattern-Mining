from collections import OrderedDict
def pd(zifu,R):
    for i in R:
        if(zifu == i or ord(zifu) < 65 or 90 < ord(zifu) < 97 or 122 < ord(zifu)):
            return False
    return True

def pdR(s,R):
    for i in s:
        if i not in R:
            return False
    return True
def zl(a):
    a = list(filter(lambda x: x!='',a))
    b = list(set(a))
    return b

def yz(yuzhi,one):
    for i in range(0,len(one)):
        if one[i] < yuzhi:
            one[i] = 0
    return one

def diguipd(k, sample, R):
    sup = 0
    m = [[100000] for i in range(len(sample))]
    ll = 0
    i = 0
    while i < len(k):
        l = 0
        for j in range(len(sample)):
            if k[i] == sample[j] and j == 0 and m[j][ll] ==100000:
                m[j][ll] = i
                print(m)
            elif k[i] == sample[j] and j != 0 and m[j - 1][ll] != 100000:
                print(m,k[m[j - 1][ll] + 1:i],j,i)
                if i > m[j - 1][ll] and pdR(k[m[j - 1][ll] + 1:i], R) and m[j][ll] == 100000:
                    m[j][ll] = i
                    print('/')
                elif not pdR(k[m[j - 1][ll] + 1:i], R) and m[j][ll] == 100000:
                    i = i - 1
                    l = 1
                    print('*')
        if m[len(sample) - 1][ll] != 100000:
            sup = sup + 1
        if m[len(sample) - 1][ll] != 100000 or l == 1:
            for mm in range(len(sample)):
                m[mm][ll] = 100000
        i = i + 1
    return sup

def digui(newone,s,yuzhi,R,mui):
    m = []
    numone = []
    before = []
    after = []
    for i in newone:
        before.append(i[:-1])
        after.append(i[1:len(i)])
    for i in range(len(before)):
        for j in range(len(after)):
            if before[i]==after[j] and str(newone[j][:-1]+newone[i]) not in m:
                n = diguipd(s,str(newone[j][:-len(before[i])]+newone[i]),R)
                mui = mui +1
                if n >= yuzhi:
                    m.append(str(newone[j][:-len(before[i])]+newone[i]))
                    numone.append(n)
    if len(m):
        return m,numone,0,mui
    else:
        return m,numone,1,mui

def mainnnnn(s,R,yuzhi):
    lens = len(s)
    a = [''for i in range(10000)]
    t=0
    numm=0
    for i in range(0,lens):
        if pd(s[i],R) == False:
            a[numm] = s[t:i]
            t =i+1
            numm = numm+1
        if i+1 == lens and pd(s[i],R) ==True:
            a[numm] = s[t:i+1]
    chuxulie = zl(a)
    one = [0 for i in range(122)]
    for i in chuxulie:
        for j in i:
            one[ord(j)] = one[ord(j)] + 1
    neone = yz(yuzhi,one)
    newone = []
    numone = []

    for i in range(122):
        if neone[i] !=0:
            newone.append(chr(i))
            numone.append(one[i])
    t = 0
    textt = []
    texto = []
    www = []
    textt.append(newone)
    texto.append(numone)
    numone=[]
    mui = len(newone)
    for i in newone:
        for j in newone:
            mui = mui+1
            if diguipd(s,str(i+j),R) >= yuzhi:
                www.append(str(i+j))
                numone.append(diguipd(s,str(i+j),R))
    textt.append(www)
    texto.append(numone)

    while(t == 0):
        www,numone,t,mui= digui(www,s,yuzhi,R,mui)
        if t == 0 :
            textt.append(www)
            texto.append(numone)
    return textt,texto,mui