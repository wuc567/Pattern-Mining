#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <time.h>
using namespace std;
#define K 600    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 20000  //The length of sequence
/*struct node         //nettree node
{
	int name;     //The corresponding position of node in sequence
	//int min_leave,max_leave;   //The position of maxinum and mininum leave nodes
	int min_root,max_root;
	vector <int> parent;     //The position set of parents
	vector <int> children;  //The position set of children
	bool used;      //true is has used, false is has not used
	bool toroot;
	//bool toleave;  //true is can reach leaves, false is not
	int minroot_leave;
	int maxroot_leave;
};*/
struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];                 // sequence database

struct occurrence   //occurrence
{
	vector <int > position;
};
struct sub_ptn_struct   //a[0,3]c => start[min,max]end
{
	char start,end;		
	int min,max;
}; 
char S[N];      //sequence
map <string, int> frequent;  //frequent pattern and its support
double minsup;
int minlen,maxlen;   //length constraint
int mingap,maxgap;   //gap constraint
int ptn_len;  
int nn = 0;   //The number of types of events
int NumbS=0;
int store = 0;
string item[30];   // event set
sub_ptn_struct sub_ptn[M];  //a[0,3]c[0,3]t
int compnum = 0;  //compute number
int occurnum=0;
map<char,double> mymap;
double hupval=0;
double uphupval=0;
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

void min_freItem()
{
	map <string, int > counter; 
	string mine;
	 mymap['a']=3;
	 mymap['g']=6;
	 mymap['c']=6;
	 mymap['t']=4;
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
		if (the_iterator->second*hupval < minsup)
		{
			uphupval=the_iterator->second*6;
			if(uphupval>=minsup)
			{
				cout <<uphupval<<endl;
				//canArr[0].push_back(the_iterator->first);
				item[nn++] = the_iterator->first.at(0);
			}
			map <string,int >::iterator tmp = the_iterator;
			++tmp;
			counter.erase (the_iterator);
			the_iterator = tmp;
		} 
		else
		 {
			 item[nn++] = the_iterator->first.at(0);
			 frequent[pp] = the_iterator->second; 
			 ++the_iterator;
		 }
	}
}



int create_subnettree(vector <int> *nettree,int parent,int L,int pop)
{
	int j=0;
	if(L>ptn_len+1)
	{
		return 1;
	}
	int flag=0;
	for(j=parent+sub_ptn[L-2].min+1;j<=parent+sub_ptn[L-2].max+1;j++)//间隙约束下查找
	{	
		if(S[j]==sub_ptn[L-2].end)
		{
			int k=nettree[L-1].size();
			flag=-1;
			/*if(k!=0)
			{
				if(nettree[L-1][k-1].name==j)
				{
					flag=k-1;
				}
			}*/
			if(k!=0)
			{
				if(nettree[L-1][k-1]>=j)
				{
					flag=k-1;
				}
			}
			//node anode;	
			if(flag==-1)
			{
				int len=nettree[L-1].size ();
			//	nettree[L-1].push_back(anode);
				nettree[L-1].push_back(j);
			
				int local=nettree[L-1].size();
				int ident=0;
				ident=create_subnettree(nettree,j,L+1,local-1);
				/*anode.name =j;
				anode.parent.clear ();
		    	anode.children .clear ();
				anode.min_root=nettree[L-2][pop].min_root;
				anode.max_root=nettree[L-2][pop].max_root;
				anode.used =false;

				int len=nettree[L-1].size ();

				anode.toroot =true;
				nettree[L-1].push_back(anode);

				nettree[L-2][pop].children.push_back(len);

				nettree[L-1].back().parent.push_back(pop);
			
				int local=nettree[L-1].size();
				int ident=0;
				ident=create_subnettree(nettree,j,L+1,local-1);//j代表网树中的位置，
				*/
				if(ident==1)
				{
					return 1;
				}
			}
			
		}///创建当前节点
	}
	return 0;

}

void create_nettree(vector <int> *nettree)
{	
	occurnum=0;
	for (int i=0;i<ptn_len+1;i++)
		nettree[i].clear();//网树层初始化
	int *start;
	start=new int[ptn_len+1];
	for (i=0;i<ptn_len+1;i++)
		start[i]=0;
	
	for (i=0;i<strlen(S)-ptn_len;i++)
	{
		if(S[i]!=sub_ptn[0].start)
		{
			continue;
		}
		int len=nettree[0].size ();

		//nettree[0].push_back(anode);
		nettree[0].push_back(i);
		int ident=create_subnettree(nettree,i,2,len);
		/*node anode;
		anode.name =i;
	    anode.parent.clear ();
		anode.children .clear ();
		anode.used =false;  
	///
		int len=nettree[0].size ();
	///
		anode.toroot =true;
		anode.min_root=anode.max_root=anode.name;
		nettree[0].push_back(anode);
		int ident=create_subnettree(nettree,i,2,len);*/
		if(ident==1)
		{
			occurnum++;
		}
	}
	delete []start;
	
}


void mineFre(string p,int num)
{
	//frequent[p] = num;  //add to frequent array
	for(int e = 0; e < nn; e++)
	{
		string q = p + item[e];
		compnum++;
		//num = 0;
		hupval = 0;
		int occnum = 0; //the support num of pattern
		double rest=0;
		for(int s=0;s<q.size();s++)
		{
			hupval += mymap.find(q[s])->second;
		}
		for(int t = 0; t < NumbS; t++)
		{
			//rest=minsup-occnum;
			if(strlen(sDB[t].S) > 0)
			{
				strcpy(S,sDB[t].S);
				deal_range(q);
				num=0;
				if(ptn_len+1 > strlen(S))
				{
					num=0;
				}else{
					vector <int> *nettree;
					nettree=new vector <int> [ptn_len+1];
					create_nettree(nettree);
					num=occurnum;//num表示数据集中一条序列中模式的支持度；occurnum是全局变量
					delete []nettree;
				}
				occnum += num;//occnum是在main函数中定义的，表示这个模式在数据集中的支持度
			}
			/*hupval=occnum*hupval/q.size();
			if(hupval >= minsup)
			{
				//cout<<hupval<<"  ";
				frequent[q] = occnum; 
				mineFre(q,occnum);
				break;
			}
			else
			{
				uphupval=occnum * 0.3;
				//cout<<uphupval<<"  ";
				if(uphupval>=minsup)
				{	
					mineFre(q,occnum);
				}
			}*/
			/*rest=minsup-num;
			if(strlen(sDB[t].S) > 0)
			{
				strcpy(S,sDB[t].S);
				num += netGap(q,rest);
			}
			if (num>=minsup)
				break;*/
		}
		hupval=occnum*hupval/q.size();
			if(hupval >= minsup)
			{
				//cout<<hupval<<"  ";
				frequent[q] = occnum; 
				mineFre(q,occnum);
				//break;
			}
			else
			{
				uphupval=occnum * 6;
				//cout<<uphupval<<"  ";
				if(uphupval>=minsup)
				{	
					mineFre(q,occnum);
				}
			}
		/*if (num>=minsup)
			mineFre(q,num);	*/

	}
}
void readfile(const char * namefile)
{
	fstream file;
	string buff;
	file.open(namefile,ios::in);   //open sequence file
	/*fstream file;
	string buff;
	char filename[256]="Dataset/DNA3.TXT";
	cout <<"---------------------------------------------------------------------------\nPlease input file name:";
	//cin>>filename;
	cout <<filename<<endl;
	file.open(filename,ios::in);   //open sequence file
	//file.open("Dataset/DNA6.txt",ios::in);   //open sequence file*/
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
int main(int argc, const char *argv[])
{
	readfile(argv[1]);
	mingap=atoi(argv[2]);
	maxgap=atoi(argv[3]);
	minsup= atoi(argv[4]);
/*void main()
{
	readfile();
	cout<<"input the minlen,maxlen:"<<endl;
	//cin>>minlen>>maxlen;
	minlen=1;	maxlen=100;
	
	cout <<minlen <<"\t"<<maxlen<<endl;
	cout<<"input the mingap,maxgap:"<<endl;
	//cin>>mingap>>maxgap;
	mingap=0;	maxgap=3;

	cout <<mingap <<"\t"<<maxgap<<endl;
	cout<<"input the minsup:"<<endl;
	//cin>>minsup;
	minsup=150;

	cout <<minsup<<endl;*/
	/*std::map<char,double> mymap;
	std::map<char,double>::iterator it;
	mymap['a']=0.2;
	mymap['g']=0.3;
	mymap['c']=0.3;
	mymap['t']=0.2;*/
	DWORD begintime=GetTickCount();
	min_freItem();   //cout frequent items and store item[]
	for(int e = 0; e < nn; e++)    // each item
	{
		string p = item[e];
		int num = 0;
		mineFre(p,num);    // mining all frequent patterns
	}
	DWORD endtime=GetTickCount();
	cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
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
	s=s.substr(59);
	mcfile<<tmp<<"\t"<<s<<"\t"<<minsup<<"\t"<<"\t["<<mingap<<","<<maxgap<<"]\t"<<endtime-begintime<<"\t\t\t"<<frequent.size()<<"\n";
	mcfile.close(); 


	/*ofstream maxfrefile;
	maxfrefile.open("result_fature.txt",ios::app);
	maxfrefile<<tmp<<"\t"<<s<<"\t"<<minsup<<"\t"<<"\t["<<mingap<<","<<maxgap<<"]\t"<<endtime-begintime<<"\t\t\t"<<frequent.size()<<"\n";

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
