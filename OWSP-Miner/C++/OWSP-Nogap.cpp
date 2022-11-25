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
typedef char Elemtype;
#define K 600    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 20000  //The length of sequence
char S[N];  //sequence
int NumbS;
int s_length;
ofstream fout("2.txt", ios::binary);
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
//double hupval;
//double uphupval=0;
int upminsup=50;
string item[30];   // event set
//sub_tn_struct sub_ptn[M];  //a[0,3]c[0,3]t
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> *canArr = new vector <string>[M];//  store can patterns
vector <string> candidate; 
char gapstr[100];
int compnum = 0, frenum = 0;  //compute number and frequents number

//计算每个长度模式的时间
DWORD time1;
DWORD time2;
int hxms[1000];//候选模式
int pfms[1000];//频繁模式

void readfile()
{
	fstream file;
	string buff;
	char filename[256]="SDB1.txt";
	cout <<"---------------------------------------------------------------------------\nPlease input file name:";
	//cin>>filename;
	cout <<filename<<endl;
	file.open(filename,ios::in);   //open sequence file
	//file.open("Dataset/DNA6.txt",ios::in);   //open sequence file
	int i=0;
	while(getline(file, buff))
	{
		strcpy(sDB[i].S, buff.c_str());
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
}

bool gapContain(char p_gapstr[], char c){
	while(*p_gapstr != '\0'){
		//printf("哈哈%c", *p_gapstr);
		if(*p_gapstr == c){
			//printf("666");
			return true;
		}
		p_gapstr++;

	}
	return false;
}

void min_freItem()
{
	map <string, int > counter; 
	string mine;	
	//upminsup=ceil(minunity/3);
	for(int t = 0; t < NumbS; t++)  //count item and its support num
	{
		strcpy(S,sDB[t].S);
		for(int i=0;i<strlen(S);i++)
		{
			if (((S[i]>='a'&&S[i]<='z')||(S[i]>='A'&&S[i]<='Z')) && !gapContain(gapstr, S[i]))
			{
				mine=S[i];
				counter[mine]++;
				
			}
			
		}
		
	}
    
	nn = 0;
	
	for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	{
		//cout<<the_iterator->first<<the_iterator->second <<endl;
	
		 string pp=the_iterator->first;
		
	//	 hupval=mymap.find(pp[0])->second;
		 hxms[0]++;
		 compnum++;
	 		
	    if(the_iterator->second>=upminsup)
		{   canArr[0].push_back(the_iterator->first);

		//	if (the_iterator->second*hupval >= minunity)
			
		//	{
				
				freArr[0].push_back(the_iterator->first); 
		        frenum++;
				pfms[0]++;

		        
		//	}
		} 
		
			 ++the_iterator;
	
	
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
void GenPreFix( Elemtype *Pattern, int *PreFix )
{
	int LOLP = 0;			//length of largest prefix
	int NOCM;				//number of character matched
	int Patlen = strlen(Pattern);
    
	PreFix[0] = -1; 
	PreFix[1] = 0;

	for( NOCM=2; NOCM<Patlen+1; NOCM++ ) {
		while( LOLP>0 && Pattern[LOLP] != Pattern[NOCM-1] ) //cursor -1
			LOLP = PreFix[LOLP];
		if( Pattern[LOLP] == Pattern[NOCM-1] )// -1 
			LOLP++;
		PreFix[NOCM] = LOLP;
	}
	PreFix[Patlen] = 0;
}
int KmpStrMatching( Elemtype *Target, Elemtype *Pattern, int *prefix )
{
	int Patlen = strlen( Pattern );
	//cout<<Patlen<<endl;
	//printf("Patlen%d",Patlen);
	int Targetlen = strlen( Target );
	//cout<<Targetlen<<endl;
	//printf("Patlen==---%d",Targetlen);
	int Tarlen = 0;				//记录已查找的目标串长度
	int NextLength = 0;
	int flag = 0;				//标记是否匹配成功过
	int num_occur=0;
	while( '\0' != *Target  ) {
		
		for( int i=0; i<Patlen; i++ ) 
			if( *(Target+i) != *(Pattern+i) )
				break;
		if( i == Patlen ) {
			//printf("i = %d",i);
		    //cout<<"i="<<i<<endl;
            //cout<<"位置"<<Tarlen+1<<"处匹配成功!"<<endl;
			//printf("位置%d处匹配成功!\n", Tarlen+1);
			//show_occ(Tarlen+1);
			num_occur++;
			//change_bool(Tarlen);
			//show_bool();
			
			flag = 1;
		}
		NextLength = i - prefix[i];  // i--已经匹配成功的字符数， i=0 --- prefix[0]=-1 表示没匹配到任何字符，向后移一位
		//printf("NextLength = %d \n",NextLength);
		Target = Target + NextLength;
		Tarlen += NextLength;

	}

	
	//printf("匹配到个数为：%d\n",n);

    return num_occur;
	
}

void main()
{
	readfile();
//	cout<<"input the minunity:";
//	cin>>minunity;
	printf("\n\nPlease input the gapstr:\n");
	scanf("%s",gapstr);
	//minunity=20;
	//cout <<minunity<<endl;
   int prefix[N];
//	mymap['a']=1;
//	mymap['g']=1;
//	mymap['c']=1;
//	mymap['t']=1;
//	upminsup=ceil(minunity/1);
	DWORD begintime = GetTickCount();
	
	time1 = begintime;
	min_freItem();   //cout frequent items and store item[]
	time2 = GetTickCount();
	printf("len_1_Time cost:%ld\t候选数：%d\t频繁数：%d\n",time2-time1, hxms[0], pfms[0]);
    int f_level=1;
    
	gen_candidate(f_level);	//生成了长度为2的候选模式
	
    while(candidate.size()!=0)
	{
		int num = 0;

		for(int i=0;i<candidate.size();i++)
		{
			num=0;
			occnum = 0; //the support num of pattern
			//int rest = 0;
			
			string p = candidate[i];
			hxms[f_level]++;
		
			ptn_len=p.size();
		//	hupval=0;
		//	for(int s=0;s<ptn_len;s++)
		//	{
		//		hupval += mymap.find(p[s])->second;
		//	}
			compnum++;
			char*pp=(char*)p.data();
			GenPreFix( pp, prefix );  
			for(int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					// p="AGCA";
					 s_length=strlen(S);									
			     	 num += KmpStrMatching(S, pp, prefix );
					 //no_que(s_length, ptn_len) ;
					 link_pan.clear();
				}				
				
			}
			occnum=num;
			if(occnum>=upminsup){
                   canArr[f_level].push_back(p);
				//   hupval=occnum*hupval/p.size();
				 //  if(hupval >= minunity)
				//	{
						freArr[f_level].push_back(p);
                        frenum++;
						pfms[f_level]++;
					//	canArr[f_level].push_back(p);
						//frenun++;
						//cout <<p<<' ' ;
						//occnum = 0; 
						//break;
				//	}
					
				}
		}
		time1 = time2;
		time2 = GetTickCount();
		//printf("len_%d_Time cost:%ld\n", f_level+1, time2-time1);
		printf("len_%d_Time cost:%ld\t候选数：%d\t频繁数：%d\n", f_level+1, time2-time1, hxms[f_level], pfms[f_level]);
		f_level++;
		candidate.clear();
		gen_candidate(f_level);
	}
	//DWORD endtime = GetTickCount();
	DWORD endtime = time2;
    cout <<endl;
	
	for(int i = 0; i<f_level; i++)
	{
		for(int j = 0; j<freArr[i].size();j++)
		{
			cout<<freArr[i][j]<<"   ";
			fout<<freArr[i][j]<<"   ";
			//frenum++;
		}
		cout<<endl;
        fout<<endl;
	}

	//cout<<endl;
	//cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	fout<<"The time-consuming:"<<endtime-begintime<<"ms. \n"<<endl;
	cout <<"候选总数为:"<<compnum;
	cout <<"频繁总数为:"<<frenum;
   
	//cout <<"The number of calculation:"<<frenum;
    //fout<< "The number of calculation:"<<frenum<<endl;
	system("pause");	
	fout.close();

}
