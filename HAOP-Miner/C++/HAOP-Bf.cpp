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
	file.open(namefile,ios::in);   //open sequence file
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
void min_freItem()
{
	map <string, int > counter; 
	string mine;	
	//upminsup=ceil(minunity/7);
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
		//cout<<the_iterator->first<<the_iterator->second <<endl;
	
		 string pp=the_iterator->first;
		
		 hupval=mymap.find(pp[0])->second;
	 
		
	    if(the_iterator->second>=upminsup)
		//if (the_iterator->second*hupval < minunity)
		{   //uphupval=the_iterator->second*10;
			//cout<<the_iterator->first<<":"<<uphupval<<endl ;
			if (the_iterator->second*hupval >= minunity)
			//if(the_iterator->second>=upminsup)
			//if(uphupval>=minunity)
			{
				//cout <<uphupval<<endl;
				freArr[0].push_back(the_iterator->first); 
		        frenun++;
		        canArr[0].push_back(the_iterator->first);
			}else
			{canArr[0].push_back(the_iterator->first);}
			//map <string,int >::iterator tmp = the_iterator;
			//++tmp;
			//counter.erase (the_iterator);
			//the_iterator = tmp;
		} 
		//else
		//{   //freArr[0].push_back(the_iterator->first); 
		    //frenun++;
		    //canArr[0].push_back(the_iterator->first);
			//frenun++;
			//cout<<the_iterator->first<<' ';
			//item[nn++] = the_iterator->first.at(0);
			 ++the_iterator;
		
		// }
	
	}
}
//find the first position of cand in the level of freArr by binary search

void gen_candidate(int level)
{
	int size = canArr[level-1].size();
	for(int k=0;k<size;k++)
	{ 
		//fnode *pnode = &frequenttree[level][k];
		//string p = pnode->name;
		string cand;
		string Q=canArr[level-1][k];  //suffix pattern of freArr[level-1][i]
		for(int i=0;i<canArr[0].size();i++)
		{
			cand=Q;
			cand=cand.append(canArr[0][i]);
			candidate.push_back(cand);
		}
	}
}
void Creat_ptn(string p,int ptn_len){
	for(int i =0;i<ptn_len;i++){
		pant_p  pan;
		memset(&pan,0,sizeof(pan));
		pan.name=p[i];
		link_pan.push_back(pan);
	}

}
void clear_vector_que(queue<int>& q)
{
	queue<int> empty;
	swap(empty, q);

}

int no_que(int len_s, int len_p) {
	occnum = 0;
	int k;
	/*
	for (int i = 0; i<len_s; i++)
	{
		if (S[i] == link_pan[0].name)
		{
			k = i;
			break;
		}

	}
	*/
	for (k=0; k<len_s; k++)
	{   
		int postion = 0;
		for (int m = ptn_len - 1; m>0; m--)//
		{
			//cout << S[k] <<k<< link_pan[m].name<< m<< link_pan[m].que_pan.size() << link_pan[m - 1].que_pan.size() << endl;
			if (S[k] == link_pan[m].name  && link_pan[m].que_pan.size()<link_pan[m - 1].que_pan.size())
			{
				link_pan[m].que_pan.push(k);
				postion = m;
				break;
			}

		}
		if (postion == 0 && S[k] == link_pan[0].name) {
			link_pan[0].que_pan.push(k);
		}
		if (postion == ptn_len - 1) {
			
			occnum++;
		}
	}
//	link_pan.clear();
	/**/
	for ( k = 0; k < link_pan.size();k++)
	{
		clear_vector_que(link_pan[k].que_pan);
	}
	//cout << occnum << endl;
	return occnum;
}


int main(int argc, const char *argv[])
{
	readfile(argv[1]);
	minunity= atoi(argv[2]);

	mymap['a']=2;
	mymap['g']=3;
	mymap['c']=2;
	mymap['t']=3;
	upminsup=ceil(minunity/3);
	DWORD begintime=GetTickCount();
	
	min_freItem();   //cout frequent items and store item[]
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
			compnum++;
			ptn_len=p.size();
			hupval=0;
			for(int s=0;s<ptn_len;s++)
			{
				hupval += mymap.find(p[s])->second;
			}
			
			Creat_ptn(p,ptn_len);
			for(int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				if(strlen(sDB[t].S) > 0)
				{   
					strcpy(S,sDB[t].S);
					// p="AGCA";
					 s_length=strlen(S);
					 if(ptn_len> s_length)
					{
						num=0;
					}else{
			     	 num += no_que(s_length, ptn_len) ;
					 //no_que(s_length, ptn_len) ;
					 
				}				
				}	
			}
			link_pan.clear();
			occnum=num;
			if(occnum>=upminsup){
				   hupval=occnum*hupval/p.size();
				   if(hupval >= minunity)
					{
						freArr[f_level].push_back(p);
						canArr[f_level].push_back(p);
						//frenun++;
						//cout <<p<<' ' ;
						//occnum = 0; 
						//break;
					}
					else{
				
						//uphupval=occnum * 10;
						//cout<<uphupval<<"  ";
				   		//if(occnum>=upminsup)
						//if(uphupval>=minunity)
					
						canArr[f_level].push_back(p);
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
		for(int j = 0; j<freArr[i].size();j++)
		{
			cout<<freArr[i][j]<<"   ";
			//fout<<freArr[i][j]<<"   ";
			frenum++;
		}
		cout<<endl;
        //fout<<endl;
	}
	//cout<<endl;
	//cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	//fout<<"The time-consuming:"<<endtime-begintime<<"ms. \n"<<endl;
    cout <<"总数为:"<<frenum;
	cout <<"总数为:"<<compnum;
	//cout <<"The number of calculation:"<<frenum;
    //fout<< "The number of calculation:"<<frenum<<endl;
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
	{
		for(int j = 0; j<freArr[m].size();j++)
		{
			maxfrefile<<freArr[m][j]<<"\t";
		}
	}
	maxfrefile<<"\n";
	maxfrefile.close();
	//system("pause");	
	//fout.close();
	return 0;

}
