#include <stdio.h>
#include <string>
#include <iostream>
#include <fstream>
#include <windows.h>
#include <map>
#include <vector>

using namespace std;
#define K 1600    //The sequence number of sequence database
#define M 20   //The length of pattern
#define N 20000  //The length of sequence

struct seqdb
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];

struct node {
	int name;
	int NRP;
	bool operator == (const int &j) {
		return (this->name == j);
	}
};

struct MLin {
	vector <node> suffIndex;
};

struct Qpattern {
	string pattern;
	vector <MLin> allIndex;
	int len1;
	int len2;
	char element1;
	char element2;
};

struct Candy {
	string pattern;
	vector <MLin> preffixTree;
	char e1;
	char e2;
};

int NumbS, mins, maxs, stlen, supcount = 0;
int **SDB;
char charSet[] = {'a', 'c','g','t','\0' };
//char charSet[] = { 'A', 'C','G','T','\0' };
//char charSet[] = { 'a', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'y', '\0' };
int setlen = strlen(charSet);
double threshold;
vector <string> frequent_ARR;
vector <Qpattern> *freArr = new vector <Qpattern>[M];
vector <MLin> temp_index;
vector <Candy> candidate;

double *A_offsup(int n) {
	SDB = (int **) new int *[NumbS];
	for (int i = 0; i < NumbS; i++)
	{
		SDB[i] = new int[strlen(sDB[i].S)];
		for (int j = strlen(sDB[i].S) - 1; j >= 0; j--)
		{
			for (int k = 0; k < setlen; k++)
			{
				if (sDB[i].S[j] == charSet[k]) {
					SDB[i][j] = k;
					break;
				}
			}
		}
	}
	int proMaxLen = 31;
	int W = maxs - mins + 1;
	if (proMaxLen<n * 2) {
		proMaxLen = n * 2 + 1;
	}
	double *offsup = new double[proMaxLen]();//动态数组
	for (int j = 2; j<proMaxLen; j++) {
		offsup[j] = stlen*pow(W, j - 1);
	}
	return offsup;
}

int read_file()
{
	fstream file;	//定义了一个流file
	char filename[256];
	string buff;
	file.open("Virus1.txt", ios::in);   //open sequence file
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
	node anode;
	vector <MLin> tempArray;
	tempArray.resize(NumbS);
	Qpattern PT;
	vector <node> **newlevels = (vector <node> **)new vector <node> *[NumbS];
	for (int i = 0; i < NumbS; i++)
	{
		newlevels[i] = new vector <node>[setlen];
	}
	int *sups = (int *) new int[setlen];
	for (int i = 0; i < setlen; i++)
	{
		sups[i] = 0;
	}
	for (int i = 0; i < NumbS; i++)
	{
		for (int j = 0; j < strlen(sDB[i].S); j++)
		{
			int k = SDB[i][j];
			sups[k]++;
			anode.name = j;
			anode.NRP = 1;
			newlevels[i][k].push_back(anode);
		}
	}
	for (int i = 0; i < setlen; i++) {
		if (sups[i] * 1.0 / stlen >= threshold)
		{
			PT.element2 = charSet[i];
			string buff;
			buff.append(1, charSet[i]);
			frequent_ARR.push_back(buff);//进入频繁模式集
			PT.pattern = buff;
			tempArray.resize(NumbS);
			for (int t = 0; t < NumbS; t++)
			{
				MLin ML;
				ML.suffIndex = newlevels[t][i];
				tempArray[t] = ML;
			}
			PT.allIndex = tempArray;
			freArr[0].push_back(PT);
			buff.erase(buff.begin());
			tempArray.clear();
		}
	}
}

int matching(Candy cand) {//模式匹配方法太慢
	supcount++;
	int occnum = 0;
	char pre = cand.e1;
	char c = cand.e2;
	for (int t = 0; t < NumbS; t++) {
		vector <node> IND1 = cand.preffixTree[t].suffIndex;
		vector <node> IND2;
		for (int i = 0; i < IND1.size(); i++)
		{
			int index=IND1[i].name;
			int flag = 0;
			for (int j = index + 1, k = index + 1; j < strlen(sDB[t].S) && k <= index + maxs + 1; j++, k++)
			{
				if (flag==1)
				{
					break;
				}
				if (pre == sDB[t].S[j])//间隙出现负元素则标记
				{
					flag = 1;
				}
				if (c!=sDB[t].S[j])//正元素不对应
				{
					continue;
				}
				occnum += IND1[i].NRP;
				vector<node>::iterator   iter;
				iter = find(IND2.begin(), IND2.end(), j);
				if (iter == IND2.end())
				{
					node anode;
					anode.name = j;
					anode.NRP = IND1[i].NRP;
					IND2.push_back(anode);
				}
				else
				{
					iter->NRP+= IND1[i].NRP;
				}
			}
		}
		MLin ML;
		ML.suffIndex = IND2;
		temp_index.push_back(ML);
	}
	return occnum;
}

void deal_len2(double *offsup) {
	int size = freArr[0].size();
	for (int i = 0; i < size; i++)
	{
		for (int j = 0; j < size; j++)
		{
			Candy cand;
			string pat = freArr[0][i].pattern;
			pat += freArr[0][j].pattern;
			cand.pattern = pat;
			cand.preffixTree = freArr[0][i].allIndex;
			cand.e1 = NULL;
			cand.e2 = freArr[0][j].element2;
			int occnum = matching(cand);
			if (occnum >= threshold*offsup[2])
			{
				Qpattern PT;
				PT.pattern = pat;
				frequent_ARR.push_back(pat);
				PT.allIndex = temp_index;
				PT.element1 = NULL;
				PT.element2 = cand.e2;
				PT.len1 = 1;
				PT.len2 = 1;
				freArr[1].push_back(PT);
				//处理负元素
				for (int i = 0; i < setlen; i++)
				{
					temp_index.clear();
					temp_index.resize(0);
					cand.e1 = charSet[i];//如果中间不包含负元素的正元素频繁，则为其中插入负元素c
					occnum = matching(cand);
					//printf("%s\t%c\t%d\n",pat.c_str(),c,occnum);
					if (occnum >= threshold*offsup[2])
					{
						string p2 = "(-";
						p2 += charSet[i];
						p2 += ')';
						string pat2 = pat;
						pat2.insert(1, p2);//这里检查1.10
						frequent_ARR.push_back(pat2);
						PT.pattern = pat2;
						PT.allIndex = temp_index;
						PT.element1 = charSet[i];
						PT.len1 = 5;
						PT.len2 = 5;
						freArr[1].push_back(PT);
					}
				}
			}
			temp_index.clear();
			temp_index.resize(0);
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
		int len = freArr[level - 1][mid].pattern.length() - freArr[level - 1][mid].len2;
		int result = cand.compare(freArr[level - 1][mid].pattern.substr(0, len));
		if (result == 0)
		{
			int slow = low;
			int shigh = mid;
			int len2 = freArr[level - 1][low].pattern.length() - freArr[level - 1][low].len2;
			if (cand.compare(freArr[level - 1][low].pattern.substr(0, len2)) == 0)
			{
				start = low;
			}
			else
			{
				while (slow<shigh)
				{
					start = (slow + shigh) / 2;
					int len3 = freArr[level - 1][start].pattern.length() - freArr[level - 1][start].len2;
					int sresult = cand.compare(freArr[level - 1][start].pattern.substr(0, len3));
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

void gen_candidate(int level)//两大不确定，1：顺序。2：1元素时的遍历顺序
{
	int size = freArr[level - 1].size();
	int start;
	Candy tempcand;
	for (int i = 0; i < size; i++)
	{
		start = 0;
		string Q = "", R = "";
		int len1 = freArr[level - 1][i].len1;
		int len2 = freArr[level - 1][start].pattern.length() - freArr[level - 1][start].len2;
		R = freArr[level - 1][i].pattern.substr(len1);
		Q = freArr[level - 1][start].pattern.substr(0, len2);
		//printf("%s\n", R.c_str());
		//printf("%s\n", Q.c_str());
		if (Q != R)
		{
			start = binary_search(level, R, 0, size - 1);
		}
		if (start<0 || start >= size)     //if not exist, begin from the first
			start = 0;
		else {
			len2 = freArr[level - 1][start].pattern.length() - freArr[level - 1][start].len2;
			Q = freArr[level - 1][start].pattern.substr(0, len2);
			while (Q == R)
			{
				string cand = freArr[level - 1][i].pattern;
				cand = cand + freArr[level - 1][start].pattern.substr(len2);
				tempcand.pattern = cand;
				tempcand.preffixTree = freArr[level - 1][i].allIndex;
				tempcand.e1 = freArr[level - 1][start].element1;
				tempcand.e2= freArr[level - 1][start].element2;
				candidate.push_back(tempcand);
				start = start + 1;
				if (start >= size)
				{
					start = 0;
					break;
				}
				len2 = freArr[level - 1][start].pattern.length() - freArr[level - 1][start].len2;
				Q = freArr[level - 1][start].pattern.substr(0, len2);
			}
		}
	}
}

void main() {
	stlen = read_file();
	int frenum = 0, n = 0;
	cout << "input the mingap,maxgap:" << endl;
	cin >> mins >> maxs;
	cout << "input the threshold:" << endl;
	cin >> threshold;
	cout << "input the maxlen of pattern:" << endl;
	cin >> n;
	DWORD begintime = GetTickCount();
	double *offsup = A_offsup(n);
	min_freItem();
	deal_len2(offsup);//单独处理长度为2的
	int f_level = 2;
	gen_candidate(f_level);
	while (candidate.size() != 0)
	{
		for (int i = 0; i < candidate.size(); i++)
		{
			Candy cand_p = candidate[i];
			//printf("%s\n", cand_p.pattern.c_str());
			int occnum = matching(cand_p);
			if (occnum >= threshold*offsup[f_level + 1])
			{
				Qpattern Pat;
				Pat.allIndex = temp_index;
				string pattern = cand_p.pattern;
				frequent_ARR.push_back(pattern);
				Pat.pattern = pattern;
				/*printf("%s\t", cand_p.pattern.c_str());
				printf("%d\n", occnum);*/
				int len = pattern.length();
				int templen1 = 1, templen2 = 1;
				if (pattern[1] == '(')
				{
					templen1 += 4;
				}
				Pat.len1 = templen1;
				if (pattern[len - 2] == ')')
				{
					templen2 += 4;
				}
				Pat.len2 = templen2;
				Pat.element1 = cand_p.e1;
				Pat.element2 = cand_p.e2;
				freArr[f_level].push_back(Pat);
			}
			temp_index.clear();
			temp_index.resize(0);
		}
		f_level++;
		candidate.clear();
		candidate.resize(0);//new
		gen_candidate(f_level);
	}
	DWORD endtime = GetTickCount();
	int len = frequent_ARR.size();
	for (int i = 0; i < len; i++)
	{
		printf("%s\n", frequent_ARR[i].c_str());
		frenum++;
	}
	cout << "频繁模式数：" << frenum << "\n";
	cout << "耗时" << endtime - begintime << "ms. \n";
	cout << "支持度计算数：" << supcount << endl;
	system("pause");
	return;
}