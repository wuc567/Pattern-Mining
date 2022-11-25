class pant_p:
    def __init__(self, name : str, que_pan : list) -> None:
        self.name = name
        self.que_pan = que_pan

class seqdb:
    """
    id : sequence id
    S : sequence
    """
    def __init__(self, id_, S) -> None:
        self.id_ = id_
        self.S = S

def readfile(filename):
    sdb = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for t, line in enumerate(lines, 1):
            sdb.append(seqdb(t, line))

    return sdb

def Creat_ptn(p : str):
    link_pan = []
    for c in p:
        pan = pant_p(c, [])
        link_pan.append(pan)
    return link_pan


def no_que(S : str, link_pan : list, ptn_len : int):
    occnum = 0
    for k in range(len(S)):
        postion = 0
        for m in range(len(link_pan)-1, 0, -1):
            if S[k] == link_pan[m].name and len(link_pan[m].que_pan) < len(link_pan[m-1].que_pan):
                link_pan[m].que_pan.append(k)
                postion = m
                break

        if postion == 0 and S[k] == link_pan[0].name:
            link_pan[0].que_pan.append(k)
        if postion == ptn_len - 1:
            occnum += 1

    for k in range(len(link_pan)):
        link_pan[k].que_pan = []

    return occnum


def binary_search(canArr: list, level : int, cand : str, low : int, high : int):
    if low > high:
        return -1
    while low <= high:
        mid = (high + low) // 2
        # To avoid multiple calls the same function
        midstr = canArr[level-1][mid][0 : level-1]
        if cand == midstr:
            slow = low
            shigh = mid
            flag = -1
            if cand == canArr[level-1][low][0 : level-1]:
                start = low
            else:
                while slow < shigh:
                    start = (slow + shigh) // 2
                    sresult=cand == canArr[level-1][start][0 : level-1]
                    if sresult:
                        shigh = start
                        flag = 0
                    else:
                        slow = start + 1
                start = slow
            return start
        elif cand < midstr:
            high = mid - 1
        else:
            low = mid + 1
    return -1