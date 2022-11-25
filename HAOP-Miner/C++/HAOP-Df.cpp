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
int minsup;
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
int nn ;   //The number of types of events
//int NumbS=0;
int store = 0;
int	num_occur=0;
int occnum = 0; 
int frenun=0;
double hupval;
double uphupval=0;
int upminsup=0;
int occurnum;
string item[30];   // event set
//sub_tn_struct sub_ptn[M];  //a[0,3]c[0,3]t
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> *canArr = new vector <string>[M];//  store can patterns
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number
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
				mine=S[i];
				counter[mine]++;
			}	
		}
	}
	nn = 0;
	for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	{
		string pp=the_iterator->first;
		hupval=mymap.find(pp[0])->second;

		if(the_iterator->second>=minsup){
			item[nn++] = the_iterator->first.at(0);
			if (the_iterator->second*hupval >= minunity)
			
			{
				
				frequent[pp] = the_iterator->second; 
		        //frenun++;
		        
			}
		} 
		
			 ++the_iterator;

	
		
	    /*
		if (the_iterator->second*hupval < minsup)
		{
			uphupval=the_iterator->second*3;
			if(uphupval>=minsup)
			{
				cout <<uphupval<<endl;
				//canArr[0].push_back(the_iterator->first);
				item[nn++] = the_iterator->first.at(0);
			}
		
		} 
		else
		 {
			
			 item[nn++] = the_iterator->first.at(0);
			 frequent[pp] = the_iterator->second; 
			 ++the_iterator;
		 }
		 */
		
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
	int k=0;	
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
	for (k = 0; k < link_pan.size();k++)
	{
		clear_vector_que(link_pan[k].que_pan);
	}
	//cout << occnum << endl;
	return occnum;
}


void mineFre(string p,int num)
{
	//frequent[p] = num;  //add to frequent array
	for(int e = 0; e < nn; e++)
	{
		string q = p + item[e];
		//cout<<q<<endl;
		ptn_len=q.size();
		compnum++;
		//num = 0;
		hupval = 0;
		//int occnum = 0; //the support num of pattern
		double rest=0;
		for(int l=0;l<q.size();l++)
		{
			hupval += mymap.find(q[l])->second;
		}
		Creat_ptn(q,ptn_len);
		num=0;
		occnum=0;
		for(int t = 0; t < NumbS; t++)
		{
			
			//rest=minsup-occnum;
			if(strlen(sDB[t].S) > 0)
			{
				strcpy(S,sDB[t].S);			
				if(ptn_len > strlen(S))
				{
					num=0;
				}else{
					//num += no_que(s_length, ptn_len) ;
					s_length=strlen(S);
					
					//num+=no_que(s_length, ptn_len) ;//num表示数据集中一条序列中模式的支持度；occurnum是全局变量
				   no_que(s_length, ptn_len) ;
				  
				}
				//occnum += num;//occnum是在main函数中定义的，表示这个模式在数据集中的支持度
			}
		}
		 link_pan.clear();
		 //occnum = num;
		if(occnum>=minsup){
					
			hupval=occnum*hupval/q.size();
			if(hupval>=minunity){
				frequent[q] = occnum; 
				//mineFre(q,occnum);						
			}
            mineFre(q,occnum);
		}
		
	}
}
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
int  main(int argc, const char *argv[])
{
	readfile(argv[1]);
	minunity= atoi(argv[2]);
	mymap['a']=2;
	mymap['g']=3;
	mymap['c']=2;
	mymap['t']=3;
	minsup=ceil(minunity/3);
	//cout <<minsup<<endl;
	DWORD begintime=GetTickCount();
	min_freItem();   //cout frequent items and store item[]
	for(int e = 0; e < nn; e++)    // each item
	{
		string p = item[e];
		int num = 0;
		mineFre(p,num);    // mining all frequent patterns
	}
	DWORD endtime=GetTickCount();
	//cout<<"**************************"<<endl;
	//cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	for(map<string,int> ::iterator f_iterator = frequent.begin (); f_iterator!= frequent.end ();f_iterator++)
	{
		cout<< f_iterator->first<<"\t";
	}
	cout<<endl;
	cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	cout <<"The number of calculation:"<<compnum<<" \n";
	time_t t = time(0); 
	char tmp[32]={NULL};
	strftime(tmp, sizeof(tmp), "%Y-%m-%d %H:%M:%S",localtime(&t)); 
	ofstream mcfile; 

	mcfile.open("result_file.txt",ios::app); 
	string s;
	s.assign(argv[1]);
	s=s.substr(50);
	mcfile<<tmp<<"\t"<<s<<"\t"<<minunity<<"\t"<<endtime-begintime<<"\t\t\t"<<frequent.size()<<"\n";
	mcfile.close(); 
	//system("pause");	
	//fout.close();
 return 0;
}
