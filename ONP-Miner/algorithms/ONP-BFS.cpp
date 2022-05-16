#pragma warning(disable : 4786)
#pragma warning(disable:4996)
#include <stdio.h>
#include <string>
#include <iostream>
#include <fstream>
#include <windows.h>
#include <math.h>
#include <map>
#include <vector>
using namespace std;
#define K 1000  
#define M 1000   
#define N 200000  

struct element
{
	char ch;
	bool flag;
};
element chp[M];

struct gapnit
{
	element start;
	element nchar;
	int min, max;
};
gapnit gapp[M];

struct sele
{
	char sch;
	bool flag;
};
sele sq[N];

struct seqdb
{
	int id;                  
	char s[N];              
} sDB[K];

struct node {
	int name;
	int sum;
};

struct pfix
{
	string frp;
	string prefix;
	string suffix;
	int len2;
};

int NumbS;
int s_len;
int gapp_len;
int stlen;
int mins, maxs;
int threshold;
char S[N];
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
vector <string>* freArr = new vector <string>[M];
vector <pfix>* fix = new vector <pfix>[M];
vector <string> candidate;
vector <string>* posfre = new vector <string>[M];
int read_file()
{
	fstream file;
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
	string buff;
	if (!file.is_open())
	{
		cout << "未打开" << endl;
		exit(EXIT_FAILURE);
	}
	int i = 0, strLen = 0;
	while (getline(file, buff))	
	{
		strcpy(sDB[i].s, buff.c_str());	
		i++;
		strLen += buff.length();
	}
	NumbS = i;
	cout << "ppppppppp" << NumbS << endl;
	for (int t = 0; t < NumbS; t++)
	{
		sDB[t].id = t + 1;
	}

	return strLen;
}
bool isalpha(char a)     
{
	if ((a >= 97 && a <= 96 + 26) || (a >= 65 && a <= 64 + 26))
		return 1;
	else
		return 0;
}
bool isn(char a)    
{
	if (a == 45)
		return 0;
	else
		return 1;
}
void change_s(char* s)
{

	s_len = strlen(s);
	for (int i = 0; i < s_len; i++)
	{
		sq[i].flag = 0;
		sq[i].sch = s[i];
	}
}

bool np(string s)
{
	for (int i = 0; i < s.length(); i++)
	{
		if (s[i] == 45)
			return 0;
	}
	return 1;
}

gapnit* change_p(string pattern)
{
	gapp_len = 0;
	gapnit* pt = gapp;
	memset(gapp, 0, sizeof(gapnit));
	char p[M];
	strcpy(p, pattern.c_str());
	int gap[100];
	int len = strlen(p);
	int i;
	int t = 0;
	int p_len = 0;
	if (isalpha(p[0]) && isalpha(p[len - 1]))
	{

		chp[p_len].ch = p[0];
		chp[p_len].flag = 1;
		for (i = 1; i < len; i++)
		{
			if (isalpha(p[i]))
			{
				p_len = p_len + 1;
				chp[p_len].ch = p[i];
				chp[p_len].flag = 1;
				if (!isn(p[i - 1]))
				{
					chp[p_len].flag = 0;
				}
			}
			if (p[i] >= 48 && p[i] <= 57)
			{
				gap[t] = p[i] - 48;
				t = t + 1;
			}
		}
	}
	else printf("irregular pattern");
	int k = 2;
	gapp[gapp_len].start = chp[0];
	gapp[gapp_len].nchar.flag = 1;
	gapp[gapp_len].min = gap[0];
	gapp[gapp_len].max = gap[1];
	gapp_len = gapp_len + 1;
	for (i = 1; i <= p_len; i++)
	{
		if (chp[i].flag == 1)
		{
			gapp[gapp_len].start = chp[i];
			gapp[gapp_len].nchar.flag = 1;
			if (i == p_len)
			{
				gapp[gapp_len].min = gapp[i].max = 0;
			}
			else
			{
				gapp[gapp_len].min = gap[k];
				gapp[gapp_len].max = gap[k + 1];
				k = k + 2;
			}
			gapp_len = gapp_len + 1;
		}
		else
		{
			gapp[gapp_len - 1].nchar = chp[i];
		}
	}
	return pt;

}
void min_freItem()
	int* sups = new int[setlen]; 
	for (int i = 0; i < setlen; i++)
	{
		sups[i] = 0;
	}
	for (int t = 0; t < NumbS; t++)	
	{
		strcpy(S, sDB[t].s);
		for (int i = 0; i < strlen(S); i++)
		{
			for (int j = 0; j < setlen; j++)
			{
				if (S[i] == charset[j])
				{
					sups[j]++;
				}
			}
		}
	}
	for (int i = 0; i < setlen; i++)
	{
			string mine;
			mine.append(1, charset[i]);
			freArr[0].push_back(mine);
			cout << charset[i] << "=" << sups[i] << endl;
	}
	delete[] sups;
	sups = NULL;
}

int matchp(gapnit* p, char* s);
int matchsup(string cand)
{
	gapnit* pt = change_p(cand);
	int occnum = 0;
	for (int t = 0; t < NumbS; t++)
	{
		if (strlen(sDB[t].s) > 0)
		{
			strcpy(S, sDB[t].s);
			occnum += matchp(pt, S);
		}
		if (occnum >= threshold)
		{
			break;
		}
	}
	return occnum;
}
int frennum = 0; int pfrenum = 0; int pf = 0;

int matchp(gapnit* p, char* s);


void gen_candidate(int level)
{

	int size = freArr[level].size();
	for (int k = 0; k < size; k++)
	{
		string Q = freArr[level][k];  
		for (int i = 0; i < freArr[0].size(); i++)
		{
			string cand = Q;
			cand = cand + '[' + char(48 + mins) + ',' + char(48 + maxs) + ']' + freArr[0][i];
			pfrenum++;
			int candsup = matchsup(cand);
			if (candsup >= threshold)
			{
				if (np(cand) == 0)
				{
					frennum++;
					freArr[level + 1].push_back(cand);
				}
				else
				{
					pf++;
					freArr[level + 1].push_back(cand);
				}
				
            }
			for (int j = 0; j < setlen; j++)
			{
				string candl = Q;
				candl = candl + '[' + char(48 + mins) + ',' + char(48 + maxs) + ']' + '-' + charset[j] + freArr[0][i];
				pfrenum++;
				candsup = matchsup(candl);
				if (candsup >= threshold)
				{
					frennum++;
					freArr[level + 1].push_back(candl);
				}
			}
		}
	}
}

int matchp(gapnit* p, char* s)
{
	change_s(s);
	int* start;
	start = new int[gapp_len];
	int occ_len = 0;
	for (int i = 0; i < gapp_len; i++)
	{
		start[i] = 0;
	}
	for (int l = 0; l < s_len; l++)
	{
		for (int m = 0; m < gapp_len; m++)
		{
			bool gflag = true;
			int j;
			bool sflag = false;
			for (j = l; j < s_len; j++)
			{
				if (gapp[m].start.ch == sq[j].sch && sq[j].flag == 0)
				{
					sflag = true;
					if (m == 0) 
					{
						start[m] = j;
						break;
					}
					if (j - start[m - 1] - 1 > gapp[m - 1].max && m != 0)
					{
						gflag = false;
						break;
					}
					if (j - start[m - 1] - 1 < gapp[m - 1].min)
					{
						sflag = false;
						continue;
					}
					if (gapp[m - 1].nchar.flag == 0)
					{
						bool flag = true;
						if (j - start[m - 1] - 1 == 0)
						{
							sflag = false;
							continue;
						}
						for (int k = start[m - 1] + 1; k < j; k++)
						{

							if (sq[k].sch == gapp[m - 1].nchar.ch)
							{
								flag = false;
								break;
							}
						}
						if (flag == true)
						{
							break;
						}
						else
						{
							gflag = false;
							break;
						}
					}
					else
					{
						start[m] = j;
						break;
					}
				}
			}
			if (sflag == false)
			{
				break;
			}
			if (gflag == false)
			{
				m = m - 2;
				l = start[m + 1] + 1;
			}
			else
			{
				start[m] = j;
				l = start[m] + 1;
			}
		}
		bool occflag = true;
		int k;
		for (k = 0; k < gapp_len; k++)
		{
			if (start[k] == 0)
			{
				if (k == 0 && occ_len == 0)
				{
					sq[start[k]].flag = 1;
				}
				else
				{
					occflag = false;
					break;
				}

			}
			else
			{
				sq[start[k]].flag = 1;
			}
		}
		if (occflag == false)
		{
			for (k - 1; k >= 0; k--)
			{
				sq[start[k]].flag = 0;
			}
			break;
		}
		else
		{
			occ_len = occ_len + 1;
			l = start[0];
			for (int i = 0; i < gapp_len; i++)
			{
				start[i] = 0;
			}
		}
	}
	delete[] start;
	start = NULL;
	return occ_len;
}
void main() {
	stlen = read_file();
	cout << "aaaa" << stlen;
	int n = 13, frenum = 0;
	cout << "input the mingap,maxgap:" << endl;
	cin >> mins >> maxs;
	cout << "input the threshold:" << endl;
	cin >> threshold;
	DWORD begintime = GetTickCount();

	min_freItem();	
	int f_level = 0;
	string p;
	while (freArr[f_level].size() != 0)
	{
		cout << "  freArr[f_level].size() " << freArr[f_level].size() <<endl;
		gen_candidate(f_level);
		f_level++;
	}
	DWORD endtime = GetTickCount();
	cout << "正频繁数" << pf << endl;
	cout << "负序列候选数" << pfrenum << endl;
	printf("频繁模式数：%d\n", frennum);
	cout << "耗时" << endtime - begintime << "ms. \n";
	system("pause");
	return;
}