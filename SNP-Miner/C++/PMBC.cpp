#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include<queue>
#include<time.h>
#include<math.h>
using namespace std;
#define K 1000    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 20000  //The length of sequence
char S[N];  //sequence
int NumbS;
int s_length;
//ofstream fout("2.txt", ios::binary);
struct pant_p         //nettree node
{
	char name;     //The corresponding position of node in sequence
	queue<int> que_pan;
};
vector <pant_p> link_pan;
map<char,double> mymap;
struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];
struct sequence
{
	char c;
	bool used;

};
struct occurrence   //occurrence
{
	vector <int > position;
};
//char S[N];      //sequence
map <string, int> frequent;  //frequent pattern and its support
double minunity;
int ptn_len;  
int nn = 0;   //The number of types of events
//int NumbS=0;
int store = 0;
int	num_occur=0;
int occnum = 0; 
int frenun=0;
double hupval;
double uphupval=0;
string p;
int upminsup=5000;
string item[30];   // event set
//sub_tn_struct sub_ptn[M];  //a[0,3]c[0,3]t
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> *canArr = new vector <string>[M];//  store can patterns
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number
void readfile()
{
//	fstream file;
	FILE *fp=NULL;
	char p[20];
	string buff;
	fp=fopen("SDB1.txt","r+");
	int i=0;
	while (fscanf(fp,"%s",sDB[i].S )!= EOF)
	{
		//strcpy(sDB[i].S, buff.c_str());
		i++;
	}
	NumbS=i;
	// print sequence database
	//cout << "sDB and min_sup are as follows : " << endl;
	for(int t = 0; t < NumbS; t++)
	{
		sDB[t].id = t + 1;
	//	cout << "\t(" << sDB[t].id << ",(" << sDB[t].S << "))" << endl;
	}
	cout<<"sequence number:"<<NumbS<<endl;
}
void min_freItem()
{
	map <string, int > counter; 
	string mine;
	//upminsup=ceil(minunity/1);
	for(int t = 0; t < NumbS; t++)  //count item and its support num
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
    
	nn = 0;
	
	for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	 {
		compnum++;
		 if (the_iterator->second <upminsup)
		 {
			map <string, int >::iterator tmp = the_iterator;
			++tmp;
			counter.erase (the_iterator);
			the_iterator = tmp;
		 } 
		 else
		 {
			 canArr[0].push_back(the_iterator->first);  //add to freArr[0]
			 ++the_iterator;
		 }
	}
}
//find the first position of cand in the level of freArr by binary search
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
		    //find start
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
void gen_candidate(int level)
{
	int size = canArr[level-1].size();
	int start = 0;
	for(int i=0;i<size;i++)
	{
		string Q="",R="";
		R = canArr[level-1][i].substr(1,level-1);  //suffix pattern of freArr[level-1][i] 第1个位置后面level-1个字符赋给R
		Q = canArr[level-1][start].substr(0,level-1);   //prefix pattern of freArr[level-1][start]
		if(Q != R)
		{
			start = binary_search(level, R, 0, size-1);	//通过二分查找，查找在freArr[level-1]中R出现的首个位置
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
				candidate.push_back(cand);	//自动将cand插入向量candidate末尾
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
void InitSequence(char s[],sequence seq[] ){
	int l=strlen(s);
	int i=0;
	while(i<l)
	{
		seq[i].c=s[i];
		seq[i].used=false;
		i++;
	}
}
int matching(sequence seq[],int occ[]){
	int num=0;
	int n=strlen(S);
	int m=p.size();
	int i=0;
	for(int j=0;j<m;j++)
	{
		int flag=-1;		
		while(i<n)
		{		
			if(seq[i].c==p[j]&&seq[i].used==false)
			{
				flag=1;
				occ[j]=i;
				seq[i].used=true;
				break;
			}
		
			i++;
		}//while
	
		if(j==m-1&&i<n)
		{
			i=occ[0];		
			j=-1;			
		    num++;
		}

		if(flag==1)
		{
			i++;
		}
		
		if(i>=n)
		{
			break;
		}
	}
   return num;
}

int  main(int argc, const char *argv[])
{
	//readfile(argv[1]);
	readfile();
	//upminsup= atoi(argv[2]);

	
	DWORD begintime=GetTickCount();
	
	min_freItem();   //cout frequent items and store item[]
    int f_level=1;
    
	gen_candidate(f_level);	
	
    while(candidate.size()!=0)
	{
		int num = 0;

		for(int i=0;i<candidate.size();i++)
		{
			
			occnum = 0; //the support num of pattern
			//int rest = 0;
			
			//string p = candidate[i];
			p = candidate[i];
			ptn_len=p.size();
			
			compnum++;
			//Creat_ptn(p,ptn_len);
			sequence  seq[N];
			for(int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					s_length=strlen(S);
					 if(ptn_len> s_length)
					{
						num=0;
					}else{
					InitSequence(S,seq);
					int occ[100];
					num=matching(seq,occ);
					// p="AGCA";
					 //s_length=strlen(S);									
			     	 //num += no_que(s_length, ptn_len) ;
					 //no_que(s_length, ptn_len) ;
					 //link_pan.clear();

				}				
				}	
			
			occnum+=num;  
			if(occnum>=upminsup){
                   canArr[f_level].push_back(p);
					break;
			}	
			}
		}
		f_level++;
		candidate.clear();
		gen_candidate(f_level);
	}
	DWORD endtime=GetTickCount();
    cout <<endl;
	
	for(int i = 0; i<f_level; i++)
	{
		for(int j = 0; j<canArr[i].size();j++)
		{
			cout<<canArr[i][j]<<"   ";
			//fout<<canArr[i][j]<<"   ";
			frenum++;
		}
		cout<<endl;
       // fout<<endl;
	}
	//cout<<endl;
	//cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	cout <<"frquent number:"<<frenum<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	cout <<"candidate number:"<<compnum<<endl;
	//fout<<"The time-consuming:"<<endtime-begintime<<"ms. \n"<<endl;
	time_t t = time(0); 
	char tmp[32]={NULL};
	strftime(tmp, sizeof(tmp), "%Y-%m-%d %H:%M:%S",localtime(&t)); 
/*	ofstream mcfile; 

	mcfile.open("result_file.txt",ios::app); 
	string s;
	s.assign(argv[1]);
	s=s.substr(50);
	mcfile<<tmp<<"\t"<<s<<"\t"<<minunity<<"\t"<<endtime-begintime<<"\t\t\t"<<frenum<<"\t\t\t"<<compnum<<"\n";
	mcfile.close(); 
	
	ofstream maxfrefile;
	maxfrefile.open("result_fature.txt",ios::app);
	maxfrefile<<tmp<<"\t"<<s<<"\t"<<minunity<<"\t"<<endtime-begintime<<"\t\t\t"<<frenum<<"\t\t\t"<<compnum<<"\n";	
	for(int m = 0; m<f_level; m++)
	{   int kk=0;
		for(int j = 0; j<canArr[m].size();j++)
		{
			maxfrefile<<canArr[m][j]<<"\t";
			kk++;
           	
		}
		maxfrefile<<kk<<"\t";
	}
	maxfrefile<<"\n";
	maxfrefile.close();*/
    //fout<< "The number of calculation:"<<frenum<<endl;
	return 0;
	//system("pause");	
	//fout.close();

}
