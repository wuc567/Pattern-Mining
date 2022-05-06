#include <stdio.h>
#include <string>
#include <fstream>
#include <iostream>
#include <windows.h>
#include <vector>
#include <map>
#include <math.h>

using namespace std;
#define K 1500    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 20000  //The length of sequence

struct seqdb
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];

struct r_nsp {//�洢��Ƶ��ģʽ�������Ϣ�����ݽṹ
	string pattern;
	int support;
	map<int, int> index;
	bool operator == (const string &p) {
		return (this->pattern == p);
	}
};

struct NSC {//�洢��Ԫ�غ�ѡ�������Ϣ
	string pattern;
	vector <int> NSCid;//��Ԫ������λ��
};

int stlen, NumbS;
double threshold;
int max_s = 0;
int max_rps = 0;
int frenum = 0;
vector <string> *freArr = new vector <string>[M];
char S[N];
vector <string> candidate;
vector <r_nsp> frePSP;
vector <NSC> NSCinfo;

//char charset[] = { 'a','b','\0' };//�ַ���һ��Ҫ��˳��
char charset[] = { 'a','b','c','d','e','f','g','\0' };
//char charset[] = { 'A','B','C','D','E','F','G','H','I','J','\0' };
int setlen = strlen(charset);

int read_file()
{
	fstream file;	//������һ����file
	string buff;
	file.open("credit.txt", ios::in);   //open sequence file
	int i = 0, strLen = 0;
	while (getline(file, buff))	//��file�����ַ�������buff��
	{
		strcpy(sDB[i].S, buff.c_str());	//��buff���Ƹ��������ݿ�sDB��s
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

void min_freItem()	//Ѱ�ҳ�����С��Ƶ����
{
	int *sups = new int[setlen];
	int *sups2 = new int[setlen];
	int *sups3 = new int[setlen];
	bool *tag = new bool[setlen];
	vector <map<int, int>> tempH;
	tempH.resize(setlen);
	for (int i = 0; i < setlen; i++)
	{
		sups[i] = 0;
		sups2[i] = 0;
	}
	for (int t = 0; t < NumbS; t++)	//NumbSΪS����Ŀ
	{
		for (int i = 0; i < setlen; i++)
		{
			tag[i] = false;
			sups3[i] = 0;
		}
		strcpy(S, sDB[t].S);	//���ΰ����п�ÿ�����и�ֵ��S
		for (int i = 0; i<strlen(S); i++)
		{
			for (int j = 0; j < setlen; j++)
			{
				if (S[i] == charset[j])
				{
					sups[j]++;
					sups3[j]++;
					if (tag[j] == false)
					{
						sups2[j]++;
						tag[j] = true;
					}
				}
			}
		}
		for (int i = 0; i < setlen; i++)
		{
			tempH[i].insert(map<int, int>::value_type(t, sups3[i]));
		}
	}
	for (int i = 0; i < setlen; i++)
	{
		if (sups[i] >= max_rps)
		{
			max_rps = sups[i];
		}
		if (sups2[i] >= max_s)
		{
			max_s = sups2[i];
		}
	}
	//printf("%d\t%d\n", max_rps, max_s);
	for (int i = 0; i < setlen; i++)
	{
		if (sups[i] * max_s >= threshold*stlen*max_rps)
		{
			r_nsp node;
			string mine;
			mine.append(1, charset[i]);
			node.pattern = mine;
			node.index = tempH[i];
			node.support = sups2[i];
			frePSP.push_back(node);
			freArr[0].push_back(mine);
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

int LAE(char *p, string S2) {
	int j = 0;
	for (int i = 0; i < S2.length(); i++)
	{
		if (p[j] == S2[i])
		{
			j++;
		}
		if (j == strlen(p))
		{
			return i;
		}
	}
	return 0;
}

int rptGSP(string pattern,int sid, map<int, int> &TempIndex) {
	char p[M];
	strcpy(p, pattern.c_str());
	int t = 0;
	string S2(S);
	int position = LAE(p, S2);  
	while (position>0)
	{
		t++;
		S2 = S2.substr(position + 1);
		position = LAE(p, S2);
	}
	if (t)
	{
		TempIndex.insert(map<int,int>::value_type(sid, t));
	}
	return t;
}

int MPSP(int f_level) {
	gen_candidate(f_level);
	while (candidate.size() != 0)
	{
		for (int i = 0; i < candidate.size(); i++)
		{
			int occnum = 0; //the support num of pattern
			string p = candidate[i];
			map<int, int> TempIndex;
			r_nsp node;
			for (int t = 0; t < NumbS; t++)
			{
				if (strlen(sDB[t].S) > 0)
				{
					strcpy(S, sDB[t].S);
					occnum += rptGSP(p,t, TempIndex);
				}
			}
			if (occnum*max_s >= threshold*stlen*max_rps)
			{
				printf("%s\t%d\n",p.c_str(),occnum);
				frenum++;
				freArr[f_level].push_back(p);
				node.pattern = p;
				node.index= TempIndex;
				frePSP.push_back(node);
			}
		}
		f_level++;
		candidate.clear();
		gen_candidate(f_level);
	}
	return f_level;
}

//�����в���
void findNeg(vector<int> id,string p,int t,NSC nsc) {
	for (int i = 0; i < p.length(); i++)
	{
		vector<int> element_id;
		element_id.assign(id.begin(),id.end());
		element_id.push_back(t+i);
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

//ͨ��Ƶ������ģʽ�ݹ������ģʽ����Ϣ
void GenNSC(){
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
	GenNSC();
	for (int i = 0; i < NSCinfo.size(); i++)
	{
		string pattern = NSCinfo[i].pattern;
		vector <int> v;
		v.assign(NSCinfo[i].NSCid.begin(), NSCinfo[i].NSCid.end());
		v.push_back(-1);
		int Len = v.size();
		string *p = new string[Len];
		//���㸺ģʽ�������ģʽ������p��
		for (int k = 0; k < Len; k++)
		{
			for (int j = 0, t = 0; j < pattern.length() && t<Len; j++)
			{
				if (j == v[t])
				{
					if (j==v[k])
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
		vector<r_nsp>::iterator   iter;
		if (pattern.length()==1)//һ��Ԫ��
		{
			iter = find(frePSP.begin(), frePSP.end(), p[0]);
			int cn = iter->support;
			support = NumbS - cn;
		}
		else//�ฺԪ�صļ������㣬ͨ��ɾ��NSCmap�е�idʵ�֣�������µ�id����Ƶ��id
		{
			iter = find(frePSP.begin(), frePSP.end(), p[Len - 1]);//��ȷ��
			map<int, int> NSCmap = iter->index;
			for (int j = 0; j < Len - 1; j++)//����������һ�ַ���
			{
				vector<r_nsp>::iterator   iter2;
				iter2 = find(frePSP.begin(), frePSP.end(), p[j]);
				map<int, int>::iterator iter3;
				for (iter3 = iter2->index.begin(); iter3 != iter2->index.end(); iter3++)
				{
					int key = iter3->first;
					map<int, int>::iterator iter4;
					iter4 = NSCmap.find(key);
					if (iter4 != NSCmap.end())
					{
						NSCmap.erase(iter4);
					}
				}
			}
			map<int, int>::iterator iter5;
			for (iter5 = NSCmap.begin(); iter5 != NSCmap.end(); iter5++)
			{
				support += iter5->second;
			}
		}
		if (support*max_s >= threshold*stlen*max_rps)
		{
			frenum++;
			printf("%s\t", pattern.c_str());
			for (int j = 0; j < NSCinfo[i].NSCid.size(); j++)
			{
				printf("%d", NSCinfo[i].NSCid[j]);
			}
			printf("\t");
			int Len2 = pattern.length();
			int Len3 = NSCinfo[i].NSCid.size();
			for (int j = 0,k=0; j < Len2; j++)
			{
				if (j== NSCinfo[i].NSCid[k])
				{
					printf("-%c",pattern[j]);
					if (k!=Len3-1)
					{
						k++;
					}
				}
				else
				{
					printf("%c",pattern[j]);
				}
			}
			printf("\t%d", support);
			printf("\n");
		}
	}
}

int main() {
	stlen = read_file();
	cout << "input the threshold:" << endl;
	cin >> threshold;
	DWORD begintime = GetTickCount();
	min_freItem();
	int f_level = 1;
	f_level = MPSP(f_level);
	MNSP();
	DWORD endtime = GetTickCount();
	cout << "The number of frequent patterns:" << frenum << endl;
	//cout << "The time-consuming:" << endtime - begintime << "ms. \n";
	system("pause");
	return 0;
}