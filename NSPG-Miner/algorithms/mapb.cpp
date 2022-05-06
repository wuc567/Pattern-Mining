#include <stdio.h>
#include <string>
#include <stdlib.h>
#include <Windows.h>
#include <iostream> 
#include <vector>
#include <map>
#include <queue>
#include <math.h>
#include <fstream>
#include <iostream>

using namespace std; 

//char charSet[] = { 'A','B','C','D','E','F','H','I','J','\0'};
//char charSet[] = { 'A','B','C','D','E','F','G','H','I','J','\0'};
//char charSet[] = { 'A','B','C','D','E','F','G','H','I','J','K','L','\0' };
//char charSet[] = {'g','k','l','a','e','n','y','i','m','f','t','q','v','d','r','s','h','p','c','w','\0' };
//char charSet[] = { 'A','B','D','E','G','H','I','J','K','M','N','O','\0' };
//char charSet[] = { 'a','b','c','d','e','f','g','h','i','j','\0' };
//char charSet[] = { 'a','b','c','d','e','f','g','\0' };
char charSet[] = { 'a','c','g','t','\0' };
//char charSet[] = { 'b','c','d','e','f','g','h','i','\0' };
//char charset[] = { 'q','m','h','d','f','j','o','p','l','k','g','e','i','n','r','c','b','t','s','a' ,'\0' };
int mins = 0, maxs = 0;
int setlen = strlen(charSet);
int NumbS;//wenjian
int supcount=0;
map<int, long> ofsindex;//检查

struct seqdb//wenjian
{
	int id;                  // sequence id
	char S[20000];              // sequence
} sDB[600];

struct node {
	int name;
	int NRP;
	bool operator == (const int &j) {
		return (this->name == j);
	}
};

struct MLin{
	int id;
	vector <node> suffIndex;
};

struct Qpattern {
	string pattern;
	vector <MLin> allIndex;
	int indexNum;
	int index[2000];
};

queue <Qpattern> frePats;

int read_file()
{
	fstream file;	//定义了一个流file
	string buff;
	int strLen=0;
	//file.open("Location1.txt", ios::in);   //open sequence file
	//file.open("Activity2.txt", ios::in);
	file.open("DNA1.txt", ios::in);
	//file.open("ebola.txt",ios::in);
	//file.open("SDB2.txt", ios::in);
	//file.open("promoter.txt", ios::in);
	//file.open("credit card.txt", ios::in);
	//file.open("Location2.txt", ios::in);
	//file.open("random2.txt",ios::in);
	int i = 0;
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

void getNewLevels(vector <node> **newLevels, long *sups) {
	for (int i = 0; i<setlen; i++) {
		sups[i] = 0;
		for (int j = 0; j < NumbS; j++)
		{
			newLevels[j][i].resize(0);
		}
	}
}

int getLen_1Pats(int **SDB, long *sups, double threshold, string buff, int n,int strLen) {
	vector <node> **newlevels = (vector <node> **)new vector <node> *[NumbS];
	for (int i = 0; i < NumbS; i++)
	{
		newlevels[i] = new vector <node>[setlen];
	}
	getNewLevels(newlevels,sups);
	node anode;
	Qpattern PT;
	vector <MLin> tempArray;
	//Qpattern=NULL;
	for (int i = 0; i < NumbS; i++)
	{
		for (int j = 0; j < strlen(sDB[i].S); j++)
		{
			int k = SDB[i][j];
			sups[k]++;
			int len = newlevels[i][k].size();
			newlevels[i][k].resize(len+1);
			anode.name = j;
			anode.NRP = 1;
			newlevels[i][k][len] = anode;
		}
	}
	for (int i = 0; i<setlen; i++) {
		if (sups[i] * 1.0 / strLen>threshold){
			tempArray.resize(0);
			buff.append(1,charSet[i]);
			PT.pattern = buff;
			for (int j = 0; j < NumbS; j++)
			{
				MLin ML;
				ML.id = i;
				if (newlevels[j][i].size())
				{
					ML.suffIndex = newlevels[j][i];
					int len = tempArray.size();
					tempArray.resize(len + 1);
					tempArray[len] = ML;
					PT.indexNum = len + 1;
					PT.index[len] = j;
				}
			}
			PT.allIndex = tempArray;
			frePats.push(PT);
			buff.erase(buff.begin());
		}
		else {
			for (int j = 0; j < NumbS; j++)
			{
				newlevels[j][i].clear();
				newlevels[j][i].resize(0);
			}
		}
	}
	newlevels = NULL;
	return frePats.size();
}

void IN_Support(Qpattern oldPat, int strLen, int **SDB, vector <node> **newLevel, long *newOcurs) {
	int index = 0, flex = maxs - mins + 1;
	int oldOcur = 0;
	vector<node>::iterator   iter;
	node anode;
	for (int i = 0; i < oldPat.indexNum; i++)
	{
		int z = oldPat.index[i];
		for (iter = oldPat.allIndex[i].suffIndex.begin(); iter != oldPat.allIndex[i].suffIndex.end(); iter++)
		{
			index = iter->name;
			for (int t = 1, j = index + mins + 1; j < strlen(sDB[z].S) &&t <= flex; j++, t++) {
				int c1=SDB[z][j];
				oldOcur = iter->NRP;
				newOcurs[c1] += oldOcur;
				vector<node>::iterator   iter2;
				iter2 = find(newLevel[i][c1].begin(), newLevel[i][c1].end(),j);
				if (iter2== newLevel[i][c1].end())
				{
					int len = newLevel[i][c1].size();
					newLevel[i][c1].resize(len + 1);
					anode.name = j;
					anode.NRP = oldOcur;
					newLevel[i][c1][len] = anode;
				}
				else
				{
					int ocur = iter2->NRP;
					iter2->NRP = ocur + oldOcur;
				}
			}
		}
	}
}

void mineFrePat(int strLen,int n, double threshold, double *offSup,int **SDB,float *pro) {
	string buff;
	Qpattern PT;
	int patLen = 1;
	int frePatsNum = 0;
	long *sup = new long[strlen(charSet)];
	frePatsNum = getLen_1Pats(SDB, sup, threshold, buff, n,strLen);
	int queueLen = frePats.size();
	int genPatNum = 0, Num = frePatsNum;
	vector <MLin> tempArray;
	vector <node> **newLevels = (vector <node> **)new vector <node> *[NumbS];
	for (int i = 0; i < NumbS; i++)
	{
		newLevels[i] = new vector <node>[setlen];
	}
	double freSup = 0.0;
	double candiSup = 0.0;
	while (!frePats.empty())
	{
		printf("the number of frequent patterns of length-%d is %d\n",patLen,Num);
		if (patLen==n+1) {
			newLevels = NULL;
			printf("the maximum capacity of the queue is %d\n", queueLen);
			return;
		}
		Num = 0;
		genPatNum = 0;
		patLen++;
		freSup = offSup[patLen] * threshold;
		candiSup = offSup[patLen] * pro[patLen] * threshold;
		for (int k = 0; k < frePatsNum; k++)
		{
			PT = frePats.front();
			frePats.pop();
			buff.append(PT.pattern);
			getNewLevels(newLevels,sup);
			IN_Support(PT, strLen, SDB, newLevels, sup);
			for (int t = 0; t < setlen; t++)
			{
				if (sup[t] > 0) {
					supcount++;
				}
				if (sup[t] >= candiSup) {
					buff.append(1, charSet[t]);
					if (sup[t] >= freSup)
					{
						printf("第%d层频繁序列包括：%s\t", patLen,buff.c_str());
						printf("\t阈值为:%d%\t%lf\n", sup[t], offSup[patLen]);
						Num++;
					}
					Qpattern newPat;
					newPat.pattern = buff;
					for (int j = 0; j < NumbS; j++)
					{
						MLin ML;
						ML.id = t;
						if (newLevels[j][t].size())
						{
							ML.suffIndex = newLevels[j][t];
							int len = tempArray.size();
							tempArray.resize(len + 1);
							tempArray[len] = ML;
							newPat.indexNum = len + 1;
							newPat.index[len] = j;
						}
					}
					newPat.allIndex = tempArray;
					tempArray.clear();
					tempArray.resize(0);
					frePats.push(newPat);
					genPatNum++;
					buff.erase(buff.end()-1);
					int queueCaptity = frePats.size();
					if (queueCaptity > queueLen) {
						queueLen = queueCaptity;
					}
				}
				else {
					for (int j = 0; j < NumbS; j++)
					{
						newLevels[j][t].clear();
						newLevels[j][t].resize(0);
					}
				}
			}
			PT.pattern = "";
			PT.allIndex.clear();
			buff.erase(buff.begin(), buff.end());
		}
		frePatsNum = genPatNum;
	}
	newLevels = NULL;
	printf("the maximum capacity of the queue is %d\n", queueLen);
}

int main() {
	printf("the name of algorithm is MSPB\n");
	int proMaxLen = 31;
	double threshold = 0.00003;
	int n = 13;
	int stlen = read_file();
	printf("the length of the sequence is %d\n",stlen);
	printf("please input the minimum gap:");
	scanf("%d",&mins);
	printf("please input the maximum gap:");
	scanf("%d",&maxs);
	printf("please input the threshold:");
	scanf("%lf",&threshold);
	printf("please input the possible maximum length of frequent patterns:");
	scanf("%d",&n);
	DWORD time1 = GetTickCount();
	int W = maxs - mins + 1;
	int **SDB = (int **) new int *[NumbS];
	for (int i = 0; i < NumbS; i++)
	{
		SDB[i] = new int[strlen(sDB[i].S)];
		for (int j = 0; j < strlen(sDB[i].S); j++)
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
	double *offsup=new double[proMaxLen]();//动态数组

	float *pro = new float[proMaxLen]();//动态数组
	for (int i = 2; i <= n; i++) {
		pro[i] = (float)((stlen - (n - 1)*((maxs + mins) / 2.0 + 1)) / (stlen - (i - 1)*((maxs + mins) / 2.0 + 1)));
	}
	for (int i = n + 1; i<proMaxLen; i++) {
		pro[i] = 1.0f;
	}

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

	mineFrePat(stlen,n,threshold,offsup,SDB,pro);
	DWORD time2 = GetTickCount();
	cout << "耗时" << time2 - time1 << "ms. \n";
	printf("支持度计算数:%d\n",supcount);
	system("pause");
	return 0;
}