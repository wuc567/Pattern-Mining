﻿//共生的无重叠高平均效用，深度优先。
#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <stack>
#include <queue>
//#include<cmath>
using namespace std;
struct pattern
{
	string name;
	int support;
	//	double utl;
};
vector <pattern > CoP;//存储了所有的共生模式
vector <pattern > Max_CoP;//存储了所有的最大共生模式

stack <string > candidate;//存储了所有的候选模式
vector <int > filter1;//设置过滤，长度为1的filter；如果为0，对应ID的sequence被过滤掉；为1进行计算
vector <int > filter;//设置过滤，如果为0，对应ID的sequence被过滤掉；为1进行计算

vector <string > SDB;

//map<char, double> utility;//确定每个字符的效用字典
struct sigma_pos
{
	char ch;
	vector <int>position;
	int fre;//可以做标记，判定是否可以扩展。
};
//vector <sigma_pos> store;
#define Max_Pattern_Length 50

struct sub_ptn_struct   //a[0,3]c => start[min,max]end
{
	char start, end;
	int min, max;
};
#define M 1000   //The length of pattern
sub_ptn_struct sub_ptn[M];  //pattern p[i]
int ptn_len = 0;
int seq_len = 0;
#define N 200000  //The length of sequence
char S[N];  //sequence



struct sigma_sdb
{
	int id;
	//每条序列有自己独有的字符集。
	map<char, int> sigma;//确定每个字符存储在哪里的字典sigma['a']=1,sigma['c']=2,sigma['g']=3
	vector <sigma_pos> store;

};
vector <sigma_sdb> sdbstore;


void read_file()
{
	fstream file;
	char filename[256];
	cout << "---------------------------------------------------------------------------\nPlease input file name:";
	string buff;
	file.open("sars.txt", ios::in);   //open sequence file
	int i = 0;
	while (getline(file, buff))
	{
		SDB.push_back(buff);
		i++;
		cout << buff << endl;
	}
}


void display_store(vector <sigma_pos>& store)
{
	int i, j;
	for (i = 0;i < store.size();i++)
	{
		cout << store[i].ch << ":";
		for (j = 0;j < store[i].position.size();j++)
		{
			cout << store[i].position[j] << "\t";
		}
		cout << endl;
	}
}
void scan_sequence(string sequence, vector <sigma_pos>& store, map<char, int>& sigma)//确定每个字符存储在哪里的字典sigma['a']=1,sigma['c']=2,sigma['g']=3
{//将每条序列中的字符按照位置存储了。
	int count = 1, chno;//第几个字符		
	for (int i = 0;i < sequence.size();i++)
	{
		if (sigma[sequence[i]] == 0)//
		{//新字符
			sigma_pos current;
			sigma[sequence[i]] = count;
			count++;
			current.ch = sequence[i];
			current.position.push_back(i);
			store.push_back(current);
		}
		else
		{//旧字符
			chno = sigma[sequence[i]] - 1;//获取是序列集合中第几个字符
			store[chno].position.push_back(i);
		}
		//cout <<sequence[i]<< ":"<<sigma [sequence[i]]<<"\t"; //debug
	}
	//cout <<endl;
	//display_store(store);
}

struct item
{
	int ID;
	char ch;
	int frequence;
};
void display(vector <item>& itemset)
{
	int i;
	cout << "itemset:\n";
	for (i = 0; i < itemset.size();i++)
	{
		cout << "id:" << itemset[i].ID << "\t chare:" << itemset[i].ch
			<< "\t freq:" << itemset[i].frequence << endl;
	}
}
void display(vector <char>& itemset, map<char, int>& allsig)
{
	int len = allsig.size();
	int len1 = itemset.size();
	for (int i = 0; i < len;i++)
		cout << itemset[i] << ":\t" << allsig[itemset[i]] << endl;
}
void scan_SDB(char first, vector <char>& allsigma, map<char, int>& frequence)
{
	int id;
	for (id = 0;id < SDB.size();id++)
	{
		sigma_sdb tmp;
		tmp.id = id;
		//cout<<endl<<SDB[id]<<endl;
		//对每行序列进行处理。tmp.sigma是字符集
		scan_sequence(SDB[id], tmp.store, tmp.sigma);
		sdbstore.push_back(tmp);
	}
	//string sigma;//每个序列的字符集拼接起来
	vector <item> item_sequence;
	for (id = 0;id < SDB.size();id++)
	{
		int flag = 0;
		for (int j = 0;j < sdbstore[id].store.size();j++)
		{
			//sigma+=sdbstore[id].store[j].ch;
			item tmp;
			tmp.ID = id;
			tmp.ch = sdbstore[id].store[j].ch;
			tmp.frequence = sdbstore[id].store[j].position.size();
			if (tmp.ch == first)
				flag = tmp.frequence;
			item_sequence.push_back(tmp);
		}
		filter1.push_back(flag);//flag要么是0；要么是first在中的频度；
	}
	//display (item_sequence);
	//cout<<sigma<<endl;
	//计算各个字符的出现频度
	for (int i = 0;i < item_sequence.size();i++)
	{
		char t = item_sequence[i].ch;
		if (frequence[t] == 0)
		{//新字符			
			frequence[t] = item_sequence[i].frequence;
			allsigma.push_back(t);
		}
		else
			frequence[t] += item_sequence[i].frequence;
	}
	//display (allsigma,frequence);
}
int depthfirst_support(int node, int level, const string& cand, const  sigma_sdb& seq_store,
	int& mingap, int& maxgap, vector <int >& next, vector <int>& patternv, int* occurrence)
{
	do
	{
		// find the first child of nd according to the gap;
		int childlevel = level;
		int val, child;
		do
		{
			char childch = cand[childlevel];//获得当前模式串
			int childstore = patternv[childlevel];
			int childpos = next[childlevel];
			if (childpos == seq_store.store[childstore].position.size())
				return -3;//已经到了最后的最后，表明不可能再有出现了。
			next[childlevel]++;//仅仅向前处理；
			child = seq_store.store[childstore].position[childpos];//寻找第一个可用的孩子
			val = child - node - 1;
		} while (val < mingap);
		if (mingap <= val && val <= maxgap)//满足间隙约束
		{
			//depthfirst_support(child, level+1, cand, seq_store, mingap, maxgap,  next, patternv);
			occurrence[level] = child;
			node = child;
			level = level + 1;
		}
		else//距离大，需要进行回溯
		{
			//当前结点需要退回
			next[childlevel]--;
			if (level - 2 < 0)
				return -1;//需要找下一个树根
			int cparentpos = next[level - 2] - 1;
			int cparentstore = patternv[level - 2];//??????????
			int cparent = seq_store.store[cparentstore].position[cparentpos];
			//depthfirst_support(cparent, level-1, cand, seq_store, mingap, maxgap,  next, patternv);
			node = cparent;
			level = level - 1;
		}
	} while (level > 0 && level < cand.size());
	if (level == cand.size())
		return level;
	else if (level <= 0)
		return -1;
}
int support_sequence(const string& cand, sigma_sdb& seq_store,
	int& mingap, int& maxgap)
{//计算一个模式在一条序列中支持度
	int sup = 0;
	//cout <<seq_store.id <<endl;	
	vector <int> pv;//模式对应在该序列中存储的位置。
	vector <int >next;
	for (int i = 0;i < cand.size();i++)
	{
		next.push_back(0);//都初始化为0
	}
	for (int i = 0;i < cand.size();i++)
	{
		int val = seq_store.sigma[cand[i]] - 1;//sigma 在存储的时候多了1，因此需要减去1
		if (val == -1)//表明该字符不在该序列中出现。
			return 0;
		pv.push_back(val);
	}
	//vector <int > &rootposition=seq_store.store [pv[0]].position;//树根层
	int rootsize = seq_store.store[pv[0]].position.size();
	vector <int> roots;
	for (int i = 0;i < rootsize;i++)
	{
		int root = seq_store.store[pv[0]].position[i];
		roots.push_back(root);
	}
	for (int len = 0;len < rootsize;len++)//rootposition.size ()存储了树根的个数
	{//每个树根逐一判定
		int root = roots[len];
		int level = 1;
		int occurrence[Max_Pattern_Length] = { 0 };
		occurrence[0] = root;
		next[level - 1] = len + 1;//next指向了每层下一个开始的地方。因此一个出现occ是每层next中对应前面的数据。
		int occ = depthfirst_support(root, level, cand, seq_store, mingap, maxgap, next, pv, occurrence);
		if (occ == cand.size())
		{
			sup++;
		}
		else if (occ == -3)
			break;
	}
	return sup;
}
/*int support_SDB_prefix (string &cand, int &mingap, int &maxgap)
{
	int sup=0;
	int len=cand.size ();
	if (len>=2)
	{
		for (int id=0;id<sdbstore.size ();id++)
		{
			int result;
			result=support_sequence(cand, sdbstore[id], mingap, maxgap);
			filter.push_back (result);
			sup+=result;
			cout <<id<<":"<<result<<endl;
		}
	}
	else
	{//单个字符
		filter=filter1;
		for (int id=0;id<sdbstore.size ();id++)
			sup+=filter[id];
	}

	return sup;
}
int support_SDB (string &cand, int &mingap, int &maxgap)
{
	int sup=0;
	for (int id=0;id<sdbstore.size ();id++)
	{
		//if (filter[id]==1)//filter过滤机制
		if (filter[id])//filter过滤机制
			sup+=support_sequence(cand, sdbstore[id], mingap, maxgap);
	}
	return sup;
}*/
int create_subnettree(vector <int>* nettree, int parent, int L)
//int create_subnettree(vector <int> *nettree,int parent,int L,int pop)
{
	int j = 0;
	if (L > ptn_len + 1)
	{
		return 1;
	}
	int flag = 0;
	int maxbound = parent + sub_ptn[L - 2].max + 1;
	if (strlen(S) < maxbound)
	{
		maxbound = strlen(S);
	}
	for (j = parent + sub_ptn[L - 2].min + 1;j <= maxbound;j++)//间隙约束下查找
	{
		if (S[j] == sub_ptn[L - 2].end)
		{
			int k = nettree[L - 1].size();
			flag = -1;
			if (k != 0)
			{
				if (nettree[L - 1][k - 1] >= j)
				{
					flag = k - 1;
				}
			}
			if (flag == -1)
			{
				int len = nettree[L - 1].size();
				nettree[L - 1].push_back(j);

				int local = nettree[L - 1].size();
				int ident = 0;
				//ident=create_subnettree(nettree,j,L+1,local-1);//j代表网树中的位置，
				ident = create_subnettree(nettree, j, L + 1);
				if (ident == 1)
				{
					return 1;
				}

			}

		}///创建当前节点
	}
	return 0;

}

int create_nettree(vector <int>* nettree)
{
	int occurnum = 0;
	for (int i = 0;i < ptn_len + 1;i++)
		nettree[i].clear();//网树层初始化
	int* start;
	start = new int[ptn_len + 1];
	{
		for (int i = 0;i < ptn_len + 1;i++)
			start[i] = 0;
	}
	{
		for (int i = 0;i < strlen(S) - ptn_len;i++)
		{
			if (S[i] != sub_ptn[0].start)
			{
				continue;
			}
			int len = nettree[0].size();
			nettree[0].push_back(i);
			//int ident=create_subnettree(nettree,i,2,len);
			int ident = create_subnettree(nettree, i, 2);
			if (ident == 1)
			{
				occurnum++;
			}
		}
	}
	delete[]start;
	return occurnum;
}

void deal_range(string pattern, int& mingap, int& maxgap)
//put sub-pattern "a[1,3]b" into sub_ptn and sub_ptn.start=a，sub_ptn.end=b, sub_ptn.min=1，sub_ptn.max=3
{
	ptn_len = 0;
	memset(sub_ptn, 0, sizeof(sub_ptn_struct));
	char p[M];
	//strcpy(p, pattern.c_str());
	strcpy_s(p,pattern.c_str()); 
	if (strlen(p) == 1)
	{
		sub_ptn[ptn_len].start = p[0];
		sub_ptn[ptn_len].max = sub_ptn[ptn_len].min = 0;
	}
	for (int i = 0;i < strlen(p) - 1;i++)
	{
		sub_ptn[ptn_len].start = p[i];
		sub_ptn[ptn_len].end = p[i + 1];
		sub_ptn[ptn_len].min = mingap;
		sub_ptn[ptn_len].max = maxgap;
		ptn_len++;
	}
}
void strcopy(char* target, string& source)
{
	int len = source.size();
	target[len] = 0;
	for (int i = 0;i < len;i++)
		target[i] = source[i];
}
int support(string& pattern, int& mingap, int& maxgap)
{
	int occnum = 0;
	deal_range(pattern, mingap, maxgap);
	for (int t = 0; t < SDB.size(); t++)
	{
		if (SDB[t].size() > 0)
		{
			//strcpy_s(S,SDB[t].S);
			strcopy(S, SDB[t]);
			//deal_range(p);
			int num = 0;
			if (ptn_len + 1 > strlen(S))
			{
				num = 0;
			}
			else
			{
				vector <int>* nettree;
				nettree = new vector <int>[ptn_len + 1];
				num = create_nettree(nettree);
				//cout<<"p="<<p<<"\tnum="<<num<<endl;
				//num=occurnum;//num表示数据集中一条序列中模式的支持度；occurnum是全局变量
				delete[]nettree;
			}
			occnum += num;//occnum是在main函数中定义的，表示这个模式在数据集中的支持度
		}
	}
	return occnum;
}


void enumtree_allsigma(string prefix, vector <char>& allsigma,
	int& mingap, int& maxgap, double minconf)
{
	int candcount = 0;
	do
	{
		int flag = 0;
		for (int i = 0;i < allsigma.size();i++)
		{
			string cand = prefix + allsigma[i];
			int sup = support(cand, mingap, maxgap);
			//int sup=support_SDB(cand,mingap, maxgap);
			//cout <<cand<<":"<<sup<<endl;
			int patternlen = cand.size();
		}
		if (candidate.empty() && flag == 0)
			break;//栈是空的，并且当前模式没有超模式可以进栈。
		prefix = candidate.top();
		candidate.pop();
	} while (1); //while (!candidate.empty ());  这样写不对，最后的prefix没有处理。
	cout << "candidate=" << candcount << endl;
}
void enumtree_BETsigma(string prefix, vector <char>& freq_sigma,
	vector <string>& freq_2pt, map<string, int>& freq_2freq,
	int& mingap, int& maxgap, double min_sup)
{
	int candcount = 0;
	string cur_pattern = prefix;
	int prefixlen = prefix.size();
	do
	{
		int flag = 0;
		for (int i = 0;i < freq_sigma.size();i++)
		{
			char item = freq_sigma[i];
			string cand;
			cand = cur_pattern + item;
			int cur_len = cur_pattern.size();
			if (prefixlen < cur_len)
			{//说明是2层及以上候选模式，需要判定是否可以用BET方式剪枝
				string last2;
				//尾部的两个子串；
				char t = cur_pattern[cur_len - 1];
				last2 = last2 + t + item;
				//判定last2是否在2长度的频繁模式中，如果不在，则进行剪枝
				if (freq_2freq[last2] == 0)
					continue;
			}
			int sup = support(cand, mingap, maxgap);
			//int sup=support_SDB(cand,mingap, maxgap);
			//cout <<cand<<":"<<sup<<endl;  //debug
			if (sup >= min_sup)
			{
				flag = 1;
				pattern tmp;
				tmp.name = cand;
				tmp.support = sup;
				CoP.push_back(tmp);
				candidate.push(cand);
				candcount++;
			}
		}
		if (flag == 0)
		{//实现screening策略，寻找最大共生
			//flag为0，表明所有候选模式都不是共生模式，因此cur_pattern是最大共生模式；
			pattern tmp;
			tmp.name = cur_pattern;
			tmp.support = 1;
			Max_CoP.push_back(tmp);
		}
		if (candidate.empty() && flag == 0)
			break;//栈是空的，并且当前模式没有超模式可以进栈。
		cur_pattern = candidate.top();
		candidate.pop();
	} while (1); //while (!candidate.empty ());  这样写不对，最后的prefix没有处理。
	cout << "candidate=" << candcount << endl;
}


void displayCoP(vector <pattern >& Patterns)
{
	int len = Patterns.size();
	for (int i = 0;i < len;i++)
	{
		cout << Patterns[i].name << ":  " << Patterns[i].support << endl;//": "<<hau[i].utl<<endl;
	}
	cout << len << endl << endl << endl;
}
void	discover_frequent_sigma(
	vector <char>& allsigma, map<char, int>& frequence, double& min_sup,
	vector <char>& freq_sigma, map<char, int>& freq_frequence)
{
	for (int i = 0;i < allsigma.size();i++)
	{
		if (frequence[allsigma[i]] >= min_sup)
		{
			char t = allsigma[i];
			freq_sigma.push_back(t);
			freq_frequence[t] = frequence[allsigma[i]];
		}
	}
}

void discover_frequent_2pattern(
	vector <char>& freq_sigma, map<char, int>& freq_frequence, double& min_sup,
	vector <string>& freq_2pt, map<string, int>& freq_2freq,
	int& mingap, int& maxgap, string& prefix)
{
	//计算2长度的频繁模式
	int candcount = 0;
	int len = prefix.size();
	if (len == 1)
	{//如果前缀是单个字符，需要逐一处理；
		for (int i = 0;i < freq_sigma.size();i++)
			for (int j = 0;j < freq_sigma.size();j++)
			{
				char ti = freq_sigma[i], tj = freq_sigma[j];
				string cand;
				cand = cand + ti + tj;
				//cout <<"2 length candidate:"<<cand<<endl;
				int sup = support(cand, mingap, maxgap);
				//int sup=support_SDB(cand,mingap, maxgap);
				if (sup >= min_sup)
				{
					freq_2pt.push_back(cand);
					freq_2freq[cand] = sup;
					candcount++;
					//cout <<"2 length candidate:"<<cand<<endl;  //debug
				}
			}
	}
	else
	{
		for (int i = 0;i < freq_sigma.size();i++)
			for (int j = 0;j < freq_sigma.size();j++)
			{
				char ti = freq_sigma[i], tj = freq_sigma[j];
				string cand;
				cand = cand + ti + tj;
				int result = prefix.find(cand);
				//cout <<"2 length candidate:"<<cand<<endl;
				if (result == -1)
				{//当前二长度子串不是prefix子序列需要计算；
					int sup = support(cand, mingap, maxgap);
					//int sup=support_SDB(cand,mingap, maxgap);
					if (sup >= min_sup)
					{
						freq_2pt.push_back(cand);
						freq_2freq[cand] = sup;
						candcount++;
						//cout <<"2 length candidate:"<<cand<<endl;
					}
				}
				else
				{//cand是prefix的子序列，无需计算，因为满足Apriori
					//cout<<"prefix的子序列，无需计算，因为满足Apriori\n";
					freq_2pt.push_back(cand);
					freq_2freq[cand] = min_sup + 1;//
				}
			}
	}//cout <<"2 length candidate="<<candcount<<endl;
}
void main()
{
	vector <char> allsigma;
	map<char, int> frequence;
	vector <char> freq_sigma;
	map<char, int> freq_frequence;
	vector <string> freq_2pt;
	map<string, int> freq_2freq;
	int mingap, maxgap;
	double min_conf;
	double min_sup;
	//string seq="acceaabaaccccdcbcca";
	read_file();//读文件
	//initialutility();//效用值
	string prefix;
	cout << "Please input min gap and max gap:";
	cin >> mingap >> maxgap;
	cout << "Please input min confidence:";
	cin >> min_conf;
	cout << "Please input prefix string:";
	cin >> prefix;
	DWORD begintime = GetTickCount();//开始时间
	scan_SDB(prefix[0], allsigma, frequence);
	int prefix_support;
	prefix_support = support(prefix, mingap, maxgap);
	//prefix_support=support_SDB_prefix(prefix,mingap, maxgap);
	min_sup = prefix_support * min_conf;
	//寻找频繁单项
	discover_frequent_sigma(allsigma,
		frequence, min_sup, freq_sigma, freq_frequence);
	//display(freq_sigma, freq_frequence);
	//寻找频繁2长度模式
	discover_frequent_2pattern(freq_sigma, freq_frequence, min_sup,
		freq_2pt, freq_2freq, mingap, maxgap, prefix);
	//enumtree_allsigma(prefix, allsigma,mingap, maxgap, minconf);
	enumtree_BETsigma(prefix, freq_sigma, freq_2pt, freq_2freq, mingap, maxgap, min_sup);
	DWORD endtime = GetTickCount();//222222222222
	cout << "support:" << prefix_support << endl;
	cout << "min support:" << prefix_support * min_conf << endl;


	cout << "时间：" << endtime - begintime << "ms. \n";
	cout << "全部共生频繁模式 \n";
	displayCoP(CoP);
	cout << "最大共生频繁模式 \n";
	displayCoP(Max_CoP);

}