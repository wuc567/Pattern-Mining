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
#include <iomanip>
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
int freNum=0;
int compnum=0;
DWORD time1;
DWORD time2;
int hxms[1000];//��ѡģʽ
int pfms[1000];//Ƶ��ģʽ
//Vector �����P.name
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
//�ж��Ƿ�������ͨ��
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


//����S ��Ӧ��p�е�queue�����S[i]
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
		if (/*postion==0&&*/S[k]==link_pan[0].name && bool_S[k]==true){
			link_pan[0].que_pan.push(k);
		}
		for (int m = 1;m < pattern_len;m++)//
		{
			int len_aa = link_pan[m-1].que_pan.size();
			int len_bb = link_pan[m].que_pan.size();
			int flagaa = 0;
			for(int ia = 0; ia < len_aa; ia++){
				if(ia == len_bb){
					flagaa = link_pan[m-1].que_pan.front();
				}
				//cout << link_pan[m-1].que_pan.front() << endl;
				link_pan[m-1].que_pan.push(link_pan[m-1].que_pan.front());
				link_pan[m-1].que_pan.pop();
				
			}
			if (S[k]==link_pan[m].name && bool_S[k]==true && link_pan[m].que_pan.size()<link_pan[m-1].que_pan.size() && k > flagaa)
			{
				

				//��ʱ���У�����ɾ����һ�����м�ڵ�
				queue<int> temp_pan;
				//��һ���д�С
				int lqueSize = link_pan[m-1].que_pan.size();
				
				//��ǰ���д�С
				int queSize = link_pan[m].que_pan.size();
				bool gapstr_flag = true;
				bool forover = false;
				for(int z = 0; z < lqueSize; z++){

					if(z >= queSize){
						if(forover == false){
							//������ͨ���ж�
							gapstr_flag = gap_ok(link_pan[m-1].que_pan.front(), k);
							if(gapstr_flag == true){//����
								temp_pan.push(link_pan[m-1].que_pan.front());
								link_pan[m-1].que_pan.pop();
								forover = true;
								//break;

							} else {//������
								link_pan[m-1].que_pan.pop();

								int currLevel = m-2;//��ǰ���в㼶
								if(currLevel >= 0){
									//ɾ����ǰ���������еĽڵ�
									for(int hij = currLevel; hij >=0; hij--){
										queue<int> temp_q;
										int curr_q_size = link_pan[hij].que_pan.size();//��ǰ���д�С
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
		

					} else {//�ڵ�ǰ�ĸ���
						temp_pan.push(link_pan[m-1].que_pan.front());
						link_pan[m-1].que_pan.pop();
					}
					
				}

				//��ȡ�µ���һ�ڵ�
				link_pan[m-1].que_pan = temp_pan;


				int len_aa2 = link_pan[m-1].que_pan.size();
				int len_bb2 = link_pan[m].que_pan.size();
				int flagaa2 = 0;
				for(int ia2 = 0; ia2 < len_aa2; ia2++){
					if(ia2 == len_bb2){
						flagaa2 = link_pan[m-1].que_pan.front();
					}
					//cout << link_pan[m-1].que_pan.front() << endl;
					link_pan[m-1].que_pan.push(link_pan[m-1].que_pan.front());
					link_pan[m-1].que_pan.pop();
				
				}
				if(forover == true && k > flagaa2){
					link_pan[m].que_pan.push(k);
					postion = m;
					
					//break;
				} else {
					postion = m - 1;
					//break;
				}
				
			}
			
		}
		
		//�����������
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

			//�������
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

//��ȡĳ��ģʽ��֧�ֶ�
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
		//printf("����%c", *p_gapstr);
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
	 for (map <string,int >::iterator the_iterator = counter.begin (); the_iterator!= counter.end (); )
	 {
		 hxms[0]++;
		 //(->first��õ�key��->second��õ�value��
		 if (the_iterator->second < minsup)
		 {
			map <string, int >::iterator tmp = the_iterator;
			++tmp;
			//�ֲ�ɾ��ĳ��Ԫ��
			counter.erase (the_iterator);
			the_iterator = tmp;
		 } 
		 else
		 {
			 freArr[0].push_back(the_iterator->first);  //add to freArr[0]
			 cout<<"����ģʽ��"<<the_iterator->first<<endl;
			 cout<<the_iterator->second<<endl;
			 num_occur += the_iterator->second;
			 ++the_iterator;
			 freNum++;
			 pfms[0]++;
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


//������һ�����ȵ�ƥ��ģʽ������һ�����п��ܳ��ֵ�ƥ��ģʽ�浽candidate�У�������ϣ�
void gen_candidate(int level)
{
	
	int size = freArr[level-1].size();
	int start = 0;

	//ע��
	//cout <<"level:"<<level<<endl;
	for(int i=0;i<size;i++)
	{
		string Q="",R="";
		R = freArr[level-1][i].substr(1,level-1);  //suffix pattern of freArr[level-1][i]
		Q = freArr[level-1][start].substr(0,level-1);   //prefix pattern of freArr[level-1][start]
		//ע��
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

	//candidate����
	/*cout<<"candidate������ʼ"<<endl;
	for(vector<string>::iterator it = candidate.begin(); it!= candidate.end(); ++it ){
		cout<<*(it)<<endl;
	}
	cout<<"candidate��������"<<endl;*/


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
	//�Խ���ĵ�һ��������г�ʼ��
	time1 = dwBeginTime;
	min_freItem();
	time2 = GetTickCount();
	//printf("len_1_Time cost:%ld\n",time2-time1);
	printf("len_1_Time cost:%ld\t��ѡ����%d\tƵ������%d\n",time2-time1, hxms[0], pfms[0]);

	int f_level=1;
	gen_candidate(f_level);
	//cout<<candidate.size()<<endl;

	while(candidate.size() != 0){
		//cout<<"������"<<endl;
		int numm = 0;

		for(int ai=0; ai < candidate.size(); ai++)
		{
			int h_occnum = 0; //the support num of pattern
			int h_rest = 0;
			
			string patt = candidate[ai];
			cout<<"����ģʽ��"<<patt<<endl;
			hxms[f_level]++;
			char pattc[10000];
			strcpy(pattc, patt.c_str());
			compnum++;

			h_occnum += getStore(/*S,*/ pattc);
			
			if(h_occnum >= minsup){
				freArr[f_level].push_back(patt);
				countNum.push_back(h_occnum);
				//cout<<patt<<endl;
				cout<<"֧�ֶȣ�"<<h_occnum<<endl;
				freNum++;
				pfms[f_level]++;
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
		time1 = time2;
		time2 = GetTickCount();
		//printf("len_%d_Time cost:%ld\n", f_level+1, time2-time1);
		printf("len_%d_Time cost:%ld\t��ѡ����%d\tƵ������%d\n", f_level+1, time2-time1, hxms[f_level], pfms[f_level]);
		f_level++;
		candidate.clear();
		gen_candidate(f_level);

		/*if(f_level == 7){ 
			break;
		}*/
	
	}

	
	//init_bool();
	//show_bool();		
	
	//no_que(S_len,pattern_len);   
    
	
	
	//cout<<"ƥ�䵽����Ϊ��"<<num_occur<<endl;
    cout<<"The number of frequent patterns:"<<freNum<<endl;
 //   fout<<"ƥ�䵽����Ϊ��"<<num_occur<<endl;
    cout <<"The number of calculation:"<<compnum<<" \n";
	//DWORD dwEndTime=GetTickCount();
	DWORD dwEndTime = time2;
	//printf("ƥ�䵽����Ϊ��%d\n",num_occur);
	cout<<"Time cost:"<<dwEndTime-dwBeginTime<<endl;		
	system("pause");	
	fout.close();
	return 0;
}