import os
from time import time as time_now
import psutil as psutil

class sub_ptn:
	start = ''
	end = ''
	min = 0
	max = 0

class seqdb:
	id = 0
	S = ''

K = 60000  # The sequence number of sequence database
M = 20000  # The length of pattern  # define N 200000  //The length of sequence
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

def deal_range(pattern, maxgap, mingap):
	'''

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
		if cand == canArr[level - 1][mid][0:level - 1]:  # To avoid multiple calls the same function
			s_low = low
			s_high = mid
			if cand == canArr[level - 1][low][0:level - 1]:
				start = low
			else:
				while s_low < s_high:
					start = int((s_low + s_high) / 2)
					if cand == canArr[level - 1][start][0:level - 1]:
						s_high = start
					else:
						s_low = start + 1
				start = s_low
			return start
		elif cand < canArr[level - 1][mid][0:level - 1]:
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
	size = len(canArr[level - 1])
	start = 0
	for i in range(size):
		Q = canArr[level - 1][start][0:level - 1]  # prefix pattern of freArr[level-1][start]
		R = canArr[level - 1][i][1:level]  # suffix pattern of freArr[level-1][i]
		if Q != R:
			start = binary_search(level, R, 0, size - 1)
		if start < 0 or start >= size:  # if not exist, begin from the first
			start = 0
		else:
			Q = canArr[level - 1][start][0:level - 1]
			while Q == R:
				cand = canArr[level - 1][i][0:level] + canArr[level - 1][start][level - 1:level]
				candidate.append(cand)
				start = start + 1
				if start >= size:
					start = 0
					break
				Q = canArr[level - 1][start][0:level - 1]
	candidate = sorted(candidate)


def min_freItem():
	'''
	生成长度为1的频繁模式
	:return:
	'''
	global ww
	counter = dict()
	mine = ''
	my_dict['a'] = 3
	my_dict['g'] = 6
	my_dict['c'] = 6
	my_dict['t'] = 4
	# my_dict['a'] = 1
	# my_dict['b'] = 2
	# my_dict['c'] = 0.3
	# my_dict['d'] = 1
	# my_dict['e'] = 5
	# my_dict['f'] = 2
	for t in range(NumbS):
		S = sDB[t].S
		for s in S:
			mine = s
			if counter.get(mine) == None:
				counter[mine] = 1
			else:
				counter[mine] = counter[mine] + 1
	for iterator in counter.items():
		pp = list(iterator)[0]
		hupval = my_dict[pp[0]]
		if list(iterator)[1] * hupval < minsup:
			uphupval = list(iterator)[1] * 6
			if uphupval >= minsup:
				canArr[0] = canArr[0] + list(iterator)[0]
		else:
			p0 = list(iterator)[0]
			freArr[0].append(p0)
			canArr[0].append(list(iterator)[0])
			unum[ww] = hupval
			ww = ww + 1


def create_subnettree(nettree, parent, L, pop):
	'''
	创建当前节点
	:param nettree:
	:param parent:
	:param L:
	:param pop:
	:return:
	'''
	global ptn_len
	global sub_ptn_list
	global S
	if L > ptn_len + 1:
		return 1
	for i in range(parent + sub_ptn_list[L - 2].min + 1, parent + sub_ptn_list[L - 2].max + 2):
		if i >= len(S):
			continue
		if S[i] == sub_ptn_list[L - 2].end:
			k = len(nettree[L - 1])
			flag = -1
			if k != 0 and nettree[L - 1][k - 1] >= i:
				flag = k - 1
			if flag == -1:
				nettree[L - 1].append(i)
				local = len(nettree[L - 1])
				ident = create_subnettree(nettree, i, L + 1, local - 1)
				if ident == 1:
					return 1
	return 0


def create_nettree(nettree):
	'''
	创建网树
	:param nettree:
	:return:
	'''
	global S
	global ptn_len
	occurnum = 0
	for i in range(ptn_len + 1):
		nettree[i] = []
	for i in range(len(S) - ptn_len):
		if S[i] != sub_ptn_list[0].start:
			continue
		nettree[0].append(i)
		ident = create_subnettree(nettree, i, 2, len(nettree[0]))
		if ident == 1:
			occurnum = occurnum + 1
	return occurnum


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

def clear_mem():
    global K,M,N,S,unum,ww
    global my_dict, sub_ptn_list,ptn_len,sDB
    global minsup,NumbS,freArr,canArr,candidate
    K = 60000  # The sequence number of sequence database
    M = 20000  # The length of pattern
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


def HANP_Miner(filename, mingap, maxgap, minsup, output_filename = 'result_file.txt'):
	clear_mem()
	read_file(filename)
	cannum = 0
	compnum = 0
	global S
	global ww
	global candidate
	begin_time = time_now()
	min_freItem()
	f_level = 1
	gen_candidate(f_level)
	while len(candidate) != 0:
		for can in candidate:
			cannum += 1
			occnum = 0
			hupval = 0
			p = can
			for s in p:
				hupval = hupval + my_dict[s]
			compnum += 1
			for t in range(NumbS):
				if len(sDB[t].S) > 0:
					S = sDB[t].S
					deal_range(p, maxgap, mingap)
					num = 0
					if ptn_len + 1 <= len(S):
						nettree = [0 for i in range(ptn_len + 1)]
						num = create_nettree(nettree)
						del nettree
					occnum = occnum + num
			hupval = occnum * hupval / len(p)
			if hupval >= minsup:
				freArr[f_level].append(p)
				canArr[f_level].append(p)
				unum[ww] = hupval
				ww += 1
			else:
				uphupval = occnum * 6
				if uphupval >= minsup:
					canArr[f_level].append(p)
		f_level += 1
		candidate.clear()
		gen_candidate(f_level)
	end_time = time_now()
	output(f_level, begin_time, end_time, compnum, filename, output_filename)

if (__name__ == '__main__'):
	filename = 'DataSet/baby.txt'
	minlen = 1
	maxlen = 20
	mingap = 0
	maxgap = 3
	minsup = 1200
	HANP_Miner(filename, mingap, maxgap, minsup)