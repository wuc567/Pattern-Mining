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

bool np(string s)
{
	for (int i = 0; i < s.length(); i++)
	{
		if (s[i] == 45)
			return 0;
	}
	return 1;
}

bool nsp_to_pos(string s,int level)
{
	int flag = 0;
	string sp;
	sp= s[0];
	for (int i = 1; i < s.size(); i++)
	{
		if (isalpha(s[i]))
		{
			if (isn(s[i - 1]))
			{
				sp = sp + s[i];
			}
		}
	}
	for (int j = 0; j < posfre[level-1].size();j++)
	{
		if (sp == posfre[level-1][j])
		{
			flag = 1;
			break;
		}
	}
	if (flag == 1)
		return true;
	else
		return false;
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
	gapp[gapp_len].min = mins;
	gapp[gapp_len].max = maxs;
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
				gapp[gapp_len].min = mins;
				gapp[gapp_len].max = maxs;
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
{
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
		cout << charset[i] << "=" << sups[i] << endl;
		if (sups[i] >= threshold)
		{
			string mine;
			mine.append(1, charset[i]);
			freArr[0].push_back(mine);
		}
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
	}
	return occnum;
}
int frennum = 0; int pfrenum = 0; int pf = 0;
void inneg(string s)
{
	string cand = s;
	string lasts = s.substr(1);
	string pres = s.substr(0, 1);
	for (int j = 0; j < setlen; j++)
	{
		string cand2;
		cand2 = pres + '-' + charset[j];
		cand2 = cand2 + lasts;
		pfrenum++;
		int candsup = matchsup(cand2);
		if (candsup >= threshold)
		{
			frennum++;
			freArr[1].push_back(cand2);
			pfix frep;
			frep.frp = cand2;
			frep.prefix = cand2.substr(0, cand2.size() - 3);
			frep.suffix = cand2.substr(3);
			frep.len2 = 3;
			fix[0].push_back(frep);
		}

	}
}

int matchp(gapnit* p, char* s);
void gen_candtwo()
{
	int size = freArr[0].size();
	for (int i = 0; i < size; i++)
	{
		string* pcand;
		pcand = new string[size];
		string cand = freArr[0][i];
		for (int j = 0; j < size; j++)
		{
			string cand2 = cand + freArr[0][j];
			int candsup = matchsup(cand2);
			pfrenum++;
			if (candsup >= threshold)
			{
				pf++;
				pfix frep;
				frep.frp = cand2;
				frep.prefix = cand2.substr(0, cand2.size() - 1);
				frep.suffix = cand2.substr(1);
				frep.len2 = 1;
				fix[0].push_back(frep);
				posfre[0].push_back(cand2);
				inneg(cand2);
			}
		}

	}
}

int deal_len(string S)
{
	int length = S.length();
	int len;
	len = length - 3;
	return len;
}

void gen_candidate(int level)
{
	int size = fix[level - 1].size();
	
	for (int i = 0; i < size; i++)
	{
		int start = 0;
		while(start<size)
		{ 		
			string Q = "", R = "";
	    	Q = fix[level - 1][start].prefix;
		    R = fix[level - 1][i].suffix;
			if(Q == R)
			{
				int flag = 0;
				string cand = fix[level - 1][i].frp;
				int fixlen = fix[level - 1][start].frp.size();
				cand = cand + fix[level - 1][start].frp.substr(fixlen - fix[level - 1][start].len2);
				if (np(cand) == 0)
				{
					if (nsp_to_pos(cand,level) == true)
					{
						pfrenum++;
						flag = 1;
					}
					if (flag == 1)
					{
						int candsup = matchsup(cand);
						if (candsup >= threshold)
						{
							frennum++;
							freArr[level + 1].push_back(cand);
							pfix frep;
							frep.frp = cand;
							if (cand[1] == 45)
							{
								frep.suffix = cand.substr(3);
							}
							if (cand[1] != 45)
							{
								frep.suffix = cand.substr(1);
							}
							if (cand[cand.size() - 2] == 45)
							{
								frep.prefix = cand.substr(0, cand.size() - 3);
								frep.len2 = 3;
							}
							if (cand[cand.size() - 2] != 45)
							{
								frep.prefix = cand.substr(0, cand.size() - 1);
								frep.len2 = 1;
							}
							fix[level].push_back(frep);
						}
					}
				}
				else
				{
					pfrenum++;
					int candsup = matchsup(cand);
					if (candsup >= threshold) 
					{
						pf++;
						pfix frep;
						frep.frp = cand;
						frep.prefix = cand.substr(0, cand.size() - 1);
						frep.suffix = cand.substr(1);
						frep.len2 = 1;
						fix[level].push_back(frep);
						posfre[level - 1].push_back(cand);
					}
				}
			
			}
			start = start + 1;
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
	gen_candtwo();
	int f_level = 1;
	string p;
	while (fix[f_level-1].size() != 0)
	{
		gen_candidate(f_level);
		f_level++;
	}
	DWORD endtime = GetTickCount();
	cout << "候选数" << pfrenum << endl;
	cout << "正频繁数" << pf << endl;
	printf("频繁负模式数：%d\n", frennum);
	cout << "耗时" << endtime - begintime << "ms. \n";
	system("pause");
	return;
}