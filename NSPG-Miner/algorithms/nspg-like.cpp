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
};

struct MLin {
	vector <node> suffIndex;
};

struct Qpattern {
	string pattern;
	vector <MLin> allIndex;
	int len1;
	int len2;
	char element;
};

struct Candy {
	string pattern;
	vector <MLin> preffixTree;
	vector <MLin> suffixTree;
	char element;
};

int NumbS, mins, maxs, stlen,supcount=0, proMaxLen = 31;
double threshold;
map<int, long> ofsindex;
float *pro;//动态数组
int **SDB;
//char charSet[] = { 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','\0' };
//char charSet[] = { 'a','c','g','t','\0' };
char charSet[] = { 'A','C','G','T','\0' };
//char charSet[] = { 'A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y', '\0' };
//char charSet[] = { 'a','b','c','d','e','f','g','h','i','j','\0' };
//char charSet[] = { 'a', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'y', '\0' };
int setlen = strlen(charSet);
vector <string> frequent_ARR;
vector <Qpattern> *freArr= new vector <Qpattern>[M];
vector <Candy> candidate;
vector <MLin> temp_index;

int read_file()
{
	fstream file;	//定义了一个流file
	char filename[256];
	string buff;
	file.open("Virus2.txt", ios::in);   //open sequence file
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

double getOffSup(char *str) {
	double offSup = 0L;
	int index = 0, flex = maxs - mins + 1;
	long oldOcur = 0;
	int strLen = strlen(str);
	map<int, long> newOfsIndex;
	map<int, long>::iterator   iter;
	for (iter = ofsindex.begin(); iter != ofsindex.end(); iter++) {
		index = iter->first;
		for (int t = 1, j = index + mins + 1; j<strLen&&t <= flex; j++, t++) {
			oldOcur = iter->second;
			offSup += oldOcur;
			map<int, long>::iterator iter2;
			iter2 = newOfsIndex.find(j);
			if (iter2 == newOfsIndex.end()) {//if not contain new node;
				newOfsIndex.insert(map<int, long>::value_type(j, oldOcur));
			}
			else {                       //if contain new node;
				long newOcur = iter2->second + oldOcur;
				newOfsIndex[j] = newOcur;
			}
		}
	}
	ofsindex.clear();
	ofsindex = newOfsIndex;
	return offSup;
}

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
	int l1 = (stlen + maxs) / (maxs + 1);
	if (n>l1) n = l1;
	if (proMaxLen<n * 2) {
		proMaxLen = n * 2 + 1;
	}
	pro = new float[proMaxLen]();
	for (int i = 2; i <= n; i++) {
		pro[i] = (float)((stlen - (n - 1)*((maxs + mins) / 2.0 + 1)) / (stlen - (i - 1)*((maxs + mins) / 2.0 + 1)));
	}
	for (int i = n + 1; i<proMaxLen; i++) {
		pro[i] = 1.0f;
	}
	double *offsup = new double[proMaxLen]();//动态数组
	for (int j = 2; j<proMaxLen; j++) {
		offsup[j] = 0;
	}
	for (int i = 0; i < NumbS; i++)
	{
		for (int j = 0; j<strlen(sDB[i].S); j++) {
			ofsindex.insert(map<int, long>::value_type(j, 1L));//检查
		}
		for (int j = 2; j<proMaxLen; j++) {
			offsup[j] += getOffSup(sDB[i].S);
		}
		ofsindex.clear();
	}
	return offsup;
}

void min_freItem()	//寻找长度最小的频繁项
{
	node anode;
	vector <MLin> tempArray;
	tempArray.resize(NumbS);
	Qpattern PT;
	vector <node> **newlevels = (vector <node> **)new vector <node> [NumbS];
	for (int i = 0; i < NumbS; i++)
	{
		newlevels[i] = new vector <node> [setlen];
	}
	int *sups = (int *) new int [setlen];
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
			PT.len1 = 1;//用于取前缀
			PT.len2 = 1;//用于取后缀
			freArr[0].push_back(PT);//取其后缀，可以作为候选前缀
			buff.erase(buff.begin());
			tempArray.clear();
		}
	}
}

int calculate_P(Candy cand) {
	supcount++;
	int occnum=0;
	for (int t = 0; t < NumbS; t++) {
		int sum = 0, j1 = 0;
		vector <node> IND1 = cand.preffixTree[t].suffIndex;
		vector <node> IND2 = cand.suffixTree[t].suffIndex;
		vector <node> IND3;
		for (int i = 0; i < IND2.size(); i++)
		{
			int sn = 0, id2 = IND2[i].name;
			for (int j = j1; j < IND1.size(); j++)
			{
				int id1 = IND1[j].name;
				string s = sDB[t].S;
				if (id2 - id1<mins + 1)
				{
					break;
				}
				else if (id2 - id1>maxs + 1)
				{
					j1 = j + 1;
					continue;
				}
				else
				{
					sn = sn + IND1[j].NRP;
				}
			}
			if (sn > 0)
			{
				node nd;
				nd.name = id2;
				nd.NRP = sn;
				IND3.push_back(nd);
				sum += sn;
			}
		}
		MLin ML;
		ML.suffIndex = IND3;
		int len = temp_index.size();
		temp_index.push_back(ML);
		occnum+=sum;
	}
	return occnum;
}

int calculate_N(Candy cand) {//需要注意中间间隔负元素的情况两者不能相邻
	supcount++;
	int occnum = 0;
	for (int t = 0; t < NumbS; t++) {
		int sum = 0, j1 = 0;
		vector <node> IND1 = cand.preffixTree[t].suffIndex;
		vector <node> IND2 = cand.suffixTree[t].suffIndex;
		vector <node> IND3;
		for (int i = 0; i < IND2.size(); i++)
		{
			int sn = 0, id2 = IND2[i].name;
			for (int j = j1; j < IND1.size(); j++)
			{
				int id1 = IND1[j].name;
				string s = sDB[t].S;
				char c = cand.element;
				if (id2 - id1<mins + 1)
				{
					break;
				}
				/*else if (id2 - id1 == 1)//这句话有问题
				{
					break;
				}*/
				else if (id2 - id1>maxs + 1)
				{
					j1 = j + 1;
					continue;
				}
				else if (s.substr(id1 + 1, id2 - id1 - 1).find(c) != -1)//这里得改
				{
					j1 = j + 1;//这里不确定
					continue;
				}
				else
				{
					sn = sn + IND1[j].NRP;
				}
			}
			if (sn > 0)
			{
				node nd;
				nd.name = id2;
				nd.NRP = sn;
				IND3.push_back(nd);
				sum += sn;
			}
		}
		MLin ML;
		ML.suffIndex = IND3;
		int len = temp_index.size();
		temp_index.push_back(ML);
		occnum += sum;
	}
	return occnum;
}

void deal_len2(double *offsup) {
	int size =freArr[0].size();
	double freSup = offsup[2] * threshold;
	double candiSup = offsup[2] * pro[2] * threshold;
	for (int i = 0; i < size; i++)
	{
		for (int j = 0; j < size; j++)
		{
			Candy cand;
			string pat = freArr[0][i].pattern;
			pat += freArr[0][j].pattern;
			cand.pattern = pat;
			cand.preffixTree = freArr[0][i].allIndex;
			cand.suffixTree = freArr[0][j].allIndex;
			cand.element = NULL;
			int occnum =  calculate_P(cand);
			if (occnum >= candiSup)
			{
				Qpattern PT;
				PT.pattern = pat;
				if (occnum >= freSup)
				{
					frequent_ARR.push_back(pat);
				}
				PT.allIndex = temp_index;
				PT.element = NULL;
				PT.len1 = 1;
				PT.len2 = 1;
				freArr[1].push_back(PT);
				//处理负元素
				for (int i = 0; i < setlen; i++)
				{
					temp_index.clear();
					temp_index.resize(0);
					cand.element = charSet[i];//如果中间不包含负元素的正元素频繁，则为其中插入负元素c
					occnum = calculate_N(cand);
					//printf("%s\t%c\t%d\n",pat.c_str(),c,occnum);
					if (occnum >= candiSup)
					{
						string p2 = "(-";
						p2 += charSet[i];
						p2 += ')';
						string pat2 = pat;
						pat2.insert(1,p2);//这里检查1.10
						if (occnum >= freSup)
						{
							frequent_ARR.push_back(pat2);
						}
						PT.pattern = pat2;
						PT.allIndex = temp_index;
						PT.element = charSet[i];
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
		int result = cand.compare(freArr[level - 1][mid].pattern.substr(0,len));
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
		Q = freArr[level - 1][start].pattern.substr(0,len2);
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
				tempcand.suffixTree = freArr[level - 1][start].allIndex;
				tempcand.element = freArr[level - 1][start].element;
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
		double freSup = offsup[f_level + 1] * threshold;
		double candiSup = offsup[f_level + 1] * pro[f_level + 1] * threshold;
		for (int i = 0; i < candidate.size(); i++)
		{
			Candy cand_p = candidate[i];
			//printf("%s\n", cand_p.pattern.c_str());
			int occnum;
			if (cand_p.element==NULL)
			{
				occnum = calculate_P(cand_p);
			}
			else
			{
				occnum = calculate_N(cand_p);
			}
			if (occnum >= candiSup)
			{
				Qpattern Pat;
				Pat.allIndex = temp_index;
				string pattern = cand_p.pattern;
				if (occnum >= freSup)
				{
					frequent_ARR.push_back(pattern);
				}
				Pat.pattern = pattern;
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
				Pat.element = cand_p.element;
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