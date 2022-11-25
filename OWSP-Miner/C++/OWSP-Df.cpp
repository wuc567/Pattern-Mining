#include <map>
#include <set>
#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <windows.h>
#include<stdio.h>
#include<string.h>
# include <stdlib.h> 
#include <fstream>
#include<time.h>
#include<math.h>
using namespace std;
#define M 100   //The length of pattern
#define N 20000  //The length of sequence
typedef char Elemtype;
char S[N];  //sequence
int num_occur;
int pattern_len;
int S_len;
static int num=0;
bool bool_S[N]={true};
bool bool_p[N]={false};
bool bool_b[N]={false};
struct pant_p         //nettree node
{
	char name;     //The corresponding position of node in sequence
	queue<int> que_pan;
};
vector <pant_p> link_pan;
ofstream fout("demo1.txt", ios::binary);

char gapstr[1000];


vector <string> *freArr = new vector <string>[M];  //store frequent patterns
vector <string> candidate;
vector <int> countNum;  //store frequent patterns
int minsup = 10;
int freNum = 0;
int compnum = 0;
string item[30];   // event set
map <string, int> frequent;  //frequent pattern and its support
int nn = 0;   //The number of types of events
//Vector 中填充P.name
void Creat_ptn(char *p,int len_p){
	//cout<<"link_pan.size()"<<link_pan.size()<<endl;
	//cout<<"len_p"<<len_p<<endl;
	link_pan.clear();
	for(int i =0;i<len_p;i++){
		pant_p pan;
		memset(&pan,0,sizeof(pan));
		pan.name=p[i];
		link_pan.push_back(pan);
	}
	//cout<<"link_pan.size()"<<link_pan.size()<<endl;
	//cout<<link_pan[0].name;
	//cout<<link_pan[1].name;
	//cout<<link_pan[2].name;
	//cout<<link_pan[3].name;

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


//根据S 对应的p中的queue中填充S[i]
int no_que(int len_s,int len_p){
	

	int myAmount = 0;
	//cout<<"S_len:"<<S_len<<endl;
	//cout<<"pattern_len:"<<pattern_len<<endl;
	//cout<<"len_s:"<<len_s<<endl;
	//cout<<"len_p:"<<len_p<<endl;
	//cout<<link_pan[0].name<<endl;
	//cout<<link_pan[1].name<<endl;
	for (int k=0; k < S_len; k++)
	{
		//cout<<"S[k]:"<<S[k]<<endl;
		
		//cout<<"bool_S[k]:"<<bool_S[k]<<endl;
		int postion = 0;
		for (int m = pattern_len-1;m>0;m--)//
		{
			if (S[k]==link_pan[m].name && bool_S[k]==true && link_pan[m].que_pan.size()<link_pan[m-1].que_pan.size())
			{
				

				//临时队列，用于删除上一队列中间节点
				queue<int> temp_pan;
				//上一队列大小
				int lqueSize = link_pan[m-1].que_pan.size();
				
				//当前队列大小
				int queSize = link_pan[m].que_pan.size();
				bool gapstr_flag = true;
				bool forover = false;
				for(int z = 0; z < lqueSize; z++){

					if(z >= queSize){
						if(forover == false){
							//进行弱通配判断
							gapstr_flag = gap_ok(link_pan[m-1].que_pan.front(), k);
							if(gapstr_flag == true){//满足
								temp_pan.push(link_pan[m-1].que_pan.front());
								link_pan[m-1].que_pan.pop();
								forover = true;
								//break;

							} else {//不满足
								link_pan[m-1].que_pan.pop();

								int currLevel = m-2;//当前队列层级
								if(currLevel >= 0){
									//删除当前列下面所有的节点
									for(int hij = currLevel; hij >=0; hij--){
										queue<int> temp_q;
										int curr_q_size = link_pan[hij].que_pan.size();//当前队列大小
										for(int ci = 0; ci < curr_q_size; ci++){
											if(ci == queSize){
												link_pan[hij].que_pan.pop();
											} else {
												temp_q.push(link_pan[hij].que_pan.front());
												link_pan[hij].que_pan.pop();
											}
										}
										link_pan[hij].que_pan = temp_q;
									}
								}
							}
						} else {
							temp_pan.push(link_pan[m-1].que_pan.front());
							link_pan[m-1].que_pan.pop();
						}
		

					} else {//节点前的复制
						temp_pan.push(link_pan[m-1].que_pan.front());
						link_pan[m-1].que_pan.pop();
					}
					
				}

				//获取新的上一节点
				link_pan[m-1].que_pan = temp_pan;

				if(forover == true){
					link_pan[m].que_pan.push(k);
					postion = m;
					
					//break;
				} else {
					postion = m - 1;
					//break;
				}
				
			}
			
		}
		if (/*postion==0&&*/S[k]==link_pan[0].name && bool_S[k]==true){
			link_pan[0].que_pan.push(k);
		}
		
		if (link_pan[link_pan.size()-1].que_pan.size()>0){
			

			//cout<<"<";

			fout<<"<  "<<endl;

			for(int w=0;w<link_pan.size();w++){
				//cout<<"  "<<link_pan[w].que_pan.front()+1;
				//cout<<S[link_pan[w].que_pan.front()];
				bool_S[link_pan[w].que_pan.front()]=false;

				fout<<link_pan[w].que_pan.front()+1<<endl;
				fout<<"  "<<endl;

				link_pan[w].que_pan.pop();
				
			}

			//cout<<">";
			fout<<"> "<<endl;
			fout<<"\r"<<endl;
			num_occur++;
			myAmount++;
			//cout<<endl;

			//队列清空
			if(link_pan[0].que_pan.size() > 0){
				k = link_pan[0].que_pan.front() - 1;
				for(int hxn = 0; hxn < link_pan.size(); hxn++){
					queue<int> no_pan;
					link_pan[hxn].que_pan = no_pan;
					
				}
			}
			
			//num_occur++;
			
		}
	}
	for(int hxn = 0; hxn < link_pan.size(); hxn++){
		queue<int> no_pan;
		link_pan[hxn].que_pan = no_pan;			
	}

	return myAmount;

}


void init_bool()
{
	for (int i=0;i<S_len;i++)
	{
		bool_S[i]=true;
	}
}
void read_file()
{
	FILE *ss;
	int k=0;
	char ch;	
	ss=fopen("SDB1.txt","rt");   
	ch=fgetc(ss);
	while(ch!=EOF)
	{
		S[k]=ch;
		ch=fgetc(ss);
		k++;
	}
}

//获取某个模式的支持度
int getStore(char pattern[]){
	int store = 0;
	
	pattern_len = strlen(pattern);
	S_len=strlen(S);
	//char p[M]="agct";
	init_bool();
	Creat_ptn(pattern, pattern_len);
	
	store = no_que(S_len, pattern_len);
	//cout<<"store:"<<store<<endl;
	return store;

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
	 map <string, int> counter;
	 string mine;
	 for(int t = 0; t < 1; t++)
	 {
		//strcpy(S,sDB[t].S);
		for(int i=0;i<strlen(S);i++)
		{
			if (((S[i]>='a'&&S[i]<='z')||(S[i]>='A'&&S[i]<='Z')) && !gapContain(gapstr, S[i]))
			{
				mine=S[i];
				counter[mine]++;
			}			
		}	 
	 }
	 nn = 0;
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
			 //freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			 //cout<<"计算模式："<<the_iterator->first<<endl;
			 //cout<<the_iterator->second<<endl;
			 //num_occur += the_iterator->second;
			 item[nn++] = the_iterator->first.at(0);
			 ++the_iterator;
			 //freNum++;
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

void mineFre(string p,int num)
{
	frequent[p] = num;  //add to frequent array
	for(int e = 0; e < nn; e++)
	{
		string q = p + item[e];
		compnum++;
		num = 0;
		int rest=0;
		for(int t = 0; t < 1; t++)
		{
			rest=minsup-num;
			if(strlen(S) > 0)
			{
				//strcpy(S,sDB[t].S);
				char p_c[10000];
				strcpy(p_c, q.c_str());
				cout<<"模式："<<q<<endl;
				num += getStore(/*S,*/ p_c);
				cout<<num<<endl;
				if(num>=minsup){
					freNum++;
				}
			}
			if (num>=minsup)
				break;
		}
		if (num>=minsup)
			mineFre(q,num);	

	}
}

int main()
{
    //int i;
	read_file();
	cout<<S<<endl;


	cout<<"please input gapstr:"<<endl;
	cin>>gapstr;
	cout<<gapstr<<endl;
	cout<<strlen(gapstr)<<endl;

   	DWORD dwBeginTime=GetTickCount();
	//对结果的第一个数组进行初始化
	min_freItem();
	//int f_level=1;
	//gen_candidate(f_level);
	//cout<<candidate.size()<<endl;
	for(int e = 0; e < nn; e++){
		
		string patt = item[e];
		cout<<"计算模式："<<patt<<endl;
		char pattc[10000];
		strcpy(pattc, patt.c_str());
		compnum++;
		int num = 0;


		num += getStore(/*S,*/ pattc);
		
		if(num >= minsup){
			//freArr[f_level].push_back(patt);
			//countNum.push_back(h_occnum);
			//cout<<patt<<endl;
			cout<<num<<endl;
			freNum++;
		}
		mineFre(patt,num);
	}



	
	//init_bool();
	//show_bool();		
	
	//no_que(S_len,pattern_len);   
    
	
	
	//cout<<"匹配到个数为："<<num_occur<<endl;
	
	cout<<"模式个数为："<<compnum<<endl;
    cout<<"频繁模式个数为："<<freNum<<endl;
 //   fout<<"匹配到个数为："<<num_occur<<endl;

	DWORD dwEndTime=GetTickCount();
	//printf("匹配到个数为：%d\n",num_occur);
	cout<<"Time cost:"<<dwEndTime-dwBeginTime<<endl;	
	system("pause");	
	fout.close();
	return 0;
}
