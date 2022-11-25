#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
using namespace std;
#define K 1000    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 20000  //The length of sequence
#define MAXLENP 100
#define BUFFER 1000
struct node         //nettree node
{
	int name;     //The corresponding position of node in sequence
	int min_leave,max_leave;   //The position of maxinum and mininum leave nodes
	vector <int> parent;     //The position set of parents
	vector <int> children;  //The position set of children
	bool used;      //true is has used, false is has not used
	bool toleave;  //true is can reach leaves, false is not
};
struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];                 // sequence database

char S[N];  //sequence
int minsup;  
int NumbS;
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number

int binary_search(int level,string cand,int low,int high)
{
	int mid,start;
	if (low > high)
	{
		return -1;
	}
	while (low<=high)
	{
		mid=(high+low)/2;
		int result=cand.compare(freArr[level-1][mid].substr(0,level-1)); 
		if (result == 0)
		{
		    //find start
			int slow=low;
			int shigh=mid;
			int flag=-1;
			if (cand.compare(freArr[level-1][low].substr(0,level-1)) == 0)
			{
				start=low;
			}
			else
			{
				while (slow<shigh)
				{
					
					start=(slow+shigh)/2;
					int sresult=cand.compare(freArr[level-1][start].substr(0,level-1)); 
					if (sresult==0)   //Only two cases of ==0 and >0
					{
						shigh=start;
						flag=0;
					}
					else
					{
						slow=start+1;
					}				
				}
				start=slow;
			}
			return start;
		}
		else if (result<0)
		{
			high = mid-1;
		}
		else
		{
			low = mid+1;
		}
	}
	return -1;
}


void gen_candidate(int level)
{
	int size = freArr[level-1].size();
	int start = 0;
	for(int i=0;i<size;i++)
	{
		string Q="",R="";
		R = freArr[level-1][i].substr(1,level-1);  //suffix pattern of freArr[level-1][i]
		Q = freArr[level-1][start].substr(0,level-1);   //prefix pattern of freArr[level-1][start]
		if(Q != R)
		{
			start = binary_search(level, R, 0, size-1);
		}
		if (start<0 || start>=size)     //if not exist, begin from the first
			start=0;
		else
		{
			Q=freArr[level-1][start].substr(0,level-1);
			while(Q == R)
			{
				string cand = freArr[level-1][i].substr(0,level);
				cand = cand + freArr[level-1][start].substr(level-1,1);
				candidate.push_back(cand);
				start=start+1;
				if (start >= size) 
				{
					start=0;
					break;
				}
				Q=freArr[level-1][start].substr(0,level-1);
			}
		}
	}
}

void min_freItem()
{
	 map <string, int > counter;
	 string mine;
	 for(int t = 0; t < NumbS; t++)
	 {
		strcpy(S,sDB[t].S);
		for(int i=0;i<strlen(S);i++)
		{
			if ((S[i]>='a'&&S[i]<='z')||(S[i]>='A'&&S[i]<='Z'))
			{
				mine=S[i];
				counter[mine]++;
			}			
		}	 
	 }
	 for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	 {
		 compnum++;
		 if (the_iterator->second < minsup)
		 {
			map <string, int >::iterator tmp = the_iterator;
			++tmp;
			counter.erase (the_iterator);
			the_iterator = tmp;
		 } 
		 else
		 {
			 freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			 ++the_iterator;
		 }
	}
}

int matching(char *s, string p_pattern) 
{
	char p[MAXLENP];
	strcpy(p, p_pattern.c_str());
	int lens = strlen(s);
	int lenp = strlen(p);
	int nettree[BUFFER][MAXLENP] = {0};
	int level_len[MAXLENP] = {0};
	int i, j;
	int count = 0;
	if (strlen(p) == 1)
	{
		for (int i = 0; i < strlen(s); i++)
		{
			if (s[i] == p[0])
			{
				count++;
			}
		}
		return count;
	}
	for (i = 0; i < lens; i++)
	{
		int hasbeenadded = 0;
		if (p[0] == s[i])
		{
			hasbeenadded = 1;
			int position = level_len[0];
			position = position % BUFFER;
			if (level_len[0] - level_len[lenp - 1] > BUFFER - 1) 
			{
				cout << "Overflow!!!\nThe buffer is too small.\n";
				return -1;
			}
			nettree[position][0] = i;
			level_len[0]++;
		}
		for (j = 1; j < lenp; j++)
		{
			if (p[j] == s[i])
			{
				int flag = 0;
				if (p[j] == p[j - 1] && hasbeenadded)
				{				
					flag = 1;
				}
				if (level_len[j - 1] - flag > level_len[j])
				{
					hasbeenadded = 1;
					int position = level_len[j];
					position = position % BUFFER;
					nettree[position][j] = i;
					level_len[j]++;
					if (j == lenp - 1) 
					{
						count++;
						int pos = level_len[j] - 1;
						pos = pos % BUFFER;
					}
				}
				else 
					hasbeenadded = 0;
			}
		}
	}

	return count;
}

void read_file()
{
	fstream file;
	char filename[256];
	string buff;
	file.open("SDB7.txt",ios::in);   //open sequence file
	
	int i=0;
	while(getline(file, buff))
	{
		strcpy(sDB[i].S, buff.c_str());
		i++;
	}
	NumbS=i;
	for(int t = 0; t < NumbS; t++)
	{
		sDB[t].id = t + 1;
	}
	cout<<"sequence number = "<<NumbS<<endl;
	
}


void main()
{
	read_file();
	minsup=5000;
	DWORD begintime=GetTickCount();
	min_freItem();
	int f_level=1;
	gen_candidate(f_level);	
	while(candidate.size()!=0)
	{
		int num = 0;

		for(int i=0;i<candidate.size();i++)
		{
			int occnum = 0; 			
			string p = candidate[i];
			compnum++;
			for(int t = 0; t < NumbS; t++)
			{
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					occnum += matching(S,p);
				}
				if(occnum >= minsup)
				{
					freArr[f_level].push_back(p);
					break;
				}
			}
		}
		f_level++;
		candidate.clear();
		gen_candidate(f_level);
	}
	DWORD endtime=GetTickCount();
	for(int i = 0; i<f_level; i++)
	{
		for(int j = 0; j<freArr[i].size();j++)
		{
			cout<<freArr[i][j]<<"   ";
			frenum++;
		}
		cout<<endl;
	}
	cout<<"The number of frequent patterns:"<<frenum<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	cout <<"The number of calculation:"<<compnum<<" \n";
}