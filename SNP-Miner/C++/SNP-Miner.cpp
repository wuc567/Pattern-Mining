#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
using namespace std;
#define K 1000    //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 20000  //The length of sequence
#define MAXLENP 100
#define BUFFER 1000
int sequence_num = 0;

//#define sigmasize 4
//char sigma[sigmasize]={'A','C','G','T'}; //inp
int sigmasize=0; 
char sigma[M];

struct node         //nettree node
{
	int name;     //The corresponding position of node in sequence
	int min_leave,max_leave;   //The position of maxinum and mininum leave nodes
	vector <int> parent;     //The position set of parents
	vector <int> children;  //The position set of children
	bool used;      //true is has used, false is has not used
	bool toleave;  //true is can reach leaves, false is not
};
struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
};                 // sequence database
seqdb sDB0[K], sDB[K];
struct percharsequence
{
	int len;
	vector<int> store;
};
vector<percharsequence> SeqDB[M]; //character is stored by position
struct sorted_incomplete_nettree
{
	string name;
	float pos_sup;
	vector<percharsequence> intree;
};
vector<int> len_seq;

char S[N];  //sequence
int minsup;  
int NumbS;
vector <sorted_incomplete_nettree> *freArr;  //store frequent patterns
int compnum = 0, frenum = 0;  //compute number and frequents number

void calculate_intree(vector<int> &ic_ntree, vector<int> &next_level, int position, int sid)
{
	int size = ic_ntree.size();
	int len = next_level.size();
	vector<int> &store = SeqDB[position][sid].store; 
	int ch_size = store.size();
	int k = 0;
	for (int j = 0; j < size; j++)
	{
		int parent = ic_ntree[j];
		int child;
		for (; k < ch_size; k++)
		{
			child = store[k];
			if (child > parent)
			{
				next_level.push_back(child); 
				k++;
				break;
			}
		}
		if (k == ch_size) 
			break;
	}
	len = next_level.size();
}

float other_level(sorted_incomplete_nettree &sub_pattern, int position, sorted_incomplete_nettree &pattern)
{
	pattern.intree.clear();
	float occnum = 0;
	for (int sid = 0; sid < sequence_num; sid++)
	{
		float current_len = len_seq[sid];
		percharsequence atree;
		calculate_intree(sub_pattern.intree[sid].store, atree.store, position, sid);
		atree.len = atree.store.size();
		occnum += atree.len;
		pattern.intree.push_back(atree);
	}
	return occnum;
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
		int result=cand.compare(freArr[level-1][mid].name.substr(0,level-1));
		if (result == 0)
		{
			int slow=low;
			int shigh=mid;
			int flag=-1;
			if (cand.compare(freArr[level-1][low].name.substr(0,level-1)) == 0)
			{
				start=low;
			}
			else
			{
				while (slow<shigh)
				{
					
					start=(slow+shigh)/2;
					int sresult=cand.compare(freArr[level-1][start].name.substr(0,level-1)); 
					if (sresult==0)  
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
	int position;
	int start = 0;
	for(int i=0;i<size;i++)
	{
		string Q="",R="";
		R = freArr[level-1][i].name.substr(1,level-1);
		Q = freArr[level-1][start].name.substr(0,level-1);  
		if(Q != R)
		{
			start = binary_search(level, R, 0, size-1);
		}
		if (start<0 || start>=size)    
			start=0;
		else
		{
			Q=freArr[level-1][start].name.substr(0,level-1);
			while(Q == R)
			{
				compnum++;
				sorted_incomplete_nettree cand;
				cand.name = freArr[level-1][i].name.substr(0,level);
				cand.name = cand.name + freArr[level-1][start].name.substr(level-1,1);
				for(int t = 0; t < sigmasize; t++)
				{
					if(freArr[level-1][start].name[level-1] == sigma[t])
					{
						position = t;
						break;
					}

				}
				cand.pos_sup = other_level(freArr[level-1][i], position, cand); 
				if(cand.pos_sup >= minsup)
				{
					freArr[level].push_back(cand);
				}				
				start=start+1;
				if (start >= size) 
				{
					start=0;
					break;
				}
				Q=freArr[level-1][start].name.substr(0,level-1);
			}
		}
	}
}

float first_level(int position, sorted_incomplete_nettree &pattern)
{
	float occnum = 0;
	for (int sid = 0; sid < sequence_num; sid++)
	{
		vector<int> storeS;
		storeS = SeqDB[position][sid].store;
		pattern.intree = SeqDB[position];
		occnum += pattern.intree[sid].store.size();
	}
	return occnum;
}


void dealingfirstlevel(vector<sorted_incomplete_nettree> *freArr)
{
	sorted_incomplete_nettree current_pattern;
	for (int i = 0; i < sigmasize; i++)
	{
		compnum++;
		current_pattern.name = sigma[i];
		current_pattern.pos_sup = first_level(i, current_pattern); 
		if (current_pattern.pos_sup >= minsup) 
		{
			freArr[0].push_back(current_pattern);
		}
	}
}

void store_into_vec(seqdb sDB[K])
{
	int sid;
	for (sid = 0; sid < sequence_num; sid++)
	{
		percharsequence temp[M];
		string ss;
		percharsequence current_sequence;
		current_sequence.len = strlen(sDB[sid].S);
		len_seq.push_back(current_sequence.len);
		ss = sDB[sid].S;
		int i;
		for (i = 0; i < current_sequence.len; i++)
		{
			for (int j = 0; j < sigmasize; j++)
			{
				if (ss[i] == sigma[j])
				{
					temp[j].store.push_back(i);
					break;
				}
			}
		}
		for (i = 0; i < sigmasize; i++)
		{
			temp[i].len = temp[i].store.size();
			SeqDB[i].push_back(temp[i]);
		}
	}
}

void min_sigma()
{
	 map <char, int > counter;
	 char mine;
	 for(int t = 0; t < sequence_num; t++)
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
	 sigmasize= 0;
	 for (map <char, int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); the_iterator++)
	 {
		 sigma[sigmasize] = the_iterator->first;
		 sigmasize++;
	}
}

void read_file()
{
	FILE *fp=NULL;
	string buff;
	char p[20];
	cout << "Input filename: " << endl; 
	fp=fopen("SDB4.txt","r+");
	int i = 0;
	while (fscanf(fp,"%s",sDB0[i].S )!= EOF)
	{
		i++;
	}
	fclose(fp);
	int filetype = 0;
	if (filetype == 1)
	{
		for (int line = 0; line < i; line++) 
		{
			strcpy(sDB[sequence_num].S, sDB0[line].S + 1);
			sequence_num++;
		}
	}
	else
	{
		for (int line = 0; line < i; line++) 
		{
			strcpy(sDB[sequence_num].S, sDB0[line].S);
			sequence_num++;
		}
	}
	cout << "sequence number: " << sequence_num << endl; 
}

void main()
{
	freArr = new vector <sorted_incomplete_nettree>[M]; 
	read_file();
	min_sigma();
	store_into_vec(sDB);
	minsup=4300;
	sorted_incomplete_nettree sub_pattern, current_pattern;
	DWORD begintime=GetTickCount();
	dealingfirstlevel(freArr);
	int f_level=1;
	gen_candidate(f_level);	
	while(freArr[f_level].size()!=0)
	{
		f_level++;
		gen_candidate(f_level);
	}
	DWORD endtime=GetTickCount();
	for(int i = 0; i<f_level; i++)
	{
		for(int j = 0; j<freArr[i].size();j++)
		{
			cout<<freArr[i][j].name<<"\t";
			frenum++;
		}
		cout<<endl;
	}
	cout<<"The number of frequent patterns:"<<frenum<<endl;
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	cout <<"The number of calculation:"<<compnum<<" \n";
}