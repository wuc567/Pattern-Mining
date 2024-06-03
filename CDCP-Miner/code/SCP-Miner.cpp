#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <fstream>
#include <queue>
#include <cmath>
using namespace std;

#define K 20000   //The sequence number of sequence database
#define M 100   //The length of pattern
#define N 60 //The length of sequence
struct seqdb
{
	int id;	// sequence id
	char S[N]; // sequence
};			   // sequence database

#define sigmasize 4
char sigma[sigmasize] = { 'A','C','G','T' };

int flag[sigmasize] = { 0 };
double precision = 0.000001;

struct percharsequence
{
	int len;
	vector<int> store;
};
vector<percharsequence> SeqDB[sigmasize][2]; //two class sequence, character is stored by position
struct sorted_incomplete_nettree
{
	string name;
	float CR;
	float pos_sup;
	vector<percharsequence> intree[2];
};
vector<int> len_seq[2];

int sequence_num[2] = { 0, 0 };
float density, minsup;
int pruned = 0, countflag = 0;
int need_num = 0;
vector<string> prune_pat;

struct sorted_queue
{
	string name;
	float CR;
	float pos_sup;
	friend bool operator<(sorted_queue a, sorted_queue b)
	{
		return a.CR > b.CR;
	}
};

int HalfSearch(vector<sorted_incomplete_nettree>& st, int begin, int end, sorted_incomplete_nettree& value)
{
	int mid = (begin + end) / 2;
	for (; begin < end; mid = (begin + end) / 2)
	{
		if (value.CR > st[mid].CR)
		{
			begin = mid + 1;
		}
		else if (value.CR < st[mid].CR)
		{
			end = mid - 1;
		}
		else if (fabs(value.CR - st[mid].CR) < precision)
		{
			break;
		}
	}
	if (fabs(value.CR - st[mid].CR) < precision)
		return mid;
	else if (value.CR > st[end].CR)
		return end + 1;
	else if (value.CR < st[begin].CR)
		return begin;
}
void OrderAInsert(vector<sorted_incomplete_nettree>& st, sorted_incomplete_nettree& value)
{
	int len = st.size();
	if (len == 0)
	{
		st.push_back(value);
		return;
	}
	int begin = 0, end = len;
	int position = HalfSearch(st, begin, end - 1, value);
	st.insert(st.begin() + position, value);
}

void calculate_intree(vector<int>& ic_ntree, vector<int>& next_level, int position, int sid, int lab)
{
	int size = ic_ntree.size();
	int len = next_level.size();
	vector<int>& store = SeqDB[position][lab][sid].store;
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
void displaytop(priority_queue<sorted_queue> topk)
{
	int len = topk.size();

	while (!topk.empty())
	{
		cout << topk.top().name << "\t" << topk.top().CR << endl;
		topk.pop();
	}
}
float other_level(sorted_incomplete_nettree& sub_pattern, int position, sorted_incomplete_nettree& pattern, int lab)
{
	float sup_number = 0;
	float sup_rate;
	pattern.intree[lab].clear();
	for (int sid = 0; sid < sequence_num[lab]; sid++)
	{
		float occnum = 0;
		float den = 0;
		float current_len = len_seq[lab][sid];
		percharsequence atree;
		calculate_intree(sub_pattern.intree[lab][sid].store, atree.store, position, sid, lab);
		atree.len = atree.store.size();
		occnum = atree.len;
		pattern.intree[lab].push_back(atree);
		if (current_len > 0)
		{
			den = occnum / (current_len);
			if (den > density)
			{
				sup_number++;
			}
		}
	}
	sup_rate = sup_number / sequence_num[lab];
	return sup_rate;
}

float first_level(int position, sorted_incomplete_nettree& pattern, int lab)
{
	float sup_number = 0;
	float sup_rate;
	for (int sid = 0; sid < sequence_num[lab]; sid++)
	{
		vector<int> storeS;
		storeS = SeqDB[position][lab][sid].store;
		pattern.intree[lab] = SeqDB[position][lab];
		float occnum = 0;
		float den = 0;
		float current_len = len_seq[lab][sid];
		occnum = pattern.intree[lab][sid].store.size();
		if (current_len > 0)
		{
			den = occnum / (current_len);
			if (den > density)
			{
				sup_number++;
			}
		}
	}
	sup_rate = sup_number / sequence_num[lab];
	return sup_rate;
}
void dealingfirstlevel( //incomplete_nettree &current_pattern, sorted_queue &current_pat,
	priority_queue<sorted_queue>& top_ps, vector<sorted_incomplete_nettree>& entree, int& count)
{
	//process the pattern  with length 1
	sorted_incomplete_nettree current_pattern;
	sorted_queue current_pat;
	for (int i = 0; i < sigmasize; i++)
	{
		need_num++;
		current_pattern.name = sigma[i];
		current_pat.name = sigma[i];
		current_pattern.pos_sup = current_pat.pos_sup = first_level(i, current_pattern, 0);
		float neg_sup = first_level(i, current_pattern, 1);
		current_pattern.CR = current_pat.CR = current_pat.pos_sup - neg_sup;
		if (current_pat.pos_sup > 0) //wyh
		{
			flag[i] = 1;
			countflag++;
			OrderAInsert(entree, current_pattern);
			if (current_pat.CR > 0)
				top_ps.push(current_pat);
			if (top_ps.size() > minsup)
			{
				top_ps.pop();
			}
			count++;
		}
		else
		{
			flag[i] = 0;
			pruned++;
		}
	}
}
void output_entree(int level, vector<sorted_incomplete_nettree>& entree)
{
	int num = entree.size();
	int i = 0;
	if (level != 0)
	{
		cout << "the entree cycle level is  " << level << endl;
	}
	else
	{
		cout << "the first level entree is " << endl;
	}
	cout << "entree contain: ";
	for (i = num - 1; i >= 0; i--)
	{
		cout << entree.at(i).name << " ";
	}
	cout << endl;
}
//void Topk(vector <pattern> &top_ps)
void Topk(priority_queue<sorted_queue>& top_ps)
{
	int lenofpattern, cur_len_pattern;
	int i, count = 0;
	sorted_queue sub_pat, current_pat, tmp_pat, lowest_pat;
	int NOcandp = 0;
	int maxsize = 0;
	vector<sorted_incomplete_nettree> entree;
	cout << "calculated the candidate pattern is:" << endl;
	dealingfirstlevel(top_ps, entree, count);
	NOcandp += sigmasize;
	maxsize = entree.size();
	cur_len_pattern = 1;
	int out_level = 0;
	sorted_incomplete_nettree sub_pattern, current_pattern;
	while (!entree.empty())
	{
		out_level++;
		current_pattern.intree[0].clear();
		current_pattern.intree[1].clear();
		//sub_pattern=entree.front ();
		//entree.pop ();
		int sizeentree = entree.size();
		sub_pattern = entree[sizeentree - 1];
		entree.pop_back();
		//NOcandp += sigmasize;
		int size_t = top_ps.size();
		if (size_t > 0)
		{
			lowest_pat = top_ps.top();
		}
		else
		{
			lowest_pat.CR = 0;
			lowest_pat.pos_sup = 0;
			lowest_pat.name = "";
		}
		if (sub_pattern.pos_sup <= 0 || (size_t >= minsup && sub_pattern.pos_sup <= lowest_pat.CR)) //wyh
		{
			pruned++;
			continue;
		}
		NOcandp += countflag;
		for (i = 0; i < sigmasize; i++)
		{
			if (flag[i] == 0)
			{
				continue;
			}
			current_pattern.name = current_pat.name = sub_pattern.name + sigma[i];
			need_num++;
			lenofpattern = current_pattern.name.length();
			if (cur_len_pattern < lenofpattern)
			{
				cur_len_pattern++;
				//cout<<"Processing the patterns with length "<<cur_len_pattern<<"..."<<endl;
				//displaytop(top_ps);
			}
			current_pattern.pos_sup = current_pat.pos_sup = other_level(sub_pattern, i, current_pattern, 0);
			count = top_ps.size();
			if (count > 0)
			{
				tmp_pat = top_ps.top();
			}
			else
			{
				tmp_pat.CR = 0;
				tmp_pat.name = "";
				tmp_pat.pos_sup = 0;
			}
			if ((current_pat.pos_sup <= 0) || (count >= minsup && current_pat.pos_sup <= tmp_pat.CR))
			{
				pruned++;
			}
			else
			{
				float neg_sup = other_level(sub_pattern, i, current_pattern, 1);
				current_pattern.CR = current_pat.CR = current_pat.pos_sup - neg_sup; ///contrast pattern mining
				if ((current_pat.CR > tmp_pat.CR) || (top_ps.size() < minsup && current_pat.CR > 0))
				{
					top_ps.push(current_pat);
					count++;
					if (top_ps.size() > minsup)
					{
						//cout<<"Outside:\t"<< top_ps.top().name<<endl;   
						top_ps.pop();
					}
				}
				OrderAInsert(entree, current_pattern);
				int entree_size = entree.size();
				if (maxsize < entree_size)
				{
					maxsize = entree_size;
				}
			}
		}
	}
	cout << "TOPK mining over!" << endl;
	cout << "calculated candidate pattern number is: " << need_num << endl;
	cout << "calculated " << NOcandp << " candidate patterns!" << endl;
	cout << "pured number is: " << pruned << endl;
	cout << "the max length of queue is: " << maxsize << endl;
}

void disp(vector<int>& store)
{
	int len = store.size();
	for (int pos = 0; pos < len; pos++)
		cout << store[pos] << "\t";
	cout << endl
		<< endl;
}

void store_into_vec(seqdb sDB[2][K], int lab)
{
	int sid;
	for (sid = 0; sid < sequence_num[lab]; sid++)
	{
		percharsequence temp[sigmasize];
		string ss;
		percharsequence current_sequence;
		current_sequence.len = strlen(sDB[lab][sid].S);
		len_seq[lab].push_back(current_sequence.len);
		ss = sDB[lab][sid].S;
		int i;
		for (i = 0; i < current_sequence.len; i++)
		{
			//if (ss[i]>='a'&&ss[i]<='z')
			//ss[i]-=32;
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
			SeqDB[i][lab].push_back(temp[i]);
		}
	}
}
seqdb sDB0[K], sDB[2][K];
void read_file()
{
	FILE* fp = NULL;
	//fstream file;
	string buff;
	char p[20];
	cout << "Input filename: " << endl;
	//cin>>p;
	//file.open(p,ios::in);   //open sequence file

	fp = fopen("d:/×éÄÚËã·¨/pattern-mining-master/scp-miner/dataset/TSS.txt", "r+");
	int i = 0;
	while (fscanf(fp, "%s", sDB0[i].S) != EOF)
	{
		//strcpy(sDB0[i].S, buff.c_str());
		i++;
	}
	fclose(fp);
	//	file.close();
		//filetype=1;	//time-sequence,labled
		//filetype=0;	//non-labled
	int filetype = 0;
	if (filetype == 1)
	{
		//read_file-labled
		for (int line = 0; line < i; line++) //separated in sDB1  sDB2
		{
			if (sDB0[line].S[0] == '1')
			{
				strcpy(sDB[0][sequence_num[0]].S, sDB0[line].S + 1);
				sequence_num[0]++;
			}
			else if (sDB0[line].S[0] == '2')
			{
				strcpy(sDB[1][sequence_num[1]].S, sDB0[line].S + 1);
				sequence_num[1]++;
			}
		}
	}
	else
	{
		//read_file-non-labled
		for (int line = 0; line < i; line++) //separated in sDB1  sDB2
		{
			if (line < 100)
			{
				strcpy(sDB[0][sequence_num[0]].S, sDB0[line].S);
				sequence_num[0]++;
			}
			else
			{
				strcpy(sDB[1][sequence_num[1]].S, sDB0[line].S);
				sequence_num[1]++;
			}
		}
	}
	cout << "positive sequence number: " << sequence_num[0] << endl; //output the sequence number of sDB1
	cout << "neggative sequence number: " << sequence_num[1] << endl; //output the sequence number of sDB2
	store_into_vec(sDB, 0);
	store_into_vec(sDB, 1);
	//disp (SeqDB[0][0][0].store );

	//disp (SeqDB[1][0][0].store );
	//disp (SeqDB[2][0][0].store );
	//disp (SeqDB[3][0][0].store );
	/*disp (SeqDB[0][0][1].store );
	disp (SeqDB[0][1][0].store );*/
}

int main()
{
	read_file();
	//cout<<sDB[1][0].S;
	cout << "input the value of K:" << endl;
	//cin>>minsup;
	minsup = 10;
	//minsup = 15;
	cout << "input the value of density:" << endl;
	//cin>>density;
	density = 0.075;
	priority_queue<sorted_queue> vec;
	DWORD begintime = GetTickCount();
	Topk(vec);
	DWORD endtime = GetTickCount();
	//ofstream of("feature.txt",ios::app);
	int pru_num = 0;
	int i = 0;
	if (vec.empty())
		cout << "Don't have contrast pattern!" << endl;
	cout << "mining " << vec.size() << " pattern, the mining result is:" << endl;
	while (!vec.empty())
	{
		cout << i << "\t" << vec.top().name << "\t" << vec.top().CR << endl;
		i++;
		vec.pop();
	}
	cout << endl;
	//vec.clear();
	cout << "The time-consuming:" << endtime - begintime << "ms. \n";
	cout << endl;
	return 0;
}

