#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <string>
#include <afxwin.h>
#include <fstream>
#include <cctype>
#include <malloc.h>
#include <wtypes.h>
#include <fstream>
using namespace std;
#define N 10000
#define M 1000
#define K 10000
char S[N];
struct node
{
	int name;
	int min_leave,max_leave;
	vector <int> parent;
	vector <int> children;
	//int *parent,pn;
	//int *children,pc;
	bool used;
	//bool toroot;
	bool toleave;
	int minroot_leave;
	int maxroot_leave;
};
struct seqdb                 
{
	int id;                  // sequence id  
	char S[N];               // sequence  
} sDB[K];


int count=0;
int jz=0;
int h=0;
//int minlen,maxlen;   //length constraint
int mingap,maxgap; //gap constraint
int store1;
struct sub_ptn_struct
{
	char start,end;		//
	//int min,max;		//
};
struct occurrence
{
	vector <int > position;
};
vector <occurrence> store;
sub_ptn_struct sub_ptn[M];  //pattern p[i]
int ptn_len=0;  //the length of pattern
int seq_len=0;
int NumbS, minsup;
//int maxgap=-1;
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> candidate; 
int compnum = 0, frenum = 0;  //compute number and frequents number

void deal_range(string pattern)      
{
	ptn_len=0;
	memset(sub_ptn, 0, sizeof(sub_ptn_struct));
	char p[M];
	strcpy(p,pattern.c_str()); 
	if (strlen(p)==1)
	{
		sub_ptn[ptn_len].start = p[0];
	}
	for(int i=0;i<strlen(p)-1;i++ )
	{
		sub_ptn[ptn_len].start =p[i];
		sub_ptn[ptn_len].end =p[i+1];
		ptn_len++;
	}
}

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
		int result=cand.compare(freArr[level-1][mid].substr(0,level-1)); 
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
			if ((S[i]>='a'&&S[i]<='z')||(S[i]>='A'&&S[i]<='Z'))
			{
				mine=S[i];
				counter[mine]++;
			}			
		}	 
	 }
	 for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	 {
		 compnum++;
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


void createnettree_length(vector <node> *nettree)
{
	for (int i=0;i<ptn_len+1;i++)
		nettree[i].clear();  //initialize nettree
	int *start;
	start=new int[ptn_len+1];
	for (i=0;i<ptn_len+1;i++)
		start[i]=0;
	for (i=0;i<strlen(S);i++)
	{
		node anode;
		anode.name =i;
		anode.parent.clear();
		anode.children .clear();
		anode.max_leave=anode.name;
		anode.min_leave=anode.name;
		anode.used =false;   
		//store root
		if (sub_ptn[0].start ==S[i])
		{
			int len=nettree[0].size ();
			//nettree[0].resize (len+1);
			anode.toleave =true;
			//nettree[0][len]=anode;
			nettree[0].push_back(anode);
		}
		for (int j=0;j<ptn_len;j++)
		{
			if (sub_ptn[j].end==S[i])
			{
				//Look for parents from the layer above.
				int prev_len=nettree[j].size ();
				if (prev_len==0)
				{
					break;
				}
				int len=nettree[j+1].size ();
				anode.toleave =true;
				nettree[j+1].push_back(anode);
				for (int k=start[j];k<prev_len;k++)
				{
					if (i-nettree[j][k].name <= 0 )
						continue;
					nettree[j][k].children.push_back(len);
					nettree[j+1].back().parent.push_back(k);
				}
			}
		}
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
void displaynettree(vector <node> *nettree)
{
	for (int i=0;i<ptn_len+1;i++)
	{
		cout <<i<<":";
		for (int j=0;j<nettree[i].size ();j++)
			if (nettree[i][j].used ==false)
				cout <<nettree[i][j].name <<"\t";
		cout <<endl;
	}
}


#include<stack>
struct storenode
{
	int position;
	int level;
};
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
void displayocc(occurrence &occ)
{
	//cout <<"An occurrence is:";
	cout <<"<";
	for (int i=0;i<ptn_len;i++)
		cout <<occ.position [i]<<",\t";
	cout <<occ.position [i];
	cout <<">"<<endl;
}
void displaychild(vector <node> *nettree)
{
	cout <<"--------child----------------\n";
	for (int i=0;i<ptn_len+1;i++)
	{
		cout <<i<<":";
		for (int j=0;j<nettree[i].size ();j++)
		{
			//if (nettree[i][j].LPN >0)
			{
				//对不能抵达树叶层的结点不做显示
				cout <<nettree[i][j].children .size ()  <<"\t";
			}
		}
		cout <<endl;
	}
}
struct nodep
{
	int level,position;
};
int bts(int j, int  child, int root, vector <node> *nettree, occurrence & occin,occurrence & occ,int & ls, nodep * recovery)//int *  occin, int *occinname)	//BackTracking Strategy 
{ 

    if (j<=0)
		return -1;
	if (j>ptn_len)
	{
		return 1;
	}
	else 
	{
			int parent=occin.position  [j-1];    //The position of the parent in nettree
			int cs=nettree[j-1][parent].children.size ();   //The number of children of the current node
			for (int t=0;t<cs;t++)
			{
			    child=nettree[j-1][parent].children[t];    //The position of the most left child
				if (nettree[j][child].used == true)
					continue;
				if (nettree[j][child].used ==false)
				{
					occin.position  [j]=child;			//
					int value=nettree[j][child].name;
					occ.position [j]=value ;

					nettree[j][child].used=true;
					nettree[j][child].toleave =false;
					recovery[ls].level =j;
					recovery[ls].position =child;
					ls++;
					int ret=bts(j+1, child, root, nettree, occin,occ,ls,recovery);//,occinname);
					if (ret==1)
						break;
				}
			}
			if (t==cs)		// cannot find it
			{
				h++;
				int ret=bts(j-1, child, root, nettree, occin,occ,ls,recovery);//, occinname);// backtracking
				if (ret==-1)
					return -1;
				else
					return 1;
			}
			return 1;
	}
}
void nonoverlength()
{
	
	vector <node> *nettree;
	nettree=new vector <node> [ptn_len+1];
	int *nodenumber;
	nodenumber=new int [ptn_len+1];
	createnettree_length(nettree);
	update_nettree(nettree);
	store1 = 0;
	nodep * recovery;
	recovery=new nodep[100*ptn_len];
	store.clear ();
	
	for (int position=0;position<nettree[0].size ();position++)
	{
		if (nettree[0][position].used ==true)
			continue;
		if (nettree[0][position].toleave ==false)
		{
			// false is cannot reach root
			continue;
		}
		int root=nettree[0][position].name;
        occurrence occ;//////////////////////////////////////////////
		occurrence occin;  
		occ.position .resize (ptn_len+1);///////////////////////////////////////
		occin.position .resize (ptn_len+1);
		occin.position [0]=position;
		occ.position [0]=nettree[0][position].name ;
		nettree[0][position].used =true;
		nettree[0][position].toleave =false;
		int j=1,ret=-1;
		int ls=0;
		ret=bts (j, position, root, nettree, occin,occ,ls,recovery);//, occinname);	//BackTracking Strategy
		
		if (ret==1)
		{
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

void Inputstr(char *fn,char *str)
{
	FILE* fp=fopen(fn,"r+");
	if (NULL==fp)
	{
		cout<<"Cannot find the file.\n";
		return;
	}
	fseek(fp,0,SEEK_END); 
	int len =ftell(fp);
	fseek(fp,0,0); 
	fscanf(fp, "%s",str);
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
	return store.size();
}

void read_file()
{
	fstream file;
	char filename[256];
	string buff;
	file.open("SDB8.txt",ios::in);   //open sequence file
	
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
	}
	
}
void main()
{
	read_file();
	minsup=5000;
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
			string p = candidate[i];
			compnum++;
			for(int t = 0; t < NumbS; t++)
			{
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
	cout <<"耗时"<<(endtime-begintime)/50.0<<"ms. \n";

}
