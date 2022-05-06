#include <stdio.h>
#include <string>
#include <fstream>
#include <iostream>
#include <windows.h>
#include <vector>
#include <map>
#include <utility>
#include <algorithm>

using namespace std;
#define K 1300
//The sequence number of sequence database
#define M 100   //The length of pattern
#define N 20000  //The length of sequence

struct seqdb
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];

struct Nsp {//存储正频繁模式的相关信息的数据结构
	string pattern;
	int support;
	vector<int> index;
	bool operator == (const string &p) {
		return (this->pattern == p);
	}
};

struct NSC {//存储负元素候选的相关信息
	string pattern;
	vector <int> NSCid;//负元素所在位置
};

int stlen, NumbS, threshold;
//char charset[] = {'A','B','C','D','E','F','G','H','I','J','\0'};
//char charset[] = { 'a','c','g','t','\0' };//字符集一定要按顺序！
//char charset[] = { 'a','c','d','e','f','g','h','i','k','l','m','n','p','q','r','s','t','v','w','y','\0'};
//char charset[] = { 'A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y', '\0'};
//char charset[] = { 'b','c','d','e','f','g','h','i','\0'};
//char charset[] = {'1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','\0'};
//char charset[] = { 'a','b','c','d','e','f','g','h','i','j','\0' };
char charset[] = { 'a','b','c','d','e','f','g','\0' };
int setlen = strlen(charset);
int negnum = 0;
vector <Nsp> frePSP;
vector <NSC> NSCinfo;
vector <string> *freArr = new vector <string>[M];
char S[N];
vector <string> candidate;
vector<pair<string, int>> fremap;

bool compare(pair<string, int> map1, pair<string, int> map2)
{
	return map1.second > map2.second;
}

int read_file()
{
	fstream file;	//定义了一个流file
	char filename[256];
	string buff;
	//file.open("Activity.txt", ios::in);   //open sequence file
	//file.open("credit card.txt", ios::in);
	//file.open("HIV2.txt", ios::in);
	//file.open("SDB2.txt", ios::in);
	//file.open("msnbc.txt", ios::in);
	file.open("random2.txt", ios::in);
	//file.open("promoter.txt", ios::in);
	int i = 0, strLen = 0;
	while (getline(file, buff))	//从file读入字符串放入buff中
	{
		strcpy(sDB[i].S, buff.c_str());	//将buff复制给序列数据库sDB的s
		i++;
		strLen += buff.length();
	}
	NumbS = i;
	for (int t = 0; t < NumbS; t++)
	{
		sDB[t].id = t + 1;
	}
	return strLen;
}

void min_freItem()	//寻找长度最小的频繁项
{
	int *sups = new int[setlen]; //定义一个名为counter的键值对
	bool *tag = new bool[setlen];
	vector<int> *temp = new vector<int>[setlen];
	for (int i = 0; i < setlen; i++)
	{
		sups[i] = 0;
	}
	for (int t = 0; t < NumbS; t++)	//NumbS为S的数目
	{
		for (int i = 0; i < setlen; i++)
		{
			tag[i] = false;
		}
		strcpy(S, sDB[t].S);	//依次把序列库每个序列赋值给S
		for (int i = 0; i<strlen(S); i++)
		{
			for (int j = 0; j < setlen; j++)
			{
				if (S[i] == charset[j])
				{
					if (tag[j] == false)
					{
						sups[j]++;
						tag[j] = true;
					}
				}
			}
		}
		for (int i = 0; i < setlen; i++)
		{
			if (tag[i] == true)
			{
				temp[i].push_back(t);
			}
		}
	}
	for (int i = 0; i < setlen; i++)
	{
		if (sups[i] >= threshold)
		{
			string mine;
			mine.append(1, charset[i]);
			freArr[0].push_back(mine);
			Nsp node;
			node.pattern = mine;
			node.support = sups[i];
			node.index = temp[i];
			frePSP.push_back(node);
			fremap.push_back(make_pair(mine, sups[i]));
		}
	}
}

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
		int result = cand.compare(freArr[level - 1][mid].substr(0, level - 1)); //To avoid multiple calls the same function
		if (result == 0)
		{
			//find start
			int slow = low;
			int shigh = mid;
			if (cand.compare(freArr[level - 1][low].substr(0, level - 1)) == 0)
			{
				start = low;
			}
			else
			{
				while (slow<shigh)
				{

					start = (slow + shigh) / 2;
					int sresult = cand.compare(freArr[level - 1][start].substr(0, level - 1));
					if (sresult == 0)   //Only two cases of ==0 and >0
					{
						shigh = start;
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
		else if (result<0)
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

void gen_candidate(int level)
{
	int size = freArr[level - 1].size();
	int start = 0;
	for (int i = 0; i<size; i++)
	{
		string Q = "", R = "";
		R = freArr[level - 1][i].substr(1, level - 1);  //suffix pattern of freArr[level-1][i]
		Q = freArr[level - 1][start].substr(0, level - 1);   //prefix pattern of freArr[level-1][start]
		if (Q != R)
		{
			start = binary_search(level, R, 0, size - 1);
		}
		if (start<0 || start >= size)     //if not exist, begin from the first
			start = 0;
		else
		{
			Q = freArr[level - 1][start].substr(0, level - 1);
			while (Q == R)
			{
				string cand = freArr[level - 1][i].substr(0, level);
				cand = cand + freArr[level - 1][start].substr(level - 1, 1);
				candidate.push_back(cand);
				start = start + 1;
				if (start >= size)
				{
					start = 0;
					break;
				}
				Q = freArr[level - 1][start].substr(0, level - 1);
			}
		}
	}
}

int GSP(string pattern) {
	char p[M];
	strcpy(p, pattern.c_str());
	for (int i = 0, j = 0; i < strlen(S); i++)
	{
		if (p[j] == S[i])
		{
			j++;
		}
		if (j == strlen(p))
		{
			return 1;
		}
	}
	return 0;
}

int MPSP(int f_level) {
	gen_candidate(f_level);
	int something;
	while (candidate.size() != 0)
	{
		for (int i = 0; i < candidate.size(); i++)
		{
			int occnum = 0; //the support num of pattern
			string p = candidate[i];
			vector<int> temp;
			Nsp node;
			for (int t = 0; t < NumbS; t++)
			{
				if (strlen(sDB[t].S) > 0)
				{
					strcpy(S, sDB[t].S);
					something= GSP(p);
					if (something)
					{
						occnum += something;
						temp.push_back(t);
					}
				}
			}
			if (occnum >= threshold)
			{
				freArr[f_level].push_back(p);
				node.pattern = p;
				node.support = occnum;
				node.index = temp;
				frePSP.push_back(node);
				fremap.push_back(make_pair(p, occnum));
			}
		}
		f_level++;
		candidate.clear();
		gen_candidate(f_level);
	}
	return f_level;
}

//负序列部分
void findNeg(vector<int> id, string p, int t, NSC nsc) {
	for (int i = 0; i < p.length(); i++)
	{
		vector<int> element_id;
		element_id.assign(id.begin(), id.end());
		element_id.push_back(t + i);
		nsc.NSCid = element_id;
		NSCinfo.push_back(nsc);
		if (i + 2<p.length())
		{
			string p2 = p.substr(i + 2);
			findNeg(element_id, p2, t + i + 2, nsc);
		}
	}
	return;
}

//通过频繁的正模式递归产生负模式的信息
void GenNSC() {
	int PSPsize = frePSP.size();
	for (int i = 0; i < PSPsize; i++)
	{
		string p = frePSP[i].pattern;
		NSC nsc;
		nsc.pattern = p;
		int length = p.length();
		for (int j = 0; j < length; j++)
		{
			vector<int> element_id;
			element_id.push_back(j);
			nsc.NSCid = element_id;
			NSCinfo.push_back(nsc);
			if (j + 2<p.length())
			{
				string p2 = p.substr(j + 2);
				findNeg(element_id, p2, j + 2, nsc);
			}
		}
	}
	return;
}

void MNSP() {
	string mine;
	GenNSC();
	for (int i = 0; i < NSCinfo.size(); i++)
	{
		string pattern = NSCinfo[i].pattern;
		vector <int> v;
		v.assign(NSCinfo[i].NSCid.begin(), NSCinfo[i].NSCid.end());
		v.push_back(-1);
		int Len = v.size();
		string *p = new string[Len];
		//计算负模式的相关正模式并存在p中
		for (int k = 0; k < Len; k++)
		{
			for (int j = 0, t = 0; j < pattern.length() && t<Len; j++)
			{
				if (j == v[t])
				{
					if (j == v[k])
					{
						p[k] += pattern[j];
					}
					t++;
				}
				else
				{
					p[k] += pattern[j];
				}
			}
		}
		int support = 0;
		vector<Nsp>::iterator   iter;
		if (pattern.length() == 1)//长度为1一个负元素
		{
			iter = find(frePSP.begin(), frePSP.end(), p[0]);
			int cn = iter->support;
			support = NumbS - cn;
		}
		else if(Len==2)//长度为n一个负元素
		{
			iter = find(frePSP.begin(), frePSP.end(), p[1]);
			int no_negitem = iter->support;
			vector<Nsp>::iterator   iter2;
			iter2 = find(frePSP.begin(), frePSP.end(), p[0]);
			int one_negitem = iter2->support;
			support = no_negitem - one_negitem;
		}
		else//多负元素的集合运算，通过删除NSCmap中的id实现，最后留下的id就是频繁id
		{
			iter = find(frePSP.begin(), frePSP.end(), p[Len - 1]);//不确定
			vector<int> NSCmap = iter->index;
			for (int j = 0; j < Len - 1; j++)//可以试试另一种方法
			{
				vector<Nsp>::iterator   iter2;
				iter2 = find(frePSP.begin(), frePSP.end(), p[j]);
				int len2 = iter2->index.size();
				/*if (pattern=="aaa")
				{
					printf("%d\n",len2);
				}*/
				for (int i=0; i<len2; i++)
				{
					vector<int>::iterator iter3 = std::find(NSCmap.begin(), NSCmap.end(), iter2->index[i]);
					if (iter3 != NSCmap.end())
					{
						NSCmap.erase(iter3);
					}
				}
			}
			support = NSCmap.size();
		}
		if (support>= threshold)
		{
			int Len2 = pattern.length();
			int Len3 = NSCinfo[i].NSCid.size();
			for (int j = 0, k = 0; j < Len2; j++)
			{
				if (j == NSCinfo[i].NSCid[k])
				{
					mine.append(1,'-');
					mine.append(1, pattern[j]);
					if (k != Len3 - 1)
					{
						k++;
					}
				}
				else
				{
					mine.append(1, pattern[j]);
				}
			}
			fremap.push_back(make_pair(mine, support));
			mine.erase(mine.begin(),mine.end());
			negnum++;
		}
	}
}

int main() {
	int frenum = 0;
	stlen = read_file();
	cout << "input the threshold:" << endl;
	cin >> threshold;
	DWORD begintime = GetTickCount();
	min_freItem();
	int f_level = 1;
	f_level=MPSP(f_level);
	MNSP();
	DWORD endtime = GetTickCount();
	cout << "The time-consuming:" << endtime - begintime << "ms. \n";
	int fresize = fremap.size();
	cout << "The number of psp:" << frenum << endl;
	cout << "The number of NSP:" << negnum << endl;
	cout << "The number of all:" << fresize << endl;
	sort(fremap.begin(),fremap.end(),compare);
	for (int i = 0; i < fresize; i++)
	{
		printf("%s\t\t%d\n", fremap[i].first.c_str(), fremap[i].second);
	}
	system("pause");
	return 0;
}