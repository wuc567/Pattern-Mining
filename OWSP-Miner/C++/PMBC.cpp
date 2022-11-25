#include <map>
#include <set>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h>
#include <windows.h>
#include <stack>
#include <fstream>
using namespace std;
#define K 600   //The sequence number of sequence database
#define N 20000  //The length of sequence
#define M 1000   //The length of pattern
char S[N];  //sequence
int NumbS;

char gapstr[1000];
vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> candidate;
int minsup = 50;
int freNum=0;
int compnum=0;
vector <int> countNum;  //store frequent patterns

vector <int> tempUsed;

// 每个序列的字符以及使用标识
struct sequence
{
	char c;
	bool used;

};

// 生成的字符串二维矩阵 
struct seqdb                 
{
	int id;                  // sequence id
	char S[N];              // sequence
} sDB[K];

// 初始化单个序列 
void InitSequence(char s[],sequence seq[] ){
	int l=strlen(s);
	int i=0;
	while(i<l)
	{
		seq[i].c=s[i];
		seq[i].used=false;
		i++;
	}
}
// 读取文件，初始化二维矩阵 
void read_file()
{
	fstream file;
	//char filename[256];
	//cin>>filename;
	//cout <<filename<<endl;
	string buff;
	//file.open(filename,ios::in);   //open sequence file
	file.open("SDB1.txt",ios::in);   //open sequence file
	int i=0;

	strcpy(sDB[i].S, buff.c_str());
	while(getline(file, buff))
	{
		//strcpy(sDB[i].S, buff.c_str());
		strcat(sDB[0].S, buff.c_str());
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
	 for(int t = 0; t < NumbS; t++)
	 {
		strcpy(S,sDB[t].S);
		for(int i=0;i<strlen(S);i++)
		{
			if (((S[i]>='a'&&S[i]<='z')||(S[i]>='A'&&S[i]<='Z')) /*&& !gapContain(gapstr, S[i])*/)
			{
				mine=S[i];
				counter[mine]++;
			}			
		}	 
	 }
	 for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	 {
		 //(->first会得到key，->second会得到value。
		 if (the_iterator->second < minsup)
		 {
			map <string, int >::iterator tmp = the_iterator;
			++tmp;
			//局部删除某个元素
			counter.erase (the_iterator);
			the_iterator = tmp;
		 } 
		 else
		 {
			 cout<<the_iterator->first<<endl;
			 cout<<the_iterator->second<<endl;
			 freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			 ++the_iterator;
			 freNum++;
		 }
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

//根据上一级长度的匹配模式生成下一级所有可能出现的匹配模式存到candidate中（排列组合）
void gen_candidate(int level)
{
	
	int size = freArr[level-1].size();
	int start = 0;

	//注释王晓慧
	//cout <<"level:"<<level<<endl;
	for(int i=0;i<size;i++)
	{
		string Q="",R="";
		R = freArr[level-1][i].substr(1,level-1);  //suffix pattern of freArr[level-1][i]
		Q = freArr[level-1][start].substr(0,level-1);   //prefix pattern of freArr[level-1][start]
		//注释王晓慧
		//cout <<"RS:"<<freArr[level-1][i]<<endl;
		//cout <<"QS:"<<freArr[level-1][start]<<endl;
		//cout <<"R:"<<R<<endl;
		//cout <<"Q:"<<Q<<endl;
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

	//candidate遍历
	/*cout<<"candidate遍历开始"<<endl;
	for(vector<string>::iterator it = candidate.begin(); it!= candidate.end(); ++it ){
		cout<<*(it)<<endl;
	}
	cout<<"candidate遍历结束"<<endl;*/


}

//SS		母串
//pattern	子串
int getStore(char SS[], char pattern[]){
	int store = 0;
	int S_len = strlen(SS);//母串长度
	int P_len = strlen(pattern);//子串长度
	sequence  sq[N];
	InitSequence(SS,sq);// 用S初始化队列
	int occc[100];
	//return S_len + P_len;
	int ii = 0;
	for(int j = 0; j < P_len; j++)
	{
		bool gapstr_flag = true;

		int flag=-1;		
		while(ii < S_len)
		{		
			if(sq[ii].c==pattern[j]&&sq[ii].used==false)
			{
				if(j >= 1){
					
					for(int xh = occc[j - 1] + 1; xh < ii; xh++){
						gapstr_flag = false;
						for(int gi = 0; gi < strlen(gapstr); gi++){
							if(gapstr[gi] == sq[xh].c){
								gapstr_flag = true;
								break;
							}
						}
						if(gapstr_flag == false){
							break;
						}
					}
					if(gapstr_flag == false){
						//cout<<"哈哈哈哈哈哈哈"<<endl;
						ii = occc[0] + 1;
						j = -1;
						for(int h = 0; h < P_len; h++)
						{
							occc[h]=0;
						}
						while(tempUsed.size() > 0){
							sq[tempUsed.back()].used = false;
							tempUsed.pop_back();
						}
						break;
					}
				}

				flag=1;
				occc[j]=ii; //保存当前未使用字符的位置 
				sq[ii].used=true;
				tempUsed.push_back(ii);
				break;
			}
		
			ii++;
		}//while
		if(gapstr_flag == false)
			continue;
	
		if(j==P_len - 1 && ii < S_len)
		{
			tempUsed.clear();
			ii=occc[0]; //你把指针i给重新赋值了，导致了错误 
			//cout<<"<";
			for(int h=0;h<P_len;h++)
			{
				//cout<<occc[h]+1<<",";
				occc[h]=0;
			}
			//cout<<">"<<endl;
			j =-1;
		    store++;
		}

		if(flag==1)
		{
			ii++;
		}
		
		if(ii >= S_len)
		{
			break;
		}
	}///for
	//cout<<store<<endl; 
	return store;
}
	
int main()
{
	
	//int n=11,m=3;
	read_file();
    int num;
	num=0;
	int i=0;
	sequence  seq[N];
//	char s[N]="aabb";
	strcpy(S,sDB[0].S);	// 把二维矩阵的第一行赋值给S 
	//InitSequence(S,seq);// 用S初始化队列 
	char p[M]="catg"; //子串是"cat" 
	int n=strlen(S); // 获取母串S的长度 
	int m=strlen(p);//获取子串P的长度 
	//int occ[100];

	//cout<<"store="<<getStore(S, p)<<endl;

	
	cout<<"input the gapstr:"<<endl;
	cin>>gapstr;


	//GetTickCount是一种函数。GetTickCount返回（retrieve）从操作系统启动所经过（elapsed）的毫秒数，它的返回值是DWORD
	DWORD begintime=GetTickCount();

	//对结果的第一个数组进行初始化
	min_freItem();
	int f_level=1;
	gen_candidate(f_level);
	//cout<<candidate.size()<<endl;

	while(candidate.size() != 0){
		int numm = 0;

		for(int ai=0; ai < candidate.size(); ai++)
		{
			int h_occnum = 0; //the support num of pattern
			int h_rest = 0;
			
			string patt = candidate[ai];
			char pattc[10000];
			strcpy(pattc, patt.c_str());
			compnum++;

			h_occnum += getStore(S, pattc);
			if(h_occnum >= minsup){
				freArr[f_level].push_back(patt);
				countNum.push_back(h_occnum);
				cout<<"计算模式 "<<patt<<endl;
				cout<<"支持度 "<<h_occnum<<endl;
				freNum++;
			}

			/*for(int t = 0; t < NumbS; t++)
			{
				rest=minsup-occnum;
				if(strlen(sDB[t].S) > 0)
				{
					strcpy(S,sDB[t].S);
					occnum += netGap(p,rest);
				}
				if(occnum >= minsup)
				{
					freArr[f_level].push_back(p);
					break;
				}
			}*/
		}
	f_level++;
		candidate.clear();
		gen_candidate(f_level);

		/*if(f_level == 7){ 
			break;
		}*/
	
	
	}

	//getStore(S, p);
	 cout<<"The number of frequent patterns:"<<freNum<<endl;
 //   fout<<"匹配到个数为："<<num_occur<<endl;
    cout <<"The number of calculation:"<<compnum<<" \n";
	//cout<<"总数："<<freNum<<endl;
	DWORD endtime=GetTickCount();
  
	cout <<"The time-consuming:"<<endtime-begintime<<"ms. \n";
	return 0;
}
