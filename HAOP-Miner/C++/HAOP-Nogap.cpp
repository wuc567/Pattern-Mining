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
#define K 600    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 40000 //The length of sequence
char S[N];  //sequence
int NumbS;   
int s_length;
map <char,vector <int> >p_occ;
map<char,double> mymap;
//ofstream fout("2.txt", ios::binary);
struct pant_p         //nettree node
{
	char name;     //The corresponding position of node in sequence
	queue<int> que_pan;
};
vector <pant_p> link_pan;
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
double hupval;
double uphupval=0;
int upminsup=0;
//double Tu;
string item[30];   // event set
//sub_tn_struct sub_ptn[M];  //a[0,3]c[0,3]t
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> *canArr = new vector <string>[M];//  store can patterns
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number
void readfile(const char * namefile)
{
	fstream file;
	string buff;
	//char filename[256]="1.txt";
//	cout <<"---------------------------------------------------------------------------\nPlease input file name:";
	//cin>>filename;
//	cout <<filename<<endl;
	file.open(namefile,ios::in);   //open sequence file
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
	//cout << "\t(" << sDB[t].id << ",(" << sDB[t].S << "))" << endl;
	}
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
void Creat_ptn(string p,int ptn_len){
	
	for(int i =0;i<ptn_len;i++){
		pant_p  pan;
		memset(&pan,0,sizeof(pan));
		pan.name=p[i];
		link_pan.push_back(pan);
		//p_occ[pan.name].push_back(i);
	}
	/*
		for (map <char, vector<int> >::iterator the_iterator = p_occ.begin(); the_iterator != p_occ.end(); )
	{
		cout<<the_iterator->first;
		for (int j = 0; j < the_iterator->second.size(); j++)
		{
			
			cout <<the_iterator->second[j]<<endl ;
		}
		the_iterator++;
	}
	*/
   
}
void no_que(int len_s,int len_p){

	for (int k=0;k<len_s;k++)
	{
		int postion = 0;
		for (int m=ptn_len-1;m>0;m--)//
		{
			if (S[k]==link_pan[m].name  && link_pan[m].que_pan.size()<link_pan[m-1].que_pan.size())
			{
				link_pan[m].que_pan.push(k);
				postion = m;
				break;
			}
			
		}
		if (postion==0&&S[k]==link_pan[0].name ){
			link_pan[0].que_pan.push(k);
		}
		if (postion==len_p-1){
			//for(int w=0;w<link_pan.size();w++){
			//	link_pan[w].que_pan.pop();}
					occnum++;
                  
		}
	}

}


int main(int argc, const char *argv[])
{
	//readfile();
	//cout<<"input the minunity:";
	//cin>>minunity;
	//minunity=2;
	//upminsup=2;
	//cout <<minunity<<endl;
    readfile(argv[1]);
	upminsup= atoi(argv[2]);
	/*
	mymap['a']=1;
	mymap['g']=1;
	mymap['c']=1;
	mymap['t']=1;
	upminsup=2;
	*/
	DWORD begintime=GetTickCount();
	
	min_freItem();   //cout frequent items and store item[]
    int f_level=1;
    
	gen_candidate(f_level);	//生成了长度为2的候选模式
	
    while(candidate.size()!=0)
	{
		int num = 0;

		for(int i=0;i<candidate.size();i++)
		{
			occnum = 0; //the support num of pattern
			//int rest = 0;
			
			string p = candidate[i];
			
			ptn_len=p.size();
			/*
			hupval=0;
			for(int s=0;s<ptn_len;s++)
			{
				hupval += mymap.find(p[s])->second;
			}
			*/
			compnum++;
			for(int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					// p="AGCA";
					 s_length=strlen(S);
				
					 Creat_ptn(p,ptn_len);
			     	 //occnum += no_que(s_length, ptn_len) ;
					 no_que(s_length, ptn_len) ;
					 link_pan.clear();
				}
				//hupval=occnum*hupval/p.size();
				if(occnum >= upminsup)
				{
					//freArr[f_level].push_back(p);
					canArr[f_level].push_back(p);
					//frenun++;
					//cout <<p<<' ' ;
					//occnum = 0; 
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
	/*
	cout<<"The number of frequent patterns:"<<frenun<<endl;
	for(map<string,int> ::iterator f_iterator = frequent.begin (); f_iterator!= frequent.end ();f_iterator++)
	{
		cout<< f_iterator->first<<":";
		cout<< f_iterator->second<<"\t";
	}
	*/
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
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	//fout<<"The time-consuming:"<<endtime-begintime<<"ms. \n"<<endl;
    cout <<"总数为:"<<frenum;
	time_t t = time(0); 
	char tmp[32]={NULL};
	strftime(tmp, sizeof(tmp), "%Y-%m-%d %H:%M:%S",localtime(&t)); 
	ofstream mcfile; 

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
	maxfrefile.close();
	//cout <<"The number of calculation:"<<frenum;
    //fout<< "The number of calculation:"<<frenum<<endl;
	return 0;
	//system("pause");	
	//fout.close();

}
