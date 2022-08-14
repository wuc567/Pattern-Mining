﻿#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <stack>
#include <cmath>
#include <cstring>
using namespace std;

#define K 6000   //The sequence number of sequence database
#define M 1000   //The length of pattern
#define N 200000  //The length of sequence
char S[N];  //sequence
int jz = 0;
int h = 0;
//int minlen,maxlen;   //length constraint
int mingap, maxgap; //gap constraint
int store1;
map<char, double> mymap;
struct sub_ptn_struct   //a[0,3]c => start[min,max]end
{
	char start, end;
	int min, max;
};
struct occurrence   //occurrence
{
	vector <int > position;
};
vector <occurrence> store;
sub_ptn_struct sub_ptn[M];  //pattern p[i]
int ptn_len = 0;
int seq_len = 0;



struct storenode
{
	int position;
	int level;
};
//////////////////////////
struct seqdb
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];                 // sequence database
double minsup;
int NumbS;
///////////////////////////


vector <string>* freArr = new vector <string>[M];  //store frequent patterns
vector <string>* canArr = new vector <string>[M];
vector <string> candidate;
vector <string> copattern;
int compnum = 0, frenum = 0;  //compute number and frequents number
//int occurnum=0;

double hupval = 0;
double uphupval = 0;

void deal_range(string pattern)
//put sub-pattern "a[1,3]b" into sub_ptn and sub_ptn.start=a，sub_ptn.end=b, sub_ptn.min=1，sub_ptn.max=3
{
	ptn_len = 0;
	memset(sub_ptn, 0, sizeof(sub_ptn_struct));
	char p[M];
	//strcpy(p,pattern.c_str()); 
	strcpy_s(p, pattern.c_str());
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

//find the first position of cand in the level of canArr by binary search
int binary_search(int level, string cand, int low, int high)
{
	int mid, start;
	if (low > high)
	{
		return -1;
	}
	while (low <= high)
	{
		mid = (high + low) / 2;
		int result = cand.compare(canArr[level - 1][mid].substr(0, level - 1)); //To avoid multiple calls the same function
		if (result == 0)
		{
			int slow = low;
			int shigh = mid;
			int flag = -1;
			if (cand.compare(canArr[level - 1][low].substr(0, level - 1)) == 0)
			{
				start = low;
			}
			else
			{
				while (slow < shigh)
				{

					start = (slow + shigh) / 2;
					int sresult = cand.compare(canArr[level - 1][start].substr(0, level - 1));
					if (sresult == 0)   //Only two cases of ==0 and >0
					{
						shigh = start;
						flag = 0;
					}
					else
					{
						slow = start + 1;
					}
				}
				start = slow;
			}
			return start;
		}
		else if (result < 0)
		{
			high = mid - 1;
		}
		else
		{
			low = mid + 1;
		}
	}
	return -1;
}


void gen_candidate(int level)//使用canArr数组的模式逐层生成候选模式——拼接
{
	int size = canArr[level - 1].size();
	int start = 0;
	for (int i = 0;i < size;i++)
	{
		string Q = "", R = "";
		R = canArr[level - 1][i].substr(1, level - 1);  //suffix pattern of freArr[level-1][i]
		Q = canArr[level - 1][start].substr(0, level - 1);   //prefix pattern of freArr[level-1][start]
		if (Q != R)
		{
			start = binary_search(level, R, 0, size - 1);
		}
		if (start < 0 || start >= size)     //if not exist, begin from the first
			start = 0;
		else
		{
			Q = canArr[level - 1][start].substr(0, level - 1);
			while (Q == R)
			{
				string cand = canArr[level - 1][i].substr(0, level);
				cand = cand + canArr[level - 1][start].substr(level - 1, 1);
				candidate.push_back(cand);
				start = start + 1;
				if (start >= size)
				{
					start = 0;
					break;
				}
				Q = canArr[level - 1][start].substr(0, level - 1);
			}
		}
	}
}

void min_freItem()//生成长度为1的频繁模式
{
	map <string, int > counter;
	string mine;
	for (int t = 0; t < NumbS; t++)
	{
		strcpy_s(S, sDB[t].S);
		//strcpy(S,sDB[t].S);
		for (int i = 0;i < strlen(S);i++)
		{
			mine = S[i];
			counter[mine]++;
		}
	}
	for (map <string, int >::iterator the_iterator = counter.begin(); the_iterator != counter.end(); )
	{
		string pp = the_iterator->first;
		//cout<<the_iterator->first<<":"<<the_iterator->second<<pp[0]<<endl;
		//cout<<the_iterator->first<<":"<<the_iterator->second<<" "<<hupval<<endl ;
		if (the_iterator->second >= minsup)
		{
			freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			canArr[0].push_back(the_iterator->first);
		}
		++the_iterator;
	}
}
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

void read_file()
{
	fstream file;
	char filename[256];
	string buff;
	file.open("gamesale.txt", ios::in);   //open sequence file
	int i = 0;
	while (getline(file, buff))
	{
		strcpy_s(sDB[i].S, buff.c_str());
		//strcpy(sDB[i].S, buff.c_str());
		i++;
	}
	NumbS = i;
	for (int t = 0; t < NumbS; t++)
	{
		sDB[t].id = t + 1;
		//cout << "\t(" << sDB[t].id << ",(" << sDB[t].S << "))" << endl;
	}
}

int main()
{
	read_file();
	cout << "input the mingap,maxgap:" << endl;
	cin >> mingap >> maxgap;
	//mingap=0,maxgap=3;
	cout << "input the minsup:" << endl;
	cin >> minsup;
	//minsup=800;
	cout << "请输入一个前缀:" << endl;
	string pre;
	cin >> pre;


	DWORD begintime = GetTickCount();
	min_freItem();
	int f_level = 1;
	gen_candidate(f_level);
	int cannum = 0;
	while (candidate.size() != 0)
	{
		//int num = 0;

		for (int i = 0;i < candidate.size();i++)
		{
			cannum++;
			int occnum = 0; //the support num of pattern
			//int rest = 0;
			hupval = 0;
			string p = candidate[i];
			compnum++;
			for (int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				if (strlen(sDB[t].S) > 0)
				{
					strcpy_s(S, sDB[t].S);
					//strcpy(S,sDB[t].S);
					deal_range(p);
					int num = 0;
					if (ptn_len + 1 > strlen(S))
					{
						num = 0;
					}
					else {
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
			//cout <<occnum<<" ";
			//cout<<"p="<<p<<"\tnum="<<occnum<<endl;
			if (occnum >= minsup)
			{
				freArr[f_level].push_back(p);
				canArr[f_level].push_back(p);
			}
		}
		f_level++;
		candidate.clear();
		gen_candidate(f_level);
	}
	for (int i = pre.length();i < f_level; i++)
	{
		for (int j = 0;j < freArr[i].size();j++)
		{
			if (freArr[i][j].substr(0, pre.length()) == pre)
			{
				copattern.push_back(freArr[i][j]);
			}
		}
	}
	DWORD endtime = GetTickCount();
	for (int ii = 0; ii < f_level; ii++)
	{
		for (int j = 0; j < freArr[ii].size();j++)
		{
			cout << freArr[ii][j] << "   ";
			frenum++;
		}
		cout << endl;
	}
	cout << "频繁模式数量:" << frenum << endl;
	cout << "候选模式数量:" << cannum << endl;
	cout << "运行时间:" << endtime - begintime << "ms. \n";

	cout << "共生模式：" << copattern.size() << endl;

	for (int ki = 0;ki < copattern.size();ki++)
		cout << copattern[ki] << "\t";
	cout << endl;

	return 0;
}
