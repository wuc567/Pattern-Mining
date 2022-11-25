#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <stack>
using namespace std;

#define K 6000   //The sequence number of sequence database
#define M 1000   //The length of pattern
#define N 20000  //The length of sequence
char S[N];  //sequence
int ptn_len=0;  
int seq_len=0;

int mingap,maxgap; //gap constraint

struct sub_ptn_struct   //a[0,3]c => start[min,max]end
{
	char start,end;		
	int min,max;
};

sub_ptn_struct sub_ptn[M];  //pattern p[i]

struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];                 // sequence database
int minsup; 
int nn=0; 
int NumbS;
///////////////////////////
string item[30];
map <string, int> frequent;  //frequent pattern and its support

int compnum = 0, frenum = 0;  //compute number and frequents number
int occurnum=0;
/////


/*

char mw[15]="BbCcoaO";
char sm[19]="DdEeFfBbCc";
char m[20]="BbCc";


char mw[24]="hilkmftwvrcqgpsynadeuox";
char sm[24]="hilkmftwvrcqgpsynadeuox";
char m[24]="hilkmftwvrcqgpsynadeuox";

char mw[20]="rcqgpsynadeuox";
char sm[20]="hilkmftwvrcqgpsyn";
char m[10]="rcqgpsyn";
char s[10]="hilkmftwv";

char mw[20]="AaBbCcDdEeFfGg";
char sm[20]="EeFfGgHhIiJj";
char m[10]="EeFfGg";
char s[10]="HhIiJj";
*/

char mw[24]="hilkmftwvrcqgpsynadeuox";
char sm[24]="hilkmftwvrcqgpsynadeuox";
char m[24]="hilkmftwvrcqgpsynadeuox";
char s[10]="";

/////
void deal_range(string pattern)      
//put sub-pattern "a[1,3]b" into sub_ptn and sub_ptn.start=a，sub_ptn.end=b, sub_ptn.min=1，sub_ptn.max=3
{
	ptn_len=0;
	memset(sub_ptn, 0, sizeof(sub_ptn_struct));
	char p[M];
	strcpy(p,pattern.c_str()); 
	if (strlen(p)==1)
	{
		sub_ptn[ptn_len].start = p[0];
		sub_ptn[ptn_len].max =sub_ptn[ptn_len].min=0;
	}
	for(int i=0;i<strlen(p)-1;i++ )
	{
		sub_ptn[ptn_len].start =p[i];
		sub_ptn[ptn_len].end =p[i+1];
		sub_ptn[ptn_len].min=mingap;	
		sub_ptn[ptn_len].max=maxgap;
		ptn_len++;
	}
}



bool belong(char c,char p[])
{
	
	for(int i=0;i<strlen(p);i++)
	{
		if(c==p[i])
		{
			return true;
		}
	}
	return false;

}




void min_freItem()
{
	map <string, int > counter; 
	string mine;
	for(int t = 0; t < NumbS; t++)  //count item and its support num
	{
		strcpy(S,sDB[t].S);
		for(int i=0;i<strlen(S);i++)
		{
			if ((S[i]>='a'&&S[i]<='z')||(S[i]>='A'&&S[i]<='Z'))
			{
				if(belong(S[i],sm))
				{
					mine=S[i];
					counter[mine]++;
				}
			
			}	
		}
	}
	nn = 0;
	for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	{
		if (the_iterator->second < minsup)
		{
			map <string,int >::iterator tmp = the_iterator;
			++tmp;
			counter.erase (the_iterator);
			the_iterator = tmp;
		} 
		else
		 {
			 item[nn++] = the_iterator->first.at(0);
			 ++the_iterator;
		 }
	}
}
int create_subnettree(vector <int> *nettree,int parent,int L)
{
	int j=0;
	if(L>ptn_len+1)
	{
		return 1;
	}
	int flag=0;
	for(j=parent+1;j<=parent+sub_ptn[L-2].min;j++)
	{
		if(belong(S[j],s))
		{
			return 0;
		}
	}
	

	for(j=parent+sub_ptn[L-2].min+1;j<=parent+sub_ptn[L-2].max+1;j++)
	{	
		if(S[j]==sub_ptn[L-2].end)
		{
			int k=nettree[L-1].size();
			flag=-1;
			for(int i=0;i<k;i++)
			{
				if(nettree[L-1][i]==j)
				{
					flag=i;
					break;
				}
			}

			if(flag==-1)
			{
				nettree[L-1].push_back(j);
				
				if(create_subnettree(nettree,j,L+1))
				{
					return 1;
					//break;
				}
		
			}
		}///创建当前节点

		if(!belong(S[j],mw))
		{
			break;
		}
	}
	return 0;

}

void create_nettree(vector <int> *nettree)
{	
	occurnum=0;
	for (int i=0;i<ptn_len+1;i++)
		nettree[i].clear();//网树层初始化
	
	for (i=0;i<seq_len-ptn_len;i++)
	{
		if(S[i]!=sub_ptn[0].start)
		{
			continue;
		}
		nettree[0].push_back(i);
		occurnum+=create_subnettree(nettree,i,2);
		
	}
	
}




int CalNtp(string p)
{
	deal_range(p);
	int num=0;
	if(ptn_len+1 > seq_len)
	{
		num=0;
	}else{
		vector <int> *nettree;
		nettree=new vector <int> [ptn_len+1];
		
		create_nettree(nettree);
		num=occurnum;
		delete []nettree;
	}
	return num;
}


void mineFre(string p,int num)
{
	frequent[p] = num;  //add to frequent array
	for(int e = 0; e < nn; e++)
	{
		string q = p + item[e];
		compnum++;
		num = 0;
		for(int t = 0; t < NumbS; t++)
		{
			if(strlen(sDB[t].S) > 0)
			{
				strcpy(S,sDB[t].S);
				seq_len=strlen(S);
				num += CalNtp(q);
			}
			if (num>=minsup)
				break;
		}
		if (num>=minsup)
			mineFre(q,num);	

	}
}

void read_file()
{
	fstream file;
	char filename[256];
	cout <<"---------------------------------------------------------------------------\nPlease input file name:";
	string buff;
	file.open("F:/NTP-Miner/NTP-DataSet/SDB1.txt",ios::in);   //open sequence file
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
		//cout << "\t(" << sDB[t].id << ",(" << sDB[t].S << "))" << endl;
	}
}


void main()
{
	read_file();
	cout<<"input the mingap,maxgap:"<<endl;
	cin>>mingap>>maxgap;
	cout<<"input the minsup:"<<endl;
	cin>>minsup;
	DWORD begintime=GetTickCount();
	min_freItem();   //cout frequent items and store item[]
	for(int e = 0; e < nn; e++)    // each item
	{
		string p = item[e];
		int num = 0;
		int rest=0;
		for(int t = 0; t < NumbS; t++)
		{
			rest=minsup-num;

			if(strlen(sDB[t].S) > 0)
			{
				strcpy(S,sDB[t].S);
				num += CalNtp(p);
			}
			if(num >= minsup)
			{
				break;
			}
		}
			mineFre(p,num);    // mining all frequent patterns
	}
	DWORD endtime=GetTickCount();
	cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	for(map<string,int> ::iterator f_iterator = frequent.begin (); f_iterator!= frequent.end ();f_iterator++)
	{
		cout<< f_iterator->first<<":";
		cout<< f_iterator->second<<"\t";
	}
	cout<<endl;
	cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	cout <<"The number of calculation:"<<compnum<<" \n";
	
}
