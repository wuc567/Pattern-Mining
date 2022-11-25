#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <stack>
#include<cmath>
#include <time.h>
using namespace std;

#define K 60000   //The sequence number of sequence database
#define M 10000   //The length of pattern
#define N 200000  //The length of sequence
char S[N];  //sequence
int jz=0;
int h=0;
//int minlen,maxlen;   //length constraint
int mingap,maxgap; //gap constraint
int store1;
map<char,double> mymap;
struct sub_ptn_struct   //a[0,3]c => start[min,max]end
{
	char start,end;		
	int min,max;
};
struct occurrence   //occurrence
{
	vector <int > position;
};
vector <occurrence> store;
sub_ptn_struct sub_ptn[M];  //pattern p[i]
int ptn_len=0;  
int seq_len=0;



struct storenode
{
	int position;
	int level;
};
//////////////////////////
struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];                 // sequence database
double minsup;
double blsup;  
int NumbS;
///////////////////////////


vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> *canArr = new vector <string>[M]; 
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number
//int occurnum=0;

double hupval=0;
double uphupval=0;
int *match;

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

//find the first position of cand in the level of canArr by binary search
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
		int result=cand.compare(canArr[level-1][mid].substr(0,level-1)); //To avoid multiple calls the same function
		if (result == 0)
		{
			int slow=low;
			int shigh=mid;
			int flag=-1;
			if (cand.compare(canArr[level-1][low].substr(0,level-1)) == 0)
			{
				start=low;
			}
			else
			{
				while (slow<shigh)
				{
					
					start=(slow+shigh)/2;
					int sresult=cand.compare(canArr[level-1][start].substr(0,level-1)); 
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


void gen_candidate(int level)//使用canArr数组的模式逐层生成候选模式——拼接
{
	int size = canArr[level-1].size();
	int start = 0;
	for(int i=0;i<size;i++)
	{
		string Q="",R="";
		R = canArr[level-1][i].substr(1,level-1);  //suffix pattern of freArr[level-1][i]
		Q = canArr[level-1][start].substr(0,level-1);   //prefix pattern of freArr[level-1][start]
		if(Q != R)
		{
			start = binary_search(level, R, 0, size-1);
		}
		if (start<0 || start>=size)     //if not exist, begin from the first
			start=0;
		else
		{
			Q=canArr[level-1][start].substr(0,level-1);
			while(Q == R)
			{
				string cand = canArr[level-1][i].substr(0,level);
				cand = cand + canArr[level-1][start].substr(level-1,1);
				candidate.push_back(cand);
				start=start+1;
				if (start >= size) 
				{
					start=0;
					break;
				}
				Q=canArr[level-1][start].substr(0,level-1);
			}
		}
	}
}

void min_freItem()//生成长度为1的频繁模式
{
	 map <string, int > counter;
	 string mine;
	 /**/mymap['a']=3;
	 mymap['g']=6;
	 mymap['c']=6;
	 mymap['t']=4;
	 /*mymap['a']=0.2;
	 mymap['c']=0.9;
	 mymap['d']=0.4;
	 mymap['e']=0.5;
	 mymap['f']=0.5;
	 mymap['g']=0.3;
	 mymap['h']=0.8;
	 mymap['i']=0.5;
	 mymap['k']=0.5;
	 mymap['l']=0.2;
	 mymap['m']=0.8;
	 mymap['n']=0.6;
	 mymap['p']=0.6;
	 mymap['q']=0.7;
	 mymap['r']=0.6;
	 mymap['s']=0.5;
	 mymap['t']=0.5;
	 mymap['v']=0.4;
	 mymap['w']=0.8;
	 mymap['y']=0.6;*/
	 /*mymap['s']=0.2;
	 mymap['p']=0.4;
	 mymap['r']=0.3;
	 mymap['o']=0.3;
	 mymap['u']=0.5;
	 mymap['m']=0.3;
	 mymap['h']=0.3;
	 mymap['i']=0.4;
	 mymap['a']=0.1;
	 mymap['f']=0.4;
	 mymap['d']=0.3;
	 mymap['t']=0.4;
	 mymap['c']=0.5;
	 mymap['e']=0.5;*/
	 
	 for(int t = 0; t < NumbS; t++)
	 {
		strcpy(S,sDB[t].S);
		for(int i=0;i<strlen(S);i++)
		{
			mine=S[i];
			counter[mine]++;		
		}	 
	 }
	 for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	 {
		 if (the_iterator->second >= blsup)
		 {
			canArr[0].push_back(the_iterator->first);
			string pp=the_iterator->first;
			hupval=mymap.find(pp[0])->second;
			if (the_iterator->second*hupval >= minsup)
			{
				freArr[0].push_back(the_iterator->first);
			}
		 }
		 ++the_iterator;
	}
}
/***************/

double matches(char *s,int end)
{
	struct row
	{
		int *r;
	};
	row *table;
	int start;
	//start=end-max;
	//if (start<0)
		start=0;
	int i,j,kn,kx,k;
	int len=end-start+1;
	table=new row[len];
	for (i=0;i<len;i++)
	{
		table[i].r =new int [ptn_len+1];
		for (j=0;j<=ptn_len;j++)
		{
			table[i].r [j] =0;
		}
	}
	
	for (i=start;i<end;i++ )
	{
		//????
		for (j=0;j<ptn_len;j++)
		{
			if (s[i]==sub_ptn[j].start  )
			{
				if (j==0)
				{
					table[i-start].r[j]=1;
				}
				else
				{
					kn=i-sub_ptn[j-1].max -1;
					kx=i-sub_ptn[j-1].min -1;
					if (kn<start)
						kn=start;
					if (kx>=start)
					{
						for (k=kn;k<=kx;k++)
						{
							table[i-start].r[j]+=table[k-start].r[j-1];
						}
					}
				}
			}
		}
	}
	kn=i-sub_ptn[ptn_len-1].max -1;
	kx=i-sub_ptn[ptn_len-1].min -1;
	if (kn<start)
		kn=start;
	double value=0;
	for (k=kn;k<=kx;k++)
	{
		value+=table[k-start].r[ptn_len-1];
	}
	for (i=0;i<len;i++)
	{
		delete []table[i].r;
	}
	delete []table;
	return value;
}
int  calculate(char *s)
{
	int len_s=strlen(s);
	int i;
	double count=0;
	for (i=-1;i<len_s;i++)
	{
		if (s[i]==sub_ptn[ptn_len-1].end )
		{
			count +=matches(s,i);
		}
	}
	//printf ("The number of all matches is : %lf\n\n" ,count );
	return count;
}
/***************/

void read_file(const char * namefile)
{
	fstream file;
	char filename[256];
	cout <<"---------------------------------------------------------------------------\n";
	string buff;
	file.open(namefile,ios::in);   //open sequence file
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

int main(int argc, const char *argv[])
{
	read_file(argv[1]);
	mingap=atoi(argv[2]);
	maxgap=atoi(argv[3]);
	minsup= atoi(argv[4]);
	DWORD begintime=GetTickCount();
	min_freItem();
	int f_level=1;
	gen_candidate(f_level);	
	int cannum=0;
	while(candidate.size()!=0)
	{
		//int num = 0;

		for(int i=0;i<candidate.size();i++)
		{
			cannum++;
			//cout<<cannum<<endl;
			double occnum = 0; //the support num of pattern
			//int rest = 0;
			hupval=0;
			string p = candidate[i];
			compnum++;
			for(int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					deal_range(p);
					//convert_p_to_ruler(p);
					//occnum=calculate(S);
					//calculate(m_sequence, m_max,m_min);
					occnum+=calculate(S);
					
				}
				
			}
			if(occnum>=blsup)
			{
				canArr[f_level].push_back(p);
				for(int s=0;s<p.size();s++)
				{
					hupval += mymap.find(p[s])->second;
				}
				hupval=occnum*hupval/p.size();
				if(hupval>=minsup)
				{
					freArr[f_level].push_back(p);
					//cout<<p<<"  "<<occnum<<"  "<<hupval<<endl;
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
	cout<<"***********************"<<endl;
	/*for(i = 0; i<f_level; i++)
	{
		for(int j = 0; j<canArr[i].size();j++)
		{
			cout<<canArr[i][j]<<"   ";
		}
		cout<<endl;
	}*/
	cout<<"The number of frequent patterns:"<<frenum<<endl;
	cout<<"The number of candidate patterns:"<<cannum<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	cout <<"The number of calculation:"<<compnum<<" \n";
	time_t t = time(0); 
	char tmp[32]={NULL};
	strftime(tmp, sizeof(tmp), "%Y-%m-%d %H:%M:%S",localtime(&t)); 
	ofstream mcfile; 

	mcfile.open("result_file.txt",ios::app); 

	string s;
	s.assign(argv[1]);
	s=s.substr(58);
	mcfile<<tmp<<"\t"<<s<<"\t"<<minsup<<"\t"<<"\t["<<mingap<<","<<maxgap<<"]\t"<<endtime-begintime<<"\t\t\t"<<frenum<<"\t\t\t"<<cannum<<"\n";
	mcfile.close(); 


	/*ofstream maxfrefile;
	maxfrefile.open("result_fature.txt",ios::app);
	maxfrefile<<tmp<<"\t"<<s<<"\t"<<minsup<<"\t"<<"\t["<<mingap<<","<<maxgap<<"]\t"<<endtime-begintime<<"\t\t\t"<<frenum<<"\n";

	for(int m = 0; m<f_level; m++)
	{
		for(int j = 0; j<freArr[m].size();j++)
		{
			maxfrefile<<freArr[m][j]<<"\t";
		}
	}
	maxfrefile<<"\n";
	maxfrefile.close();*/
	
	return 0;
}
