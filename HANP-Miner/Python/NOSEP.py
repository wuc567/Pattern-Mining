import os
from time import time as time_now
from copy import deepcopy

import psutil

K = 600  # The sequence number of sequence database
M = 100  # The length of pattern  # define N 200000  //The length of sequence
N = 200000  # The length of sequence
S = ''

unum = [0.0 for i in range(K)]
ww = 0
store = 0
class sub_ptn:
	start = ''
	end = ''
	min = 0
	max = 0


sub_ptn_list = [sub_ptn() for i in range(M)]

ptn_len = 0


class seqdb:
	id = 0
	S = ''

class node: #The corresponding position of node in sequence
	name = 0    #The corresponding position of node in sequence
	min_leave, max_leave = name, name #The position of maxinum and mininum leave nodes
	parent = [] #The position set of parents
	children = []   #The position set of children
	used = False    #true is has used, false is has not used
	toleave =False  #true is can reach leaves, false is not
	def __init__(self, name = name):
		self.name = name
		self.min_leave, self.max_leave = name, name
		self.children = []
		self.parent = []
		self.used = False
		self.toleave = False

class occurrence:
	position = []

sDB = [seqdb() for i in range(K)]
minsup = 0
NumbS = 0

freArr = [[] for i in range(M)]
candidate = []


def deal_range(pattern):
	'''
	put sub-pattern "a[1,3]b" into sub_ptn and sub_ptn.start=a，sub_ptn.end=b, sub_ptn.min=1，sub_ptn.max=3
	:param pattern:
	:return: void
	'''
	global ptn_len
	ptn_len = 0
	p = list(pattern)
	if len(pattern) == 1:
		sub_ptn_list[ptn_len].start = p[0]
		sub_ptn_list[ptn_len].max = 0
		sub_ptn_list[ptn_len].min = 0
	for i in range(len(pattern) - 1):
		sub_ptn_list[ptn_len].start = p[i]
		sub_ptn_list[ptn_len].end = p[i + 1]
		sub_ptn_list[ptn_len].max = maxgap
		sub_ptn_list[ptn_len].min = mingap
		ptn_len = ptn_len + 1


def binary_search(level, cand, low, high):
	'''
	find the first position of cand in the level of canArr by binary search
	:param level:
	:param cand:
	:param low:
	:param high:
	:return: int
	'''
	if low > high:
		return -1
	while low <= high:
		mid = int((low + high) / 2)
		if cand == freArr[level - 1][mid][0:level - 1]:  # To avoid multiple calls the same function
			s_low = low
			s_high = mid
			if cand == freArr[level - 1][low][0:level - 1]:
				start = low
			else:
				while s_low < s_high:
					start = int((s_low + s_high) / 2)
					if cand == freArr[level - 1][start][0:level - 1]:
						s_high = start
					else:
						s_low = start + 1
				start = s_low
			return start
		elif cand < freArr[level - 1][mid][0:level - 1]:
			high = mid - 1
		else:
			low = mid + 1
	return -1


def gen_candidate(level):
	'''
	使用canArr数组的模式逐层生成候选模式——模式连接
	:param level:
	:return:
	'''
	global candidate
	size = len(freArr[level - 1])
	start = 0
	for i in range(size):
		Q = freArr[level - 1][start][0:level - 1]  # prefix pattern of freArr[level-1][start]
		R = freArr[level - 1][i][1:level]  # suffix pattern of freArr[level-1][i]
		if Q != R:
			start = binary_search(level, R, 0, size - 1)
		if start < 0 or start >= size:  # if not exist, begin from the first
			start = 0
		else:
			Q = freArr[level - 1][start][0:level - 1]
			while Q == R:
				cand = freArr[level - 1][i][0:level] + freArr[level - 1][start][level - 1:level]
				candidate.append(cand)
				start = start + 1
				if start >= size:
					start = 0
					break
				Q = freArr[level - 1][start][0:level - 1]
	candidate = sorted(candidate)


def min_freItem():
	'''
	生成长度为1的频繁模式
	:return:
	'''
	global ww
	global NumbS
	counter = dict()
	for t in range(NumbS):
		S = sDB[t].S
		for s in S:
			mine = s
			if counter.get(mine) == None:
				counter[mine] = 1
			else:
				counter[mine] += 1
	for iterator in counter.items():
		if iterator[1] >= minsup:
			freArr[0].append(iterator[0])



def create_nettree():
	'''
	创建网树
	:param nettree:
	:return:
	'''
	global S
	global ptn_len
	nettree = [[] for i in range(ptn_len + 1)]
	start = [0 for i in range(ptn_len + 1)]
	for i in range(len(S)):
		node0 = node(i)
		if S[i] == sub_ptn_list[0].start:
			node0.toleave = True
			nettree[0].append(deepcopy(node0))
		for j in range(ptn_len):
			if sub_ptn_list[j].end == S[i]:
				if len(nettree[j]) == 0:
					break
				for k in range(start[j], len(nettree[j])):
					if i - nettree[j][k].name - 1 > sub_ptn_list[j].max:
						start[j] += 1
				if i - nettree[j][len(nettree[j])-1].name - 1 > sub_ptn_list[j].max or i - nettree[j][start[j]].name - 1 < sub_ptn_list[j].min:
					continue
				node0.toleave = True
				nettree[j + 1].append(deepcopy(node0))
				for k in range(start[j], len(nettree[j])):
					if i - nettree[j][k].name - 1 < sub_ptn_list[j].min:
						break
					nettree[j][k].children.append(len(nettree[j + 1]) - 1)
					nettree[j+1][len(nettree[j+1]) - 1].parent.append(k)
	del start
	return nettree


def update_nettree(nettree):
	global ptn_len
	for i in range(ptn_len-1, -1, -1):
		for j in range(len(nettree[i])-1, -1, -1):
			flag = True
			size = len(nettree[i][j].children)
			for k in range(size):
				child = nettree[i][j].children[k]
				if k == 0:
					nettree[i][j].min_leave = nettree[i + 1][child].min_leave
				if k == size - 1:
					nettree[i][j].max_leave = nettree[i + 1][child].max_leave
				if not nettree[i + 1][child].used:
					flag = False
			nettree[i][j].used = flag
			if flag:
				nettree[i][j].max_leave = nettree[i][j].name
				nettree[i][j].min_leave = nettree[i][j].name
				nettree[i][j].toleave = False
	return nettree

def update_nettree_pc(nettree, occin):
	for level in range(ptn_len, 0, -1):
		for position in range(occin.position[level], len(nettree[level])):
			if not nettree[level][position].used:
				break
			for i in range(len(nettree[level][position].parent)):
				parent = nettree[level][position].parent[i]
				if nettree[level - 1][parent].used:
					continue
				if len(nettree[level - 1][parent].children) == 1:
					nettree[level - 1][parent].used = True
					nettree[level - 1][parent].toleave = False
				else:
					flag = True
					for child in nettree[level - 1][parent].children:
						if not nettree[level][child].used:
							flag = False
							break
					if flag:
						nettree[level - 1][parent].used = True
						nettree[level - 1][parent].toleave = False


def nonoverlength():
	global store
	# nettree = [[node() for i in range(ptn_len + 1)]]
	nettree = create_nettree()
	nettree = update_nettree(nettree)
	store = 0
	for position in range(len(nettree[0])):
		if not nettree[0][position].toleave:
			continue
		occin = occurrence()
		occin.position = [0 for _ in range(ptn_len + 1)]
		occin.position[0] = position
		nettree[0][position].used = True
		nettree[0][position].toleave = False
		j = 1
		while j <= ptn_len:
			parent = occin.position[j - 1]
			cs = len(nettree[j - 1][parent].children)
			t = 0
			while t < cs:
				child = nettree[j - 1][parent].children[t]
				if not nettree[j][child].used:
					occin.position[j] = child
					nettree[j][child].used = True
					nettree[j][child].toleave = False
					break
				t += 1
			if t == cs:
				for kk in range(j):
					pos = occin.position[kk]
					nettree[kk][pos].used = False
					nettree[kk][pos].toleave = True
				break
			j += 1
		if j == ptn_len + 1:
			store += 1
			update_nettree_pc(nettree, occin)

def netGap(p):
	global ptn_len
	deal_range(p)
	if ptn_len + 1 > len(S):
		return 0
	nonoverlength()
	return store

def clear_mem():
    global K,M,N,S,unum,ww
    global my_dict, sub_ptn_list,ptn_len,sDB
    global minsup,NumbS,freArr,canArr,candidate
    K = 600  # The sequence number of sequence database
    M = 100  # The length of pattern
    N = 60000  # The length of sequence
    S = ''
    unum = [0.0 for i in range(K)]
    ww = 0
    my_dict = dict()
    sub_ptn_list = [sub_ptn() for i in range(M)]
    ptn_len = 0
    sDB = [seqdb() for i in range(K)]
    minsup = 0
    NumbS = 0
    freArr = [[] for i in range(M)]
    canArr = [[] for i in range(M)]
    candidate = []

def read_file(filename):
	with open(filename, 'r') as file:
		text = file.readlines()
		raw = len(text)
		for i in range(raw):
			sDB[i].S = text[i].replace('\n', '')
		global NumbS
		NumbS = raw
		for t in range(NumbS):
			sDB[t].id = t + 1

def output(f_level,begin_time,end_time,compnum,filename,output_filename):
	frenum = 0
	for i in range(f_level):
		if len(freArr[i]) == 0:
			print('\n------------ Program Running Statistics ------------')
			break
		for fre in freArr[i]:
			print(fre, end='\t')
			frenum = frenum + 1
		print(frenum)
	print('The number of frequent patterns:', frenum)
	print('The time-consuming:', end_time - begin_time, 's. ')
	print('The number of calculation:', compnum)
	with open(output_filename, 'w') as file:
		print('-------- Results of ', __file__.split('\\')[-1].split('/')[-1].replace('.py', ''), ' for ',
		      filename.split('\\')[-1].split('/')[-1].replace('.txt', ''), ' --------', file=file)
		for i in range(f_level):
			if len(freArr[i]) == 0:
				print('\n------------ Program Running Statistics ------------', file=file)
				break
			for fre in freArr[i]:
				print(fre, end='\t', file=file)
			print(file=file)
		print('The number of frequent patterns:', frenum, file=file)
		print('The time-consuming:', end_time - begin_time, 's. ', file=file)
		print('The number of calculation:', compnum, file=file)
		print(u'Memory usage of the current process: %.4f MB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024), file = file)
	print(u'Memory usage of the current process: %.4f MB' % (psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024))


def NOSEP(filename, mingap, maxgap, minsup, output_filename = 'result_file.txt'):
	clear_mem()
	read_file(filename)
	cannum = 0
	frenum = 0
	compnum = 0
	global S
	global ww
	global NumbS
	global candidate
	begin_time = time_now()
	min_freItem()
	f_level = 1
	gen_candidate(f_level)
	while len(candidate) != 0:
		for p in candidate:
			cannum += 1
			occnum = 0
			compnum += 1
			for t in range(NumbS):
				if len(sDB[t].S) > 0:
					S = sDB[t].S
					occnum += netGap(p)
				if occnum >= minsup:
					freArr[f_level].append(p)
					break
		f_level += 1
		candidate.clear()
		gen_candidate(f_level)
	end_time = time_now()
	output(f_level, begin_time, end_time, compnum, filename, output_filename)


if (__name__ == '__main__'):
	filename = 'DataSet/DNA1.txt'
	minlen = 1
	maxlen = 20
	mingap = 0
	maxgap = 3
	minsup = 900
	NOSEP(filename, mingap, maxgap, minsup)
