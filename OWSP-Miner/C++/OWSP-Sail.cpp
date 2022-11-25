// sail.cpp : Defines the entry point for the console application.

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
#define K 60000    //The sequence number of sequence database
#define M 1000   //The length of pattern
#define N 300000  //The length of sequence
char S[N];
int NumbS;
int s_length;
char m_pattern[1000];
int m_result;
int  m_timecost;
int  m_min=0;
int  m_max=800;
void convert_p_to_ruler(string p);
void create_matching_lookup();
void create_matching_table();
void calculate();
int maxlen, minlen;
char disp_all;
struct punit
{
	char start, end; //
	int min, max; //
};
int maxp_c = -1;
punit pu[M];  //pattern p[i]
int pu_len = 0;  //the length of pattern   pu_len=m
int total_occurence;
int t_occ;
int new_t_occ;
int occurence[M];
int one_off_count;
int max_one_off_count;
// The one and only application object
// using namespace std;
int *match;
map<char, double> mymap;
struct seqdb
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];
map <string, int> frequent;  //frequent pattern and its support
double minunity;
int ptn_len;
int nn = 0;   //The number of types of events
			  //int NumbS=0;
int store = 0;
int	num_occur = 0;
int occnum = 0;
//double hupval;
//double uphupval = 0;
int upminsup = 10;//70
char gapstr[1000];
string item[30];   // event set
				   //sub_tn_struct sub_ptn[M];  //a[0,3]c[0,3]t
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> *canArr = new vector <string>[M];//  store can patterns
vector <string> candidate;
int compnum = 0, frenum = 0;  //compute number and frequents number
DWORD time1;
DWORD time2;
int hxms[1000];//候选模式
int pfms[1000];//频繁模式
void readfile()
{   
	fstream file;
	string buff;
	char filename[256]="SDB1.txt";//tiantan800out.txt
	cout <<"---------------------------------------------------------------------------\nPlease input file name:";
	//cin>>filename;
	cout <<filename<<endl;
	file.open(filename,ios::in);   //open sequence file
	/*
	//file.open("Dataset/DNA6.txt",ios::in);   //open sequence file
	fstream file;
	string buff;
	file.open(namefile, ios::in);   //open sequence file
	*/
	int i = 0;
	while (getline(file, buff))
	{
		strcpy(sDB[i].S, buff.c_str());
		i++;
	}
	NumbS = i;
	// print sequence database
	//cout << "sDB and min_sup are as follows : " << endl;
	for (int t = 0; t < NumbS; t++)
	{
		sDB[t].id = t + 1;
		//	cout << "\t(" << sDB[t].id << ",(" << sDB[t].S << "))" << endl;
	}
}

bool gapContain(char p_gapstr[], char c){
	while(*p_gapstr != '\0'){
		//printf("哈哈%c", *p_gapstr);
		if(*p_gapstr == c){
			//printf("666");
			return true;
		}
		p_gapstr++;

	}
	return false;
}

void min_freItem()
{
	map <string, int > counter;
	string mine;
	//upminsup=ceil(minunity/7);
	for (int t = 0; t < NumbS; t++)  //count item and its support num
	{
		strcpy(S, sDB[t].S);
		for (int i = 0; i<strlen(S); i++)
		{
			if (((S[i] >= 'a'&&S[i] <= 'z') || (S[i] >= 'A'&&S[i] <= 'Z')) && !gapContain(gapstr, S[i]))
			{
				mine = S[i];
				counter[mine]++;

			}

		}

	}

	nn = 0;

	for (map <string, int >::iterator the_iterator = counter.begin(); the_iterator != counter.end(); )
	{
		hxms[0]++;
		//cout<<the_iterator->first<<the_iterator->second <<endl;

		string pp = the_iterator->first;

	//	hupval = mymap.find(pp[0])->second;

		if (the_iterator->second >= upminsup)
		{
			canArr[0].push_back(the_iterator->first);

//			if (the_iterator->second*hupval >= minunity)

	//		{

				freArr[0].push_back(the_iterator->first);
				cout<<"匹配模式为："<<pp<<endl;
				cout<<"支持度："<<the_iterator->second<<endl;
				frenum++;

		//	}
				pfms[0]++;
		}

		++the_iterator;


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
		int result = cand.compare(canArr[level - 1][mid].substr(0, level - 1)); //To avoid multiple calls the same function
		if (result == 0)
		{
			//find start
			int slow = low;
			int shigh = mid;
			int flag = -1;
			if (cand.compare(canArr[level - 1][low].substr(0, level - 1)) == 0)
			{
				start = low;
			}
			else
			{
				while (slow<shigh)
				{

					start = (slow + shigh) / 2;
					int sresult = cand.compare(canArr[level - 1][start].substr(0, level - 1));
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
		else if (result<0)
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
	int size = canArr[level - 1].size();
	int start = 0;
	for (int i = 0; i<size; i++)
	{
		string Q = "", R = "";
		R = canArr[level - 1][i].substr(1, level - 1);  //suffix pattern of freArr[level-1][i] 第1个位置后面level-1个字符赋给R
		Q = canArr[level - 1][start].substr(0, level - 1);   //prefix pattern of freArr[level-1][start]
		if (Q != R)
		{
			start = binary_search(level, R, 0, size - 1);	//通过二分查找，查找在freArr[level-1]中R出现的首个位置
		}
		if (start<0 || start >= size)     //if not exist, begin from the first
			start = 0;
		else
		{
			Q = canArr[level - 1][start].substr(0, level - 1);
			while (Q == R)
			{
				string cand = canArr[level - 1][i].substr(0, level);
				cand = cand + canArr[level - 1][start].substr(level - 1, 1);
				candidate.push_back(cand);	//自动将cand插入向量candidate末尾
				start = start + 1;
				if (start >= size)
				{
					start = 0;
					break;
				}
				Q = canArr[level - 1][start].substr(0, level - 1);
			}
		}
	}
}
void display_a_match(int *match)        //????????????????
{
	int i;
	printf("{");
	for (i = 0; i < pu_len; i++)
		printf("%d\t,", match[i]);
	printf("%d}\n", match[i]);
}
//判断是否满足弱通配
bool gap_ok(int s_start, int s_end){
	bool re = true;
	for(int coop = s_start + 1; coop < s_end; coop++){
		re = false;
		for(int gi = 0; gi < strlen(gapstr); gi++){
			if(gapstr[gi] == S[coop]){
				re = true;
				break;
			}
		}
		if(re == false){
			break;
		}
	}
	return re;

}
bool getoptmatch(char *s, int end, int max, int min, bool *used, int *match)
{
	struct row
	{
		int *r;
	};
	row *table;
	int start;
	start = end - max;
	if (start < 0)
		start = 0;
	int i, j, kn, kx, k;
	int len = end - start + 1;
	table = new row[len];
	for (i = 0; i < len; i++)
	{
		table[i].r = new int[pu_len + 1];
		for (j = 0; j <= pu_len; j++)
		{
			table[i].r[j] = 0;
		}
	}

	for (i = start; i < end; i++)
	{
		//????
		if (used[i] == false)
		{
			for (j = 0; j < pu_len; j++)
			{
				if (s[i] == pu[j].start)
				{
					if (j == 0)
					{
						table[i - start].r[j] = 1;
					}
					else
					{
						kn = i - pu[j - 1].max - 1;
						kx = i - pu[j - 1].min - 1;
						if (kn < start)
							kn = start;
						if (kx >= start)
						{
							for (k = kn; k <= kx; k++)
							{
								if (table[k - start].r[j - 1] == 1)
								{
									table[i - start].r[j] = 1;
									break;
								}
							}
						}
					}
				}
			}
		}
	}
	kn = i - pu[pu_len - 1].max - 1;
	kx = i - pu[pu_len - 1].min - 1;
	if (kn < start)
		kn = start;
	for (k = kn; k <= kx; k++)
	{
		if (table[k - start].r[pu_len - 1] == 1)
		{
			table[i - start].r[pu_len] = 1;
			break;
		}
	}
	if (table[i - start].r[pu_len] == 1)
	{
		//???????
		match[pu_len] = i;
		for (j = pu_len; j > 0; j--)
		{
			kn = match[j] - pu[j - 1].max - 1;
			kx = match[pu_len] - pu[j - 1].min - 1;
			if (kn < start)
				kn = start;
			//for (k = kn; k <= kx; k++)
			for (k=kx;k>=kn;k--)
			{
				if (table[k - start].r[j - 1] == 1 && k < match[j])
				{
					if(gap_ok(k, match[j])){//gap_ok(k, match[j])
						match[j-1]=k;
						break;
					} else {
						for (i=0;i<len;i++)
						{
							delete []table[i].r;
						}
						delete []table;
						return false;
					}
				}
			}
		}
		//match??
		for (i = 0; i < len; i++)
		{
			delete[]table[i].r;
		}
		delete[]table;
		for (j = 0; j <= pu_len; j++)
		{
			used[match[j]] = true;
		}
		return true;
	}
	else
	{
		for (i = 0; i < len; i++)
		{
			delete[]table[i].r;
		}
		delete[]table;
		return false;
	}
}
int display_oneoff(char *s, int max, int min)
{
	bool *used;
	int len_s = strlen(s);
	used = new bool[len_s];
	int i;
	for (i = 0; i < len_s; i++)
		used[i] = false;
	match = new int[pu_len + 1];
	int count = 0;
	for (i = min - 1; i < len_s; i++)
	{
		if (s[i] == pu[pu_len - 1].end)
		{
			bool result = getoptmatch(s, i, max, min, used, match);
			if (result == true)
			{
				count++;
				//display_a_match(match);
				if (match[0] == 955)
					count;
			}
		}
	}
	return count;
	//printf("The number of optimal matchess is : %d\n", count);
	delete[]match;
	delete[]used;

}
double matches(char *s, int end, int max, int min)
{
	struct row
	{
		int *r;
	};
	row *table;
	int start;
	start = end - max;
	if (start < 0)
		start = 0;
	int i, j, kn, kx, k;
	int len = end - start + 1;
	table = new row[len];
	for (i = 0; i < len; i++)
	{
		table[i].r = new int[pu_len + 1];
		for (j = 0; j <= pu_len; j++)
		{
			table[i].r[j] = 0;
		}
	}

	for (i = start; i < end; i++)
	{
		//????
		for (j = 0; j < pu_len; j++)
		{
			if (s[i] == pu[j].start)
			{
				if (j == 0)
				{
					table[i - start].r[j] = 1;
				}
				else
				{
					kn = i - pu[j - 1].max - 1;
					kx = i - pu[j - 1].min - 1;
					if (kn < start)
						kn = start;
					if (kx >= start)
					{
						for (k = kn; k <= kx; k++)
						{
							table[i - start].r[j] += table[k - start].r[j - 1];
						}
					}
				}
			}
		}
	}
	kn = i - pu[pu_len - 1].max - 1;
	kx = i - pu[pu_len - 1].min - 1;
	if (kn < start)
		kn = start;
	double value = 0;
	for (k = kn; k <= kx; k++)
	{
		value += table[k - start].r[pu_len - 1];
	}
	for (i = 0; i < len; i++)
	{
		delete[]table[i].r;
	}
	delete[]table;
	return value;
}
void calculate(char *s, int max, int min)
{
	int len_s = strlen(s);
	int i;
	double count = 0;
	for (i = min - 1; i < len_s; i++)
	{
		if (s[i] == pu[pu_len - 1].end)
		{
			count += matches(s, i, max, min);
		}
	}
	
	//printf("The number of all matches is : %lf\n\n", count);

}
int main()
{   
	
	readfile();
	printf("Please input gapstr:");
	scanf("%s",gapstr);
//	cout<<"input the minunity:";
//	cin>>minunity;
//	mymap['a'] = 2;
//	mymap['g'] = 3;
//	mymap['c'] = 2;
//	mymap['t'] = 3;
//	m_result = 0;
//	upminsup = ceil(minunity / 3);
	DWORD begintime = GetTickCount();
	time1 = begintime;
	min_freItem();   //cout frequent items and store item[]
	time2 = GetTickCount();
	//printf("len_1_Time cost:%ld\n",time2-time1);
	printf("len_1_Time cost:%ld\t候选数：%d\t频繁数：%d\n",time2-time1, hxms[0], pfms[0]);
	
	int f_level = 1;
	gen_candidate(f_level);	//生成了长度为2的候选模式	
	while (candidate.size() != 0)
	{
		int num = 0;

		for (int i = 0; i<candidate.size(); i++)
		{
			num = 0;
			occnum = 0; //the support num of pattern
						//int rest = 0;

			string p = candidate[i];
			hxms[f_level]++;
			ptn_len = p.size();
			compnum++;
			pu_len = 0;			
			for (int j = 0; j<ptn_len - 1; j++) {
				pu[j].start = p[j];
				pu[j].end = p[j + 1];
				pu[j].min = 0;
				pu[j].max = 20;
				if (pu[pu_len].max - pu[pu_len].min + 1 > maxp_c)
					maxp_c = pu[pu_len].max - pu[pu_len].min + 1;
				pu_len++;
			}
			//pu_len = p.size();
//			hupval = 0;
	//		for (int s = 0; s<ptn_len; s++)
	//		{
	//			hupval += mymap.find(p[s])->second;
	//		}

			//Creat_ptn(p, ptn_len);
			for (int t = 0; t < NumbS; t++)
			{
				//rest=minsup-occnum;
				if (strlen(sDB[t].S) > 0)
				{
					strcpy(S, sDB[t].S);
					if (ptn_len> strlen(S))
					{
						num = 0;
					}
					else {
						// p="AGCA";
						s_length = strlen(S);
						num= display_oneoff(S, m_max, m_min);
						//num += no_que(s_length, ptn_len);
						//no_que(s_length, ptn_len) ;

					}
				}

			}
			//link_pan.clear();
			occnum = num;
			if (occnum >= upminsup) {
				canArr[f_level].push_back(p);

		//		hupval = occnum*hupval / p.size();
		//		if (hupval >= minunity)
		//		{
				cout<<"匹配模式为："<<p<<endl;
				cout<<"支持度："<<occnum<<endl;
					freArr[f_level].push_back(p);

					frenum++;

					//	canArr[f_level].push_back(p);
					//cout <<p<<' ' ;
					//occnum = 0; 
					//break;
		//		}
					pfms[f_level]++;

			}
		}
		time1 = time2;
		time2 = GetTickCount();
		//printf("len_%d_Time cost:%ld\n", f_level+1, time2-time1);
		printf("len_%d_Time cost:%ld\t候选数：%d\t频繁数：%d\n", f_level+1, time2-time1, hxms[f_level], pfms[f_level]);
		f_level++;

		candidate.clear();
		gen_candidate(f_level);
	}
	//DWORD endtime = GetTickCount();
	DWORD endtime = time2;
	/*cout << endl;
	for (int i = 0; i<f_level; i++)
	{
		for (int j = 0; j<freArr[i].size(); j++)
		{
			cout << freArr[i][j] << "   ";
			//fout<<freArr[i][j]<<"   ";
			frenum++;
		}
		cout << endl;
		//fout<<endl;
	}*/

	//cout<<endl;
	//cout<<"The number of frequent patterns:"<<frequent.size()<<endl;
	cout << "The time-consuming:" << endtime - begintime << "ms. \n";
	//fout<<"The time-consuming:"<<endtime-begintime<<"ms. \n"<<endl;
	cout << "候选个数为：" << compnum << endl;
	cout << "频繁模式个数为：" << frenum << endl;
	// TODO: code your application's behavior here.
	//printf("Please input pattern at first:");
	//scanf("%s", m_pattern);
	//cin >> m_pattern;
	//printf("\n\nPlease input Minlen and Maxlen:\n");
	//scanf("%d%d", &m_min, &m_max);
	//cin >> m_min >> m_max;

//	int x;
//	cin >> x;
	return 0;
}


