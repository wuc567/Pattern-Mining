#pragma warning(disable : 4786)
#pragma warning(disable:4996)
#include <stdio.h>
#include <string>
#include <fstream>
#include <iostream>
#include <windows.h>
#include <vector>
#include <map>

using namespace std;
#define K 600    
#define M 100  
#define N 20000  

struct seqdb
{
	int id;                  
	char S[N];              
} sDB[K];

struct Nsp {
	string pattern;
	int support;
	vector<int> index;
	bool operator == (const string& p) {
		return (this->pattern == p);
	}
};

struct NSC {
	string pattern;
	vector <int> NSCid;
};

int stlen, NumbS, threshold;
//char charset[] = { 'a','c','d','e','f','g','h','i','k','l','m','n','p','q','r','s','t','v','w','y','\0' };
//char charset[] = { 'a','c','d','e','f','h','i','m','o','p','r','s','t','u','\0' };
//char charset[] = { 'b','c','d','e','f','g','h','i','j','\0' };
//char charset[] = { 'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','\0' };
//char charset[] = { 'a','b','c','d','e','f','g','\0' };
//char charset[] = { 'a','b','c','d','e','f','g','h','i','j','k','l','m','\0' };
//char charset[] = { 'a','c','e','g','i','k','m','o','\0' };
//char charset[] = { 'a','c','g','t','\0' };
char charset[] = { 'A','B','C','D','E','F','G','H','I','J','\0' };
int setlen = strlen(charset);
int negnum = 0;
vector <Nsp> frePSP;
vector <NSC> NSCinfo;
vector <string>* freArr = new vector <string>[M];
char S[N];
vector <string> candidate;

int read_file()
{
	fstream file;	
	char filename[256];
	string buff;
	//file.open("SDB1.txt",ios::in);
	//file.open("SDB2.txt",ios::in);
	//file.open("SDB3.txt",ios::in);
	//file.open("SDB4.txt",ios::in);
	 file.open("SDB5.txt", ios::in);
	//file.open("SDB6.txt",ios::in);
	//file.open("SDB7.txt",ios::in);
	//file.open("SDB8.txt",ios::in);
	//file.open("SDB9.txt",ios::in);
   //file.open("SDB10.txt",ios::in);
   //file.open("SDB11.txt",ios::in);
	int i = 0, strLen = 0;
	while (getline(file, buff))	
	{
		strcpy(sDB[i].S, buff.c_str());	
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

void min_freItem()	
{
	int* sups = new int[setlen]; 
	bool* tag = new bool[setlen];
	vector<int>* temp = new vector<int>[setlen];
	for (int i = 0; i < setlen; i++)
	{
		sups[i] = 0;
	}
	for (int t = 0; t < NumbS; t++)
	{
		for (int i = 0; i < setlen; i++)
		{
			tag[i] = false;
		}
		strcpy(S, sDB[t].S);
		for (int i = 0; i < strlen(S); i++)
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
			printf("%c: %d\n", charset[i], sups[i]);
			string mine;
			mine.append(1, charset[i]);
			freArr[0].push_back(mine);
			Nsp node;
			node.pattern = mine;
			node.support = sups[i];
			node.index = temp[i];
			frePSP.push_back(node);
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
		int result = cand.compare(freArr[level - 1][mid].substr(0, level - 1)); 
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
				while (slow < shigh)
				{

					start = (slow + shigh) / 2;
					int sresult = cand.compare(freArr[level - 1][start].substr(0, level - 1));
					if (sresult == 0)  
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

void gen_candidate(int level)
{
	int size = freArr[level - 1].size();
	int start = 0;
	for (int i = 0; i < size; i++)
	{
		string Q = "", R = "";
		R = freArr[level - 1][i].substr(1, level - 1); 
		Q = freArr[level - 1][start].substr(0, level - 1);   
		if (Q != R)
		{
			start = binary_search(level, R, 0, size - 1);
		}
		if (start < 0 || start >= size)    
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
			int occnum = 0; 
			string p = candidate[i];
			vector<int> temp;
			Nsp node;
			for (int t = 0; t < NumbS; t++)
			{
				if (strlen(sDB[t].S) > 0)
				{
					strcpy(S, sDB[t].S);
					something = GSP(p);
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
			}
		}
		f_level++;
		candidate.clear();
		gen_candidate(f_level);
	}
	return f_level;
}

void findNeg(vector<int> id, string p, int t, NSC nsc) {
	for (int i = 0; i < p.length(); i++)
	{
		vector<int> element_id;
		element_id.assign(id.begin(), id.end());
		element_id.push_back(t + i);
		nsc.NSCid = element_id;
		NSCinfo.push_back(nsc);
		if (i + 2 < p.length())
		{
			string p2 = p.substr(i + 2);
			findNeg(element_id, p2, t + i + 2, nsc);
		}
	}
	return;
}

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
			if (j + 2 < p.length())
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
		string* p = new string[Len];
		for (int k = 0; k < Len; k++)
		{
			for (int j = 0, t = 0; j < pattern.length() && t < Len; j++)
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
		if (pattern.length() == 1)
		{
			iter = find(frePSP.begin(), frePSP.end(), p[0]);
			int cn = iter->support;
			support = NumbS - cn;
		}
		else if (Len == 2)
		{
			iter = find(frePSP.begin(), frePSP.end(), p[1]);
			int no_negitem = iter->support;
			vector<Nsp>::iterator   iter2;
			iter2 = find(frePSP.begin(), frePSP.end(), p[0]);
			int one_negitem = iter2->support;
			support = no_negitem - one_negitem;
		}
		else
		{
			iter = find(frePSP.begin(), frePSP.end(), p[Len - 1]);
			vector<int> NSCmap = iter->index;
			for (int j = 0; j < Len - 1; j++)
			{
				vector<Nsp>::iterator   iter2;
				iter2 = find(frePSP.begin(), frePSP.end(), p[j]);
				int len2 = iter2->index.size();
				for (int i = 0; i < len2; i++)
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
		if (support >= threshold)
		{
			int Len2 = pattern.length();
			int Len3 = NSCinfo[i].NSCid.size();
			for (int j = 0, k = 0; j < Len2; j++)
			{
				if (j == NSCinfo[i].NSCid[k])
				{
					if (k != Len3 - 1)
					{
						k++;
					}
				}
			}
			if (pattern.length() > 1)
			{
				iter->support;
			}
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
	f_level = MPSP(f_level);
	
	for (int i = 0; i < f_level; i++)
	{
		for (int j = 0; j < freArr[i].size(); j++)
		{
			frenum++;
		}
	}
	MNSP();
	DWORD endtime = GetTickCount();
	cout << "The number of psp:" << frenum << endl;
	cout << "The number of NSP:" << negnum << endl;
	cout << "The time-consuming:" << endtime - begintime << "ms. \n";
	system("pause");
	return 0;
}