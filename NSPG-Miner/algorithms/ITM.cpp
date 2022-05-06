#include <stdio.h>
#include <string>
#include <iostream>
#include <fstream>
#include <windows.h>
#include <map>
#include <vector>

using namespace std;
#define K 600    //The sequence number of sequence database
#define M 20   //The length of pattern
#define N 20000  //The length of sequence

struct seqdb
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];

int NumbS, mins, maxs, stlen;
double threshold;
//char charSet[] = { 'a','b','c','d','e','f','g','h','i','j','\0' };
char charSet[] = { 'a','c','g','t','\0' };//务必是有序的
int setlen = strlen(charSet);
map<int, long> ofsindex;//
int **SDB;
float *pro;//动态数组
vector <string> frequent_ARR;
int supcount = 0;

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

typedef struct T_Node {
	char C;
	Qpattern Pattern;
	vector<int> children;
};

struct Candy {
	string pattern;
	vector <MLin> preffixTree;
	vector <MLin> suffixTree;
};



vector <T_Node> *indexTree = new vector <T_Node>[M];//2yue26
vector <Candy> candidate;
vector <MLin> temp_index;
T_Node Troot;

int read_file()
{
	fstream file;	//定义了一个流file
	char filename[256];
	string buff;
	file.open("DNA6.txt", ios::in);   //open sequence file
									  //file.open("promoter.txt", ios::in);
									  //file.open("random1.txt", ios::in);
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

double getOffSup(char *str, int pLen) {
	double offSup = 0L;
	int index = 0, flex = maxs - mins + 1;
	int strLen = strlen(str);
	long oldOcur = 0;
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
	int proMaxLen = 31;
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
			offsup[j] += getOffSup(sDB[i].S, j);
		}
		ofsindex.clear();
	}
	return offsup;
}

void min_freItem()	//寻找长度最小的频繁项
{
	int *sups = new int[setlen]; //定义一个名为counter的键值对
	for (int i = 0; i < setlen; i++) {
		sups[i] = 0;
	}
	vector <node> **newlevels = (vector <node> **)new vector <node> *[NumbS];
	for (int i = 0; i < NumbS; i++)
	{
		newlevels[i] = new vector <node>[setlen];
	}
	node anode;
	vector <MLin> tempArray;
	Qpattern PT;
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
		if (sups[i] * 1.0 / stlen>threshold) {
			tempArray.resize(NumbS);
			string buff;
			buff.append(1, charSet[i]);
			frequent_ARR.push_back(buff);
			PT.pattern = buff;
			for (int j = 0; j < NumbS; j++)
			{
				MLin ML;
				ML.suffIndex = newlevels[j][i];
				tempArray[j] = ML;
			}
			PT.allIndex = tempArray;
			T_Node tnode;           //不能用malloc，要用new才能用vector！！！
			tnode.C = charSet[i];
			tnode.Pattern = PT;
			indexTree[0].push_back(tnode);//2.26
			int treelen=indexTree[0].size()-1;//2.26  问题就在这一段和之后几行2.27
			Troot.children.push_back(treelen);
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
	return;
}

int calculate(vector <MLin> preffixTree, vector <MLin> suffixTree) {//不完整待校验
	supcount++;
	int occnum = 0;
	for (int t = 0; t < NumbS; t++)
	{
		int sum = 0, j1 = 0;
		vector <node> IND1 = preffixTree[t].suffIndex;
		vector <node> IND2 = suffixTree[t].suffIndex;
		vector <node> IND3;
		for (int i = 0; i < IND2.size(); i++)
		{
			int sn = 0, id2 = IND2[i].name;
			for (int j = j1; j < IND1.size(); j++)
			{
				int id1 = IND1[j].name;
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
			if (sn>0)
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

int get_tnode(string suffix, vector<int> child, int temp) {//这改成返回指针，后面插入父子关系还没有做，记得做
	char c = suffix[temp];
	for (int i = 0; i < child.size(); i++)
	{
		int j = child[i];
		if (indexTree[temp][j].C == c) {
			if (temp < suffix.size() - 1) {
				int temp2=temp+1;
				vector<int> new_child = indexTree[temp][j].children;//真的问题在这里，越级勒，一开始直接越级找了
				j = get_tnode(suffix, new_child, temp2);
			}
			return j;
		}
	}
	return -1;
	//printf("error!没查到你想要的元素\n");
}

void CreatTree(int level, double *offsup)
{
	int size = indexTree[level - 1].size();
	double freSup = offsup[level+1] * threshold;
	double candiSup = offsup[level + 1] * pro[level + 1] * threshold;
	for (int i = 0; i < size;i++) {
		string suffix = indexTree[level - 1][i].Pattern.pattern.substr(1, level - 1);
		vector<int> child;
		vector<int> child2 = Troot.children; 
		int add1;
		if(suffix.length() == 0) {
			child = child2;
		}
		else {
			add1 = get_tnode(suffix, child2, 0);
			if (add1 == -1) {
				continue;
			}
			else
			{
				child = indexTree[level - 2][add1].children;
			}
		}
		vector <MLin> preffixTree = indexTree[level - 1][i].Pattern.allIndex;
		int size2 = child.size();
		for (int j = 0; j < size2; j++)
		{
			int add2 = child[j];
			vector <MLin> suffixTree = indexTree[level - 1][add2].Pattern.allIndex;//这里有问题
			int sup=calculate(preffixTree, suffixTree);
			if (sup>= candiSup)
			{
				T_Node tnode;           
				Qpattern PT;
				string cand = indexTree[level - 1][i].Pattern.pattern;
				cand += indexTree[level - 1][add2].C;
				PT.pattern = cand;
				PT.allIndex = temp_index;
				tnode.C = indexTree[level - 1][add2].C;
				tnode.Pattern = PT;
				indexTree[level].push_back(tnode);
				int treelen = indexTree[level].size() - 1;
				indexTree[level - 1][i].children.push_back(treelen);
				if (sup >= freSup)
				{
					frequent_ARR.push_back(cand);
				}
			}
			temp_index.clear();
			temp_index.resize(0);
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
	int f_level = 1;
	CreatTree(f_level, offsup);
	while (indexTree[f_level].size())
	{
		f_level++;
		if (f_level+1==n)
		{
			break;
		}
		CreatTree(f_level, offsup);
	}
	DWORD endtime = GetTickCount();
	for (int i = 0; i<frequent_ARR.size(); i++)
	{
		cout << frequent_ARR[i] << endl;
		frenum++;
	}
	cout << "The number of frequent patterns:" << frenum << endl;
	cout << "The time-consuming:" << endtime - begintime << "ms. \n";
	cout << "calculate time:" << supcount << endl;
	system("pause");
	return;
}