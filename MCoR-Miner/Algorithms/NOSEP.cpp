﻿#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <time.h>
using namespace std;
#define K 6000    //The sequence number of sequence database
#define M 1000   //The length of pattern
#define N 200000  //The length of sequence
struct node         //nettree node
{
	int name;     //The corresponding position of node in sequence
	int min_leave, max_leave;   //The position of maxinum and mininum leave nodes
	vector <int> parent;     //The position set of parents
	vector <int> children;  //The position set of children
	bool used;      //true is has used, false is has not used
	bool toleave;  //true is can reach leaves, false is not
};
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
	char start, end;
	int min, max;
};
int store;
int minlen, maxlen;   //length constraint
int mingap, maxgap; //gap constraint
char S[N];  //sequence
int minsup;
int ptn_len;
int NumbS;
sub_ptn_struct sub_ptn[M];  //pattern p[i]
vector <string>* freArr = new vector <string>[M];  //store frequent patterns
vector <string> candidate;
vector <string> copattern;


int compnum = 0, frenum = 0;  //compute number and frequents number

double unum[K];//存储支持度
int ww = 0;


void deal_range(string pattern)
//put sub-pattern "a[1,3]b" into sub_ptn and sub_ptn.start=a，sub_ptn.end=b, sub_ptn.min=1，sub_ptn.max=3
{
	ptn_len = 0;
	memset(sub_ptn, 0, sizeof(sub_ptn_struct));
	char p[M];
	strcpy_s(p, pattern.c_str());
	if (strlen(p) == 1)
	{
		sub_ptn[ptn_len].start = p[0];
		sub_ptn[ptn_len].max = sub_ptn[ptn_len].min = 0;
	}
	for (int i = 0;i < strlen(p) - 1;i++)
	{
		sub_ptn[ptn_len].start = p[i];
		sub_ptn[ptn_len].end = p[i + 1];
		sub_ptn[ptn_len].min = mingap;
		sub_ptn[ptn_len].max = maxgap;
		ptn_len++;
	}
}

//find the first position of cand in the level of freArr by binary search
int binary_search(int level, string cand, int low, int high)
{
	int mid, start;
	if (low > high)
	{
		return -1;
	}
	while (low <= high)
	{
		mid = (high + low) / 2;
		int result = cand.compare(freArr[level - 1][mid].substr(0, level - 1)); //To avoid multiple calls the same function
		if (result == 0)
		{
			//find start
			int slow = low;
			int shigh = mid;
			int flag = -1;
			if (cand.compare(freArr[level - 1][low].substr(0, level - 1)) == 0)
			{
				start = low;
			}
			else
			{
				while (slow < shigh)
				{

					start = (slow + shigh) / 2;
					int sresult = cand.compare(freArr[level - 1][start].substr(0, level - 1));
					if (sresult == 0)   //Only two cases of ==0 and >0
					{
						shigh = start;
						flag = 0;
					}
					else
					{
						slow = start + 1;
					}
				}
				start = slow;
			}
			return start;
		}
		else if (result < 0)
		{
			high = mid - 1;
		}
		else
		{
			low = mid + 1;
		}
	}
	return -1;
}


void gen_candidate(int level)
{
	int size = freArr[level - 1].size();
	int start = 0;
	for (int i = 0;i < size;i++)
	{
		string Q = "", R = "";
		R = freArr[level - 1][i].substr(1, level - 1);  //suffix pattern of freArr[level-1][i]
		Q = freArr[level - 1][start].substr(0, level - 1);   //prefix pattern of freArr[level-1][start]
		if (Q != R)
		{
			start = binary_search(level, R, 0, size - 1);
		}
		if (start < 0 || start >= size)     //if not exist, begin from the first
			start = 0;
		else
		{
			Q = freArr[level - 1][start].substr(0, level - 1);
			while (Q == R)
			{
				string cand = freArr[level - 1][i].substr(0, level);
				cand = cand + freArr[level - 1][start].substr(level - 1, 1);
				candidate.push_back(cand);
				start = start + 1;
				if (start >= size)
				{
					start = 0;
					break;
				}
				Q = freArr[level - 1][start].substr(0, level - 1);
			}
		}
	}
}
void min_freItem()
{
	map <string, int > counter;
	string mine;
	for (int t = 0; t < NumbS; t++)
	{
		strcpy_s(S, sDB[t].S);
		for (int i = 0;i < strlen(S);i++)
		{
			if ((S[i] >= 'a' && S[i] <= 'z') || (S[i] >= 'A' && S[i] <= 'Z'))
			{
				mine = S[i];
				counter[mine]++;
			}
		}
	}
	for (map <string, int >::iterator the_iterator = counter.begin(); the_iterator != counter.end(); )
	{
		if (the_iterator->second < minsup)
		{
			map <string, int >::iterator tmp = the_iterator;
			++tmp;
			counter.erase(the_iterator);
			the_iterator = tmp;
		}
		else
		{
			freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			++the_iterator;
			if (the_iterator == counter.end())
				break;
			unum[ww] = the_iterator->second;
			ww++;
		}
	}
}


void create_nettree(vector <node>* nettree)
{
	for (int i = 0;i < ptn_len + 1;i++)
		nettree[i].resize(0);  //initialize nettree
	int* start;
	start = new int[ptn_len + 1];
	for (int i = 0;i < ptn_len + 1;i++)
		start[i] = 0;
	for (int i = 0;i < strlen(S);i++)
	{
		node anode;
		anode.name = i;
		anode.parent.resize(0);
		anode.children.resize(0);
		anode.max_leave = anode.name;
		anode.min_leave = anode.name;
		anode.used = false;
		//store root
		if (sub_ptn[0].start == S[i])
		{
			int len = nettree[0].size();
			nettree[0].resize(len + 1);
			anode.toleave = true;
			nettree[0][len] = anode;
		}
		for (int j = 0;j < ptn_len;j++)
		{
			if (sub_ptn[j].end == S[i])
			{
				//Look for parents from the layer above.
				int prev_len = nettree[j].size();
				if (prev_len == 0)
				{
					break;
				}
				//update start
				for (int k = start[j];k < prev_len;k++)
				{
					if (i - nettree[j][k].name - 1 > sub_ptn[j].max)
					{
						start[j]++;  // greater than max, cursor moves rearward
					}
				}
				//compare gap constraint
				if (i - nettree[j][prev_len - 1].name - 1 > sub_ptn[j].max)
				{
					continue;
				}
				if (i - nettree[j][start[j]].name - 1 < sub_ptn[j].min)
				{
					continue;
				}

				int len = nettree[j + 1].size();
				nettree[j + 1].resize(len + 1);
				anode.toleave = true;
				nettree[j + 1][len] = anode;
				for (int k = start[j];k < prev_len;k++)
				{
					if (i - nettree[j][k].name - 1 < sub_ptn[j].min)
					{
						break;
					}
					//Meet gap constraint
					//builds the relationship between father and son
					int nc = nettree[j][k].children.size();
					nettree[j][k].children.resize(nc + 1);
					nettree[j][k].children[nc] = len;
					int np = nettree[j + 1][len].parent.size();
					nettree[j + 1][len].parent.resize(np + 1);
					nettree[j + 1][len].parent[np] = k;
				}
			}
		}
	}
	delete[]start;
}

void update_nettree(vector <node>* nettree)
{
	for (int i = ptn_len - 1;i >= 0;i--)
	{
		for (int j = nettree[i].size() - 1;j >= 0;j--)
		{
			bool flag = true;
			int size = nettree[i][j].children.size();
			for (int k = 0;k < size;k++)
			{
				int child = nettree[i][j].children[k];
				if (k == 0)
				{
					nettree[i][j].min_leave = nettree[i + 1][child].min_leave;
				}
				if (k == size - 1)
				{
					nettree[i][j].max_leave = nettree[i + 1][child].max_leave;
				}
				if (nettree[i + 1][child].used == false)
				{
					flag = false;
				}
			}
			//For nodes that do not arrive at leave,marking for the used=true
			nettree[i][j].used = flag;
			if (flag == true)
			{
				nettree[i][j].max_leave = nettree[i][j].name;
				nettree[i][j].min_leave = nettree[i][j].name;
				nettree[i][j].toleave = false;
			}
		}
	}
}

void update_nettree_pc(vector <node>* nettree, occurrence& occin)
{
	//The advantage of the algorithm is do not have to traverse the entire nettree and just set the affected node as line way
	for (int level = ptn_len;level > 0;level--)
	{
		int position = occin.position[level];
		int num = nettree[level].size();
		for (;position < num;position++)
		{
			//find a node that is not used backwards and break
			if (nettree[level][position].used == false)
				break;
			//the number of parents
			int len = nettree[level][position].parent.size();
			//int name=nettree[level][position].name ;
			for (int i = 0;i < len;i++)
			{
				int parent = nettree[level][position].parent[i];
				int cs = nettree[level - 1][parent].children.size();
				//parent node have been used or cannot reach leaf node
				if (nettree[level - 1][parent].used == true)
					continue;
				if (cs == 1)   //one child
				{
					nettree[level - 1][parent].used = true;
					nettree[level - 1][parent].toleave = false;
				}
				else
				{
					int kk;
					for ( kk = 0;kk < cs;kk++)
					{
						int child = nettree[level - 1][parent].children[kk];
						if (nettree[level][child].used == false)
							break;
					}
					if (kk == cs)
					{
						nettree[level - 1][parent].used = true;
						nettree[level - 1][parent].toleave = false;
					}
				}
			}
		}
	}
}


void nonoverlength()
{
	vector <node>* nettree = new vector <node>[ptn_len + 1];
	create_nettree(nettree);
	update_nettree(nettree);
	store = 0;
	for (int position = 0;position < nettree[0].size();position++)
	{

		if (nettree[0][position].toleave == false)
		{
			// false is cannot reach root
			continue;
		}
		int root = nettree[0][position].name;
		int a = nettree[0][position].max_leave - root + 1;
		int b = nettree[0][position].min_leave - root + 1;
		if (!((minlen <= a && a <= maxlen) || (minlen <= b && b <= maxlen)))  //does not meet the length constraint
		{
			nettree[0][position].used = true;
			nettree[0][position].toleave = false;
			continue;
		}
		occurrence occin;
		occin.position.resize(ptn_len + 1);
		occin.position[0] = position;
		nettree[0][position].used = true;
		nettree[0][position].toleave = false;
		//Looking down for the most left child
		int j;
		for ( j = 1;j < ptn_len + 1;j++)
		{
			int parent = occin.position[j - 1];    //The position of the parent in nettree
			int cs = nettree[j - 1][parent].children.size();   //The number of children of the current node
			int t;
			for ( t = 0;t < cs;t++)
			{
				int child = nettree[j - 1][parent].children[t];    //The position of the most left child
				int a1 = nettree[j][child].max_leave - root + 1;
				int b1 = nettree[j][child].min_leave - root + 1;
				if (nettree[j][child].used == false &&
					((a1 <= maxlen && a1 >= minlen) || (b1 >= minlen && b1 <= maxlen)))
				{
					occin.position[j] = child;			//
					int value = nettree[j][child].name;
					nettree[j][child].used = true;
					nettree[j][child].toleave = false;
					break;
				}
			}
			if (t == cs)
			{
				for (int kk = 0;kk < j;kk++)
				{
					int pos = occin.position[kk];
					nettree[kk][pos].used = false;
					nettree[kk][pos].toleave = true;
				}
				break;
			}
		}
		if (j == ptn_len + 1)
		{
			store++;
			//if (store>rest)
				//goto END;
			update_nettree_pc(nettree, occin);
		}
		memset(&occin, 0, sizeof(occin));
	}
END:
	delete[]nettree;
}

//compute support
int netGap(string p)
{
	deal_range(p);
	if (ptn_len + 1 > strlen(S))
	{
		int num = 0;
		return num;
	}
	nonoverlength();
	return store;
}
void read_file(const char* namefile)
{
	fstream file;
	string buff;
	file.open(namefile, ios::in);   //open sequence file
	int i = 0;
	while (getline(file, buff))
	{
		strcpy_s(sDB[i].S, buff.c_str());
		i++;
	}
	NumbS = i;
	// print sequence database
	cout << "sDB and min_sup are as follows : " << endl;
	for (int t = 0; t < NumbS; t++)
	{
		sDB[t].id = t + 1;
		cout << "\t(" << sDB[t].id << ",(" << sDB[t].S << "))" << endl;
	}
}
/*
void main()
{
	read_file();
	minlen=1;
	maxlen=20;
	mingap=0;
	maxgap=3;
	strcpy(S,sDB[0].S);
	int occnum = netGap("aaatat");
	cout <<occnum<<endl;
}*/

int main(int argc, const char* argv[])
{
	//read_file(argv[1]);
	//mingap=atoi(argv[2]);
	//maxgap=atoi(argv[3]);
	//minsup= atoi(argv[4]);
	char  filename[100] = "gamesale.txt";
	read_file(filename);
	cout << "请输入最小和最大间隙:";
	cin >> mingap >> maxgap;
	cout << "请输入最小阈值：";
	cin >> minsup;
	cout << "请输入前缀:";
	string prefix;
	cin >> prefix;
	minlen = 0;maxlen = 300;
	int cannum = 0;
	/*
	cout<<"input the minlen,maxlen:"<<endl;
	cin>>minlen>>maxlen;
	//minlen=1,maxlen=20;
	cout<<"input the mingap,maxgap:"<<endl;
	cin>>mingap>>maxgap;
	//mingap=0,maxgap=3;
	cout<<"input the minsup:"<<endl;
	cin>>minsup;
	//minsup=900;
	*/
	DWORD begintime = GetTickCount();
	min_freItem();
	int f_level = 1;
	gen_candidate(f_level);
	while (candidate.size() != 0)
	{
		int num = 0;

		for (int i = 0;i < candidate.size();i++)
		{
			cannum++;
			int occnum = 0; //the support num of pattern
			//int rest = 0;

			string p = candidate[i];
			compnum++;
			for (int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				if (strlen(sDB[t].S) > 0)
				{
					strcpy_s(S, sDB[t].S);
					occnum += netGap(p);
				}
			}
			if (occnum >= minsup)
			{
				freArr[f_level].push_back(p);
				unum[ww] = occnum;
				ww++;
			}
		}
		f_level++;
		candidate.clear();
		gen_candidate(f_level);
	}
	for (int ii = prefix.length(); ii < f_level; ii++)
	{
		for (int j = 0; j < freArr[ii].size();j++)
		{
			if (freArr[ii][j].substr(0, prefix.length()) == prefix)
			{
				copattern.push_back(freArr[ii][j]);
			}
		}
		cout << endl;
	}
	DWORD endtime = GetTickCount();

	for (int i = 0; i < f_level; i++)
	{
		for (int j = 0; j < freArr[i].size();j++)
		{
			cout << freArr[i][j] << "   ";
			frenum++;
		}
		cout << endl;
	}
	cout << "The number of frequent patterns:" << frenum << endl;
	cout << "The time-consuming:" << endtime - begintime << "ms. \n";
	cout << "The number of calculation:" << compnum << " \n";

	cout << "共生模式：" << copattern.size() << endl;

	for (int ki = 0;ki < copattern.size();ki++)
		cout << copattern[ki] << "\t";

	time_t t = time(0);
	char tmp[32] = { NULL };
	//strftime(tmp, sizeof(tmp), "%Y-%m-%d %H:%M:%S", localtime(&t));
	ofstream mcfile;

	mcfile.open("result_file.txt", ios::app);

	string s;
	s.assign(argv[1]);
	s = s.substr(40);
	mcfile << tmp << "\t" << s << "\t" << minsup << "\t" << "\t[" << mingap << "," << maxgap << "]\t" << endtime - begintime << "\t\t\t" << frenum << "\t\t\t" << cannum << "\n";
	mcfile.close();


	ofstream maxfrefile;
	maxfrefile.open("result_fature.txt", ios::app);
	maxfrefile << tmp << "\t" << s << "\t" << minsup << "\t" << "\t[" << mingap << "," << maxgap << "]\t" << endtime - begintime << "\t\t\t" << frenum << "\n";

	for (int m = 0; m < f_level; m++)
	{
		for (int j = 0; j < freArr[m].size();j++)
		{
			maxfrefile << freArr[m][j] << "\t";
		}
	}
	maxfrefile << "\n";
	for (int q = 0; q < ww; q++)
	{
		maxfrefile << unum[q] << "\t";
	}
	maxfrefile << "\n";
	maxfrefile.close();



	return 0;
}