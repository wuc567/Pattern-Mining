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
#include<time.h>
using namespace std;

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
#define K 6000   //The sequence number of sequence database
#define M 1000   //The length of pattern
#define N 20000  //The length of sequence
char S[N];  //sequence
int jz=0;
int h=0;
//int minlen,maxlen;   //length constraint
int mingap,maxgap; //gap constraint
int store1;
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
int minsup;  
int NumbS;
///////////////////////////


vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> *canArr = new vector <string>[M]; 
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number
int occurnum=0;

double hupval=0;
double uphupval=0;

void deal_range(string pattern)      
//put sub-pattern "a[1,3]b" into sub_ptn and sub_ptn.start=a��sub_ptn.end=b, sub_ptn.min=1��sub_ptn.max=3
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


/*void gen_candidate(int level)//ʹ��canArr�����ģʽ������ɺ�ѡģʽ����ƴ��
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
				//cout <<cand<<"  ";
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
	//cout<<endl;
}*/
void gen_candidate(int level)
//Generate candidate set according to the level layer of frequent tree
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
void min_freItem()//���ɳ���Ϊ1��Ƶ��ģʽ
{
	 map <string, int > counter;
	 string mine;
	 std::map<char,double> mymap;
	 std::map<char,double>::iterator it;
	 mymap['a']=3;
	 mymap['g']=6;
	 mymap['c']=6;
	 mymap['t']=4;
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
		 string pp=the_iterator->first;
		 hupval=mymap.find(pp[0])->second;
		 //cout<<hupval;
		 if (the_iterator->second*hupval < minsup)
		 {
			uphupval=the_iterator->second*6;
			//cout<<the_iterator->first<<":"<<uphupval<<endl ;
			if(uphupval>=minsup)
			{
				//cout <<uphupval<<endl;
				canArr[0].push_back(the_iterator->first);
			}
			map <string, int >::iterator tmp = the_iterator;
			++tmp;
			counter.erase (the_iterator);
			the_iterator = tmp;
			
		 } 
		 else
		 {
			 freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			 canArr[0].push_back(the_iterator->first);
			 //cout<<the_iterator->first<<"  ";
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
	for(j=parent+sub_ptn[L-2].min+1;j<=parent+sub_ptn[L-2].max+1;j++)//��϶Լ���²���
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
				ident=create_subnettree(nettree,j,L+1,local-1);//j���������е�λ�ã�
				*/
				if(ident==1)
				{
					return 1;
				}
			}
			
		}///������ǰ�ڵ�
	}
	return 0;

}

void create_nettree(vector <int> *nettree)
{	
	occurnum=0;
	for (int i=0;i<ptn_len+1;i++)
		nettree[i].clear();//�������ʼ��
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

void read_file(const char * namefile)
{
	fstream file;
	string buff;
	file.open(namefile,ios::in);   //open sequence file
	/*fstream file;
	char filename[256];
	cout <<"---------------------------------------------------------------------------\nPlease input file name:";
	//cin>>filename;
	//cout <<filename<<endl;
	string buff;
	//file.open(filename,ios::in);   //open sequence file
	file.open("DataSet/DNA3.txt",ios::in);   //open sequence file*/
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

//void main()
int main(int argc, const char *argv[])
{
	read_file(argv[1]);
	mingap=atoi(argv[2]);
	maxgap=atoi(argv[3]);
	minsup= atoi(argv[4]);
	/*read_file();
	//cout<<"input the minlen,maxlen:"<<endl;
	//cin>>minlen>>maxlen;
	//minlen=1,maxlen=20;
	cout<<"input the mingap,maxgap:"<<endl;
	//cin>>mingap>>maxgap;
	mingap=0,maxgap=3;
	cout<<"input the minsup:"<<endl;
	cin>>minsup;
	//minsup=800;*/
	std::map<char,double> mymap;
	std::map<char,double>::iterator it;
	mymap['a']=3;
	mymap['g']=6;
	mymap['c']=6;
	mymap['t']=4;
	int cannum=0;
	DWORD begintime=GetTickCount();
	min_freItem();
	int f_level=1;
	gen_candidate(f_level);	
	while(candidate.size()!=0)
	{
		int num = 0;

		for(int i=0;i<candidate.size();i++)
		{
			cannum++;
			int occnum = 0; //the support num of pattern
			int rest = 0;
			hupval=0;
			string p = candidate[i];
			for(int s=0;s<p.size();s++)
			{
				hupval += mymap.find(p[s])->second;
			}
			compnum++;
			for(int t = 0; t < NumbS; t++)
			{
				rest=minsup-occnum;
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					deal_range(p);
					int num=0;
					if(ptn_len+1 > strlen(S))
					{
						num=0;
					}else{
						vector <int> *nettree;
						nettree=new vector <int> [ptn_len+1];
						create_nettree(nettree);
						num=occurnum;//num��ʾ���ݼ���һ��������ģʽ��֧�ֶȣ�occurnum��ȫ�ֱ���
						delete []nettree;
					}
					occnum += num;//occnum����main�����ж���ģ���ʾ���ģʽ�����ݼ��е�֧�ֶ�
				}
				/*hupval=occnum*hupval/p.size();
				if(hupval >= minsup)
				{
					//cout<<hupval<<"  ";
					freArr[f_level].push_back(p);
					canArr[f_level].push_back(p);
					break;
				}
				else
				{
					uphupval=occnum * 0.3;
					//cout<<uphupval<<"  ";
					if(uphupval>=minsup)
					{
						canArr[f_level].push_back(p);
					}
				}*/
			}
			hupval=occnum*hupval/p.size();
				if(hupval >= minsup)
				{
					//cout<<hupval<<"  ";
					freArr[f_level].push_back(p);
					canArr[f_level].push_back(p);
					//break;
				}
				else
				{
					uphupval=occnum * 6;
					//cout<<uphupval<<"  ";
					if(uphupval>=minsup)
					{
						canArr[f_level].push_back(p);
					}
				}
		}
		//cout <<endl;
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
	
	time_t t = time(0); 
	char tmp[32]={NULL};
	strftime(tmp, sizeof(tmp), "%Y-%m-%d %H:%M:%S",localtime(&t)); 
	ofstream mcfile; 

	mcfile.open("result_file.txt",ios::app); 

	string s;
	s.assign(argv[1]);
	s=s.substr(59);
	mcfile<<tmp<<"\t"<<s<<"\t"<<minsup<<"\t"<<"\t["<<mingap<<","<<maxgap<<"]\t"<<endtime-begintime<<"\t\t\t"<<frenum<<"\t\t\t"<<cannum<<"\n";
	mcfile.close(); 


	ofstream maxfrefile;
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
	maxfrefile.close();
	
	return 0;
	
}
