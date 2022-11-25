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
#define K 6000    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 200000  //The length of sequence
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
double hupval;
double uphupval=0;
int upminsup=0;
string item[30];   // event set

vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> *canArr = new vector <string>[M];//  store can patterns
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number
void readfile()
{ 
	fstream file;
	string buff;
	char filename[256]="C:/Users/Administrator/Desktop/LRCD/KTCD/DataSet/baby1.txt";
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
		{   canArr[0].push_back(the_iterator->first);
		      frenun++;

			if (the_iterator->second*hupval >= minunity)
			
			{
				
				freArr[0].push_back(the_iterator->first); 
		        //frenun++;
		        
			}
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
		R = canArr[level-1][i].substr(1,level-1);  //suffix pattern of freArr[level-1][i] ��1��λ�ú���level-1���ַ�����R
		Q = canArr[level-1][start].substr(0,level-1);   //prefix pattern of freArr[level-1][start]
		if(Q != R)
		{
			start = binary_search(level, R, 0, size-1);	//ͨ�����ֲ��ң�������freArr[level-1]��R���ֵ��׸�λ��
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
				candidate.push_back(cand);	//�Զ���cand��������candidateĩβ
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
	}

}
/*
int no_que(int len_s,int len_p){
	occnum=0;
	int k;
	for(int i=0;i<len_s;i++)
	{  
		if(S[i]==link_pan[0].name)
		{
			k=i;
			break;
		}
	   
	}
	for (;k<len_s;k++)
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
	
 return occnum;
}

*/
void clear_vector_que(queue<int>& q)
{
	queue<int> empty;
	swap(empty, q);

}

int no_que(int len_s, int len_p) {
	occnum = 0;
	int k=0;
	
	for (int i = 0; i<len_s; i++)
	{
		if (S[i] == link_pan[0].name)
		{
			k = i;
			break;
		}

	}
	
	for (; k<len_s; k++)
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
void  main()
{  
	readfile();
	cout<<"input the minunity:";
	cin>>minunity;
	mymap['a']=1.5;
	mymap['b']=2;
	mymap['c']=2;
	mymap['d']=3;
	mymap['e']=5;
	mymap['f']=4;

	upminsup=ceil(minunity/5);
	DWORD begintime=GetTickCount();	
	min_freItem();   //cout frequent items and store item[]
    int f_level=1;   
	gen_candidate(f_level);	//�����˳���Ϊ2�ĺ�ѡģʽ	
    while(candidate.size()!=0 )
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
		
			
			for(int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				Creat_ptn(p,ptn_len);
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					if(ptn_len> strlen(S))
					{
					num=0;
					}else{
					// p="AGCA";
					 s_length=strlen(S);									
			     	 num += no_que(s_length, ptn_len) ;
					 //no_que(s_length, ptn_len) ;
					
					}
				}				
			link_pan.clear();	
			}
			
			occnum=num;
			//cout<<"����Ϊ��"<<compnum<<endl;
			if(occnum>=upminsup){
                   canArr[f_level].push_back(p);
				   
				   hupval=occnum*hupval/p.size();
				   if(hupval >= minunity)
					{
						freArr[f_level].push_back(p);
						cout<<p<<""<<hupval<<"";
			            fout<<p<<""<<hupval<<"";
                       
					//	canArr[f_level].push_back(p);
						//frenun++;
						 
						//break;
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
			fout<<freArr[i][j]<<"   ";
			frenum++;
		}
		//cout<<frenum;
		cout<<endl;
        fout<<endl;
	}
  
	//cout<<endl;
	//cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	fout<<"The time-consuming:"<<endtime-begintime<<"ms. \n"<<endl;
	//cout <<"����Ϊ:"<<frenun;
    cout <<"����Ϊ:"<<frenum;
	cout<<"��ѡ����Ϊ��"<<compnum<<endl;

	//cout <<"The number of calculation:"<<frenum;
	fout<< "����Ϊ:"<<frenum<<endl;
    fout<< "��ѡ����Ϊ��"<<compnum<<endl;
	//system("pause");	
	system("pause");

}
