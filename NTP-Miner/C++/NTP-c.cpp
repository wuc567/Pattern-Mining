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

struct node         //nettree node
{
	int name;     //The corresponding position of node in sequence
	int min_leave,max_leave;   //The position of maxinum and mininum leave nodes
	vector <int> parent;     //The position set of parents
	vector <int> children;  //The position set of children
	bool used;      //true is has used, false is has not used
	bool toleave;  //true is can reach leaves, false is not
};
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
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number

/////


/*

char mw[15]="BbCcoaO";
char sm[19]="DdEeFfBbCc";
char m[20]="BbCc";
char mw[15]="rcqgpsynadeuox";
char sm[19]="hilkmftwvrcqgpsyn";
char m[20]="rcqgpsyn";

char mw[15]="AaBbCcDdEeFfGg";
char sm[19]="EeFfGgHhIiJj";
char m[20]="EeFfGg";

*/
char mw[25]="AaBbCcDdEeFfGgHhIiJj";
char sm[25]="AaBbCcDdEeFfGgHhIiJj";
char m[25]="AaBbCcDdEeFfGgHhIiJj";

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



int belong(char c,char p[])
{
	int flag=0;
	for(int i=0;i<strlen(p);i++)
	{
		if(c==p[i])
		{
			flag=1;
			break;
		}
	}
	return flag;

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
		int result=cand.compare(freArr[level-1][mid].substr(0,level-1)); //To avoid multiple calls the same function
		if (result == 0)
		{
		    //find start
			int slow=low;
			int shigh=mid;
			int flag=-1;
			if (cand.compare(freArr[level-1][low].substr(0,level-1)) == 0)
			{
				start=low;
			}
			else
			{
				while (slow<shigh)
				{
					
					start=(slow+shigh)/2;
					int sresult=cand.compare(freArr[level-1][start].substr(0,level-1)); 
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
	int size = freArr[level-1].size();
	int start = 0;
	for(int i=0;i<size;i++)
	{
		string Q="",R="";
		R = freArr[level-1][i].substr(1,level-1);  //suffix pattern of freArr[level-1][i]
		Q = freArr[level-1][start].substr(0,level-1);   //prefix pattern of freArr[level-1][start]
		if(Q != R)
		{
			start = binary_search(level, R, 0, size-1);
		}
		if (start<0 || start>=size)     //if not exist, begin from the first
			start=0;
		else
		{
			Q=freArr[level-1][start].substr(0,level-1);
			while(Q == R)
			{
				string cand = freArr[level-1][i].substr(0,level);
				cand = cand + freArr[level-1][start].substr(level-1,1);
				candidate.push_back(cand);
				start=start+1;
				if (start >= size) 
				{
					start=0;
					break;
				}
				Q=freArr[level-1][start].substr(0,level-1);
			}
		}
	}
}

void min_freItem()
{
	 map <string, int > counter;
	 string mine;
	 for(int t = 0; t < NumbS; t++)
	 {
		strcpy(S,sDB[t].S);
		for(int i=0;i<strlen(S);i++)
		{
			if (belong(S[i],sm))
			{
				mine=S[i];
				counter[mine]++;
			}			
		}	 
	 }
	 for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	 {
		 if (the_iterator->second < minsup)
		 {
			map <string, int >::iterator tmp = the_iterator;
			++tmp;
			counter.erase (the_iterator);
			the_iterator = tmp;
		 } 
		 else
		 {
			 freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			 ++the_iterator;
		 }
	}
}
int create_subnettree(vector <node> *nettree,int parent,int L,int pop)
{
	int j=0;
	if(L>ptn_len+1)
	{
		return 1;
	}
	int flag=0;
	for(j=parent+1;j<=parent+sub_ptn[L-2].min;j++)
	{
		if(belong(S[j],mw)==0)
		{
			flag=1;
			break;
		}
	}
	if(flag==1)
	{
		return 0;
	}

	for(j=parent+sub_ptn[L-2].min+1;j<=parent+sub_ptn[L-2].max+1;j++)
	{	
		if(S[j]==sub_ptn[L-2].end)
		{
			int k=nettree[L-1].size();
			flag=-1;
			for(int i=0;i<k;i++)
			{
				if(nettree[L-1][i].name==j)
				{
					flag=i;
					break;
				}
			}
			node anode;	
			if(flag==-1)
			{
				anode.name =j;
				anode.parent.clear ();
		    	anode.children .clear ();
				anode.max_leave=anode.name;
				anode.min_leave=anode.name;
			//	anode.min_root=nettree[L-2][pop].min_root;
			//	anode.max_root=nettree[L-2][pop].max_root;
				anode.used =false;
				int len=nettree[L-1].size ();
				//nettree[L-1].resize (len+1);
				anode.toleave =true;
				//nettree[L-1][len]=anode;
				nettree[L-1].push_back(anode);
				//int nc=nettree[L-2][pop].children .size ();
				//nettree[L-2][pop].children.resize (nc+1);
				//nettree[L-2][pop].children [nc]=len;
				nettree[L-2][pop].children.push_back(len);

				//int np=nettree[L-1][len].parent .size ();
				//nettree[L-1][len].parent.resize (np+1);
				//nettree[L-1][len].parent [np]=pop;//
				nettree[L-1].back().parent.push_back(pop);	
				int local=nettree[L-1].size();
				create_subnettree(nettree,j,L+1,local-1);				
				if(belong(S[j],m)==1)
				{	
					continue;
				}else
				{
					break;
				}
			}else
			{
				nettree[L-2][pop].children.push_back(flag);
				nettree[L-1][flag].parent.push_back(pop);
			}
			
		
		}///创建当前节点

		if(belong(S[j],mw)==0)
		{
			break;
		}
	}	

}

void create_nettree(vector <node> *nettree)
{	
	for (int i=0;i<ptn_len+1;i++)
		nettree[i].clear();//网树层初始化
	int *start;
	start=new int[ptn_len+1];
	for (i=0;i<ptn_len+1;i++)
		start[i]=0;
	
	for (i=0;i<strlen(S)-ptn_len+1;i++)
	{
		if(S[i]!=sub_ptn[0].start)
		{
			continue;
		}
		node anode;
		anode.name =i;
	    anode.parent.clear ();
		anode.children .clear ();
		anode.max_leave=anode.name;
		anode.min_leave=anode.name;
		anode.used =false;  
		int len=nettree[0].size ();
	//	nettree[0].resize (len+1);
		anode.toleave =true;
	//	anode.min_root=anode.max_root=anode.name;
		//nettree[0][len]=anode;
		nettree[0].push_back(anode);
		create_subnettree(nettree,i,2,len);
	}
	delete []start;	
}

void update_nettree(vector <node> *nettree)
{
	for (int i=ptn_len-1;i>=0;i--)
	{
		for(int j=nettree[i].size ()-1;j>=0;j--)
		{
			bool flag=true;
			int size=nettree[i][j].children.size ();
			for (int k=0;k<size;k++)
			{
				int child=nettree[i][j].children[k];
				if(k==0)
				{
					nettree[i][j].min_leave=nettree[i+1][child].min_leave;
				}
				if(k==size-1)
				{
					nettree[i][j].max_leave=nettree[i+1][child].max_leave;
				}
				if (nettree[i+1][child].used ==false)
				{
					flag=false;					
				}
			}
			//For nodes that do not arrive at leave,marking for the used=true
			nettree[i][j].used =flag;
			if(flag==true)
			{
				nettree[i][j].max_leave=nettree[i][j].name;
				nettree[i][j].min_leave=nettree[i][j].name;
				nettree[i][j].toleave = false;
			}
		}
	}
}



int minvaleposition(int *nodenumber)
{
	int p=ptn_len;
	for (int i=p-1;i>=0;i--)
	{
		if (nodenumber[i]<=nodenumber[p])
			p=i;
	}
	return p;
}
struct nodep
{
	int level,position;
};

int bts(int j, int  child, int root, vector <node> *nettree, occurrence & occin,occurrence & occ,int & ls, nodep * recovery)//int *  occin, int *occinname)	//BackTracking Strategy 
{ 
	if(j<=0)
		return -1;
	if (j>ptn_len)
		return 1;
	int parent=occin.position[j-1];    //The position of the parent in nettree
	//cout<<parent<<"...";
	
	int cs=nettree[j-1][parent].children.size ();   //The number of parent of the current node

	for (int t=0;t<cs;t++)
	{
		int child=nettree[j-1][parent].children[t];    //The position of the most left child
		if (nettree[j][child].used == true)
			continue;
		if (nettree[j][child].used ==false)
	//	&&	((a1<=maxlen&&a1>=minlen)||(b1>=minlen&&b1<=maxlen)))
		{
//					cout<<"..........."<<endl;
			occin.position[j]=child;			
			//occinname[j]=nettree[j][occin[j]].name ;
			int value=nettree[j][child].name;
			occ.position [j]=value ;
			nettree[j][child].used=true;
			nettree[j][child].toleave =false;
			recovery[ls].level =j;
			recovery[ls].position =child;
			ls++;
			//cout<<"ls"<<ls<<endl;
			int ret=bts(j+1, child, root, nettree, occin,occ,ls,recovery);//,occinname);
			//cout<<ret<<endl;
			if (ret==1)
				break;
		}
	}
	//cout<<ret<<endl;
	if (t==cs)		// cannot find it
	{
	//	h++;
		
		int ret=bts(j-1, child, root, nettree, occin,occ,ls,recovery);//, occinname);// backtracking
		//cout<<"leaf:"<<leaf<<endl;
		if (ret==-1)
			return -1;
		else
			return 1;
	}
	return 1;
			
	
}

void nonoverlength()
{	
	vector <node> *nettree;
	nettree=new vector <node> [ptn_len+1];
	int *nodenumber;
	nodenumber=new int [ptn_len+1];
	create_nettree(nettree);
	update_nettree(nettree);
	//displaynettree(nettree);
	//updatenettree(nettree,nodenumber);
	store1 = 0;
	nodep * recovery;
	recovery=new nodep[100*ptn_len];
	//cout <<"-------------------\n";
	//displaynettree(nettree);
	//displaychild(nettree);

	store.clear();
	
	for (int position=0;position<nettree[0].size ();position++)
	{
		//cout<<"nettree[ptn_len][position].used"<<nettree[ptn_len][position].used<<endl;

		if (nettree[0][position].used ==true)
		        continue;
		if (nettree[0][position].toleave ==false)
		{
		
			// false is cannot reach root
			continue;
		}

       // cout<<"true"<<endl;
		int root=nettree[0][position].name;
		//occin[0]=position;
		//occinname[0]=nettree[0][occin[0]].name ;
        occurrence occ;//////////////////////////////////////////////
		occurrence occin;  
		occ.position.resize (ptn_len+1);///////////////////////////////////////
		occin.position.resize (ptn_len+1);
		occin.position [0]=position;     //occin存放网树中对应层的第几个位置
		occ.position [0]=nettree[0][position].name ;   //occ存放序列中的位置
		nettree[0][position].used =true;
		//cout<<"nettree["<<ptn_len<<"]["<<position<<"].uesed="<<nettree[ptn_len][position].used;
		nettree[0][position].toleave=false;
		//向上最you祖先
		
		int j=1,ret=-1;
		//cout<<j<<"j"<<endl;
		int ls=0;
		ret=bts (j, position, root, nettree, occin,occ,ls,recovery);//, occinname);	//BackTracking Strategy
		
		if (ret==1)
		{

			//int len=store.size ();
			//store.resize (len+1);
			//store[len]=occ;
			store.push_back(occ);
		    
		}
		else
		{
			for (int jj=0;jj<ls;jj++)
			{
				int level=recovery[jj].level;
				int pos=recovery[jj].position ;
				nettree[level][pos].used=false;
				nettree[level][pos].toleave =true;
			}
		}
		memset(&occin,0,sizeof(occin)); 

		
	}
END:
	delete []recovery;
	delete []nettree;

	
}

int netGap(string p)
{
	deal_range(p);
	if(ptn_len+1 > strlen(S))
	{
		int num=0;
		return num;
	}
	nonoverlength();
//	cout<<p<<"支持数："<<store.size()<<endl;
	return store.size();
}
void read_file()
{
	fstream file;
	char filename[256];
	cout <<"---------------------------------------------------------------------------\nPlease input file name:";
	//cin>>filename;
	//cout <<filename<<endl;
	string buff;
	file.open("F:/NTP-Miner/NTP-DataSet/SP.txt",ios::in);   //open sequence file
	
	
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

void main()
{


	read_file();
//	cout<<"input the minlen,maxlen:"<<endl;
//	cin>>minlen>>maxlen;
	//minlen=1,maxlen=20;
	cout<<"input the mingap,maxgap:"<<endl;
	cin>>mingap>>maxgap;
	//mingap=0,maxgap=3;
	cout<<"input the minsup:"<<endl;
	cin>>minsup;
	//minsup=900;
	DWORD begintime=GetTickCount();
	min_freItem();
	int f_level=1;
	gen_candidate(f_level);	
	while(candidate.size()!=0)
	{
		int num = 0;

		for(int i=0;i<candidate.size();i++)
		{
			int occnum = 0; //the support num of pattern
			int rest = 0;
			
			string p = candidate[i];
			compnum++;
			for(int t = 0; t < NumbS; t++)
			{
				rest=minsup-occnum;
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					occnum += netGap(p);
				}
				if(occnum >= minsup)
				{
					freArr[f_level].push_back(p);
					break;
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
	cout<<"The number of frequent patterns:"<<frenum<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	cout <<"The number of calculation:"<<compnum<<" \n";
	
}
