#include <stdio.h>
#include <string>
#include <iostream>
#include <fstream>
#include <windows.h>
#include <map>
#include <vector>
#include <queue>

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
};

struct Candy {
	vector <MLin> preffixTree;
	vector <MLin> suffixTree;
	char element;
};

int NumbS, mins, maxs, stlen, supcount = 0;
double threshold;
int **SDB;
//char charSet[] = { 'a','c','g','t','\0' };
char charSet[] = { 'A','C','G','T','\0' };
//char charSet[] = { 'A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y', '\0' };
//char charSet[] = { 'a','b','c','d','e','f','g','h','i','j','\0' };
int setlen = strlen(charSet);
int **tag;
vector <string> frequent_ARR;
queue <Qpattern> frePats;
vector <Qpattern> sufArr;
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

int min_freItem()	//寻找长度最小的频繁项
{
	node anode;
	vector <MLin> tempArray;
	tempArray.resize(NumbS);
	Qpattern PT;
	int levelLen=0;
	vector <node> **newlevels = (vector <node> **)new vector <node> *[NumbS];
	for (int i = 0; i < NumbS; i++)
	{
		newlevels[i] = new vector <node> [setlen];
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
			sufArr.push_back(PT);//可以作为候选后缀
			frePats.push(PT);//可以作为候选前缀
			levelLen++;
			buff.erase(buff.begin());
			tempArray.clear();
		}	
	}
	return levelLen;
}

int calculate_P(Candy cand) {//需要注意中间间隔负元素的情况两者不能相邻
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
		occnum += sum;
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

void min_frePat(double *offsup) {
	int patLen = 2;
	int levelLen = min_freItem();
	int size = sufArr.size();
	int occnum;
	while (!frePats.empty())
	{
		int genPatNum = 0;
		double freSup = offsup[patLen] * threshold;
		for (int i = 0; i < levelLen; i++)
		{
			Qpattern PT = frePats.front();
			frePats.pop();
			Candy cand;
			cand.preffixTree = PT.allIndex;
			for (int j = 0; j < size; j++)
			{
				cand.suffixTree = sufArr[j].allIndex;
				for (int k = 0; k <= setlen; k++)
				{
					if (k==setlen)
					{
						cand.element = NULL;
						occnum= calculate_P(cand);
					}
					else
					{
						cand.element = charSet[k];
						occnum = calculate_N(cand);
					}
					if (occnum >= threshold* offsup[patLen])
					{
						string Pat = PT.pattern;
						Pat = Pat + sufArr[j].pattern;
						if (k<setlen)
						{
							string p2 = "(-";
							p2 += charSet[k];
							p2 += ')';
							Pat.insert(PT.pattern.length(), p2);//这里检查1.10
						}
						frequent_ARR.push_back(Pat);
						Qpattern NewPT;
						NewPT.pattern = Pat;
						NewPT.allIndex = temp_index;
						frePats.push(NewPT);
						genPatNum++;
					}
					temp_index.clear();
					temp_index.resize(0);
				}
			}
		}
		patLen++;
		levelLen = genPatNum;
	}
}

/*void min_frePat(double *offsup) {
	int patLen = 2;
	int levelLen=min_freItem();
	int size = sufArr.size();
	int occnum;
	while (!frePats.empty())
	{
		int genPatNum = 0;
		double freSup = offsup[patLen] * threshold;
		for (int i = 0; i < levelLen; i++)
		{
			Qpattern PT = frePats.front();
			frePats.pop();
			Candy cand;
			cand.preffixTree = PT.allIndex;
			for (int j = 0; j < size; j++)
			{
				cand.suffixTree = sufArr[j].allIndex;
				cand.element = NULL;
				occnum = calculate_P(cand);
				if (occnum >= freSup)
				{
					string Pat = PT.pattern;
					Pat = Pat + sufArr[j].pattern;
					frequent_ARR.push_back(Pat);
					Qpattern NewPT;
					int len = Pat.length();
					if (Pat[len - 1] != ')')
					{
						NewPT.pattern = Pat;
						NewPT.allIndex = temp_index;
						frePats.push(NewPT);
						genPatNum++;
					}
					for (int k = 0; k < setlen; k++)
					{
						temp_index.clear();
						temp_index.resize(0);
						cand.element = charSet[k];//如果中间不包含负元素的正元素频繁，则为其中插入负元素c
						occnum = calculate_N(cand);
						if (occnum >= threshold* offsup[patLen])
						{
							string p2 = "(-";
							p2 += charSet[k];
							p2 += ')';
							string pat2 = Pat;
							pat2.insert(PT.pattern.length(), p2);//这里检查1.10
							frequent_ARR.push_back(pat2);
							if (Pat[len - 1] != ')')
							{
								NewPT.pattern = pat2;
								NewPT.allIndex = temp_index;
								frePats.push(NewPT);
								genPatNum++;
							}
						}
					}
				}
				temp_index.clear();
				temp_index.resize(0);
			}
		}
		patLen++;
		levelLen = genPatNum;
	}
}*/

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
	min_frePat(offsup);
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