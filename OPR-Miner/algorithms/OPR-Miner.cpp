#pragma warning(disable:4996) 
#include <stdio.h>
#include <string.h>
#include <string>
#include <stdint.h>
#include <time.h>
#include <stdlib.h>
#include <malloc.h>
#include <windows.h>
#include <vector>
#include <iostream>
#include <fstream>
using namespace std;


int rulenum = 0;  //规则数量
vector<int> rule_left;//规则前件
vector<int> rule_right;//规则后件
int rule_leftnum;//规则前件支持度
int rule_rightnum;//规则后件支持度


int allrulenum = 0;



ofstream ofile;
int minsup = 25;
//int minsup = 2;
//int minsup =1;
//int minsup = 5;
//int minsup = 6;
//int minsup = 7;
//int minsup = 10;
//int minsup = 100;
//int minsup = 15;
//int minsup = 20;
//int minsup = 22;
//int minsup = 25;
//int minsup = 30;
//int minsup = 40;
//int minsup = 50;
//int minsup = 75;
//int minsup = 100;
//int minsup = 150;
//int minsup = 200;
//int minsup = 250;
//int minsup = 300;


//float minconf = 0.05;
//float minconf = 0.1;//置信度阈值
//float minconf = 0.15;
//float minconf = 0.2;//置信度阈值
//float minconf = 0.25;
//float minconf = 0.3;//置信度阈值
//float minconf = 0.35;
//float minconf = 0.4;//置信度阈值
//float minconf = 0.7;
//float minconf = 0.5;//置信度阈值
//float minconf = 0.6;//置信度阈值
//float minconf = 0.7;//置信度阈值
float minconf = 0.7;//置信度阈值
//float minconf = 0.9;//置信度阈值
//float minconf = 1;//置信度阈值



int frequent_num = 0;  //总的频繁模式数量
int fre_num = 0;
int cd_num = 2; //候选模式数量



vector<vector<int>> P;  //存放末位的数组
vector<vector<int>> L;  //存放每次生成的频繁模式
vector<int> Z;  //存放本次生成的末位数组
vector<int> Z2;

vector<int> Cd;  //存放本次生成的模式
vector<int> Cd2;

int read_file();
void find();

void judge_fre(int sup_num, vector<int> Cd, vector<int> Z);
void recommend(int sup_begin, float sup_end, vector<int> Cd_begin, vector<int> Cd_end);

vector<float> S;              // sequence

typedef struct LNode {
	int data;
	struct LNode* next;
} LNode;

int* sort(vector<int> src) {
	int k, slen = 0, y = 0;
	int level = 1;
	int* sort_array;

	slen = src.size();
	sort_array = (int*)malloc(slen * sizeof(int));
	for (int i = 0; i < slen; i++)
	{
		k = src[i];
		for (int x = 0; x < slen; x++)
		{
			if (k > src[x])
			{
				level++;
			}
		}
		sort_array[i] = level;
		level = 1;
	}
	y, slen = 0;
	return sort_array;
}

uint32_t grow_BaseP1(LNode* Ld, LNode* L)
{
	LNode* p = L;
	LNode* q = Ld;
	Z.clear();

	while (p->next != NULL && q->next != NULL)
	{
		if (q->next->data == p->next->data + 1)
		{
			Z.push_back(q->next->data);
			p->next = p->next->next;
			q->next = q->next->next;
		}
		else if (p->next->data < q->next->data)
		{
			p = p->next;
		}
		else
		{
			q = q->next;
		}
	}
	L->data = L->data - Z.size();
	Ld->data = Ld->data - Z.size();
	judge_fre(Z.size(), Cd, Z);
	return 0;
}

uint32_t grow_BaseP2(int slen, LNode* Ld, LNode* L)
{
	int lst, fri;
	LNode* p = L;
	LNode* q = Ld;
	Z.clear();
	Z2.clear();
	while (p->next != NULL && q->next != NULL)
	{
		if (q->next->data == p->next->data + 1)
		{
			lst = q->next->data;
			fri = lst - slen;
			if (S[lst] > S[fri])
			{
				Z.push_back(q->next->data);
			}
			else if (S[lst] != S[fri])
			{
				Z2.push_back(q->next->data);
			}
			p->next = p->next->next;
			q->next = q->next->next;
		}
		else if (p->next->data < q->next->data)
		{
			p = p->next;
		}
		else
		{
			q = q->next;
		}
	}
	L->data = L->data - Z.size() - Z2.size();
	Ld->data = Ld->data - Z.size() - Z2.size();
	judge_fre(Z.size(), Cd, Z);
	judge_fre(Z2.size(), Cd2, Z2);
	return 0;
}


uint32_t generate_fre()   //模式融合
{
	int slen = 0;

	vector<int> Q;
	vector<int> R;
	vector<vector<int>> pos;
	vector<vector<int>> fre;
	vector<LNode*> Lb;

	int* q;
	int* r;
	int j = 0;
	int fre_number = 0;
	int t = 0;
	int k = 0;

	slen = L[0].size();//模式长度

	fre = L;
	L.clear();
	fre_number = fre_num;
	fre_num = 0;

	pos = P;
	P.clear();

	Lb.resize(fre_number);

	Cd.resize(slen + 1);
	Cd2.resize(slen + 1);


	for (int s = 0; s < fre_number; s++)
	{
		LNode* pb, * qb;
		Lb[s] = (LNode*)malloc(sizeof(LNode));
		Lb[s]->data = pos[s].size();
		qb = Lb[s];
		for (int d = 0; d < pos[s].size(); d++)
		{
			pb = (LNode*)malloc(sizeof(LNode));
			pb->data = pos[s][d];
			qb->next = pb;
			qb = pb;
		}
		qb->next = NULL;
	}

	for (int i = 0; i < fre_number; i++)
	{
		Q.assign(fre[i].begin() + 1, fre[i].end());//求后缀
		q = sort(Q);
		//创建链表
		LNode* L;
		LNode* p, * s;
		int size = pos[i].size();

		rule_left = fre[i];
		rule_leftnum = size;

		L = (LNode*)malloc(sizeof(LNode));
		L->data = size;
		s = L;
		for (k = 0; k < size; k++)
		{
			p = (LNode*)malloc(sizeof(LNode));
			p->data = pos[i][k];
			s->next = p;
			s = p;
		}
		s->next = NULL;

		for (int j = 0; j < fre_number; j++)
		{
			if (L->data >= minsup && Lb[j]->data >= minsup)
			{
				R = fre[j];
				R.pop_back();   //求前缀
				r = sort(R);
				if (memcmp(q, r, (slen - 1) * sizeof(int)))
				{
					;//printf("排名不一样\n");		
				}
				else
				{
					//	vector <int> postion;
					//	postion = pos[j];
						//printf("排名一样\n");
					if (fre[i][0] == fre[j][slen - 1])	           //最前最后位置相等，拼接成两个模式			
					{
						//Flag[j] = 0;
						Cd[0] = fre[i][0];
						Cd2[0] = fre[i][0] + 1;
						Cd[slen] = fre[i][0] + 1;
						Cd2[slen] = fre[i][0];
						for (int t = 1; t < slen; t++)
						{
							if (fre[i][t] > fre[j][slen - 1])
							{
								//中间位置增长
								Cd[t] = fre[i][t] + 1;
								Cd2[t] = fre[i][t] + 1;
							}
							else
							{
								Cd[t] = fre[i][t];
								Cd2[t] = fre[i][t];
							}
						}
						//printf("%d+%d=%d,%d\n", fre[i][0], fre[j][0], Cd[0], Cd2[0]);
						//if (Lb[j]->data >= minsup)
						cd_num = cd_num + 2;
						//	read_num = read_num + 1;
						grow_BaseP2(Cd.size() - 1, Lb[j], L);

					}
					else if (fre[i][0] < fre[j][slen - 1])    //第一个位置比最后一个位置小
					{
						Cd[0] = fre[i][0];              //小的不变
						Cd[slen] = fre[j][slen - 1] + 1;  //大的加一

						for (int t = 1; t < slen; t++)
						{
							if (fre[i][t] > fre[j][slen - 1])
							{
								//fre[i][t]+=1;   //中间位置增长
								Cd[t] = fre[i][t] + 1;

							}
							else
							{
								Cd[t] = fre[i][t];
							}
						}
						cd_num = cd_num + 1;
						grow_BaseP1(Lb[j], L);
					}
					else {
						Cd[0] = fre[i][0] + 1;              //大的加一
						Cd[slen] = fre[j][slen - 1];       //小的不变
						for (int t = 0; t < slen - 1; t++)
						{
							if (fre[j][t] > fre[i][0])
							{
								Cd[t + 1] = fre[j][t] + 1;   //中间位置增长

							}
							else
							{
								Cd[t + 1] = fre[j][t];
							}
						}
						cd_num = cd_num + 1;
						grow_BaseP1(Lb[j], L);
					}
				}
			}	
		}
	}
	Lb.clear();
	pos.clear();
	fre.clear();
	return 0;
}


void recommend(int sup_begin, float sup_end, vector<int> Cd_begin, vector<int> Cd_end)  //规则推荐
{
	if (sup_end >= sup_begin * minconf )
	{
		
		printf("模式");
		for (vector<int>::iterator it = Cd_begin.begin(); it != Cd_begin.end(); it++)
		{
			printf("%d", *it);
			ofile << *it << ",";
		}

		printf("=>");
		ofile << " ";
		for (vector<int>::iterator it = Cd_end.begin(); it != Cd_end.end(); it++)
		{
			printf("%d", *it);
			ofile << *it << ",";
		}
		printf("置信度为：%f", sup_end / sup_begin);
		printf("\n");
		ofile << sup_end / sup_begin ;
		ofile << endl;
	
		rulenum++;
	}
	
}

void judge_fre(int sup_num, vector<int> Cd, vector<int> Z)  //频繁模式挖掘
{
	if (sup_num >= minsup)
	{
		P.push_back(Z);
		L.push_back(Cd);
		
		printf("频繁模式：");
		for (vector<int>::iterator it = Cd.begin(); it != Cd.end(); it++)
		{
			printf("%d,", *it);
		}
		printf("支持度为：%d\n", sup_num);

		/*
		printf("在字符串中出现的位置：");
		for (vector<int>::iterator it = Z.begin(); it != Z.end(); it++)
		{
			printf("%d,", *it);
		}
		printf("\n\n");
		
	*/	
		rule_right = Cd;
		rule_rightnum = sup_num;
		recommend(rule_leftnum, rule_rightnum, rule_left, rule_right);

		allrulenum++;

		frequent_num++;
		fre_num++;
	}

}
void judge_fre2(int sup_num, vector<int> Cd, vector<int> Z)//频繁模式挖掘
{
	if (sup_num >= minsup)
	{
		P.push_back(Z);
		L.push_back(Cd);
		
		printf("频繁模式：");
		for (vector<int>::iterator it = Cd.begin(); it != Cd.end(); it++)
		{
			printf("%d,", *it);
		}
		printf("支持度为：%d\n", sup_num);

		/*
		printf("在字符串中出现的位置：");
		for (vector<int>::iterator it = Z.begin(); it != Z.end(); it++)
		{
			printf("%d,", *it);
		}
		printf("\n\n");
	*/	

		frequent_num++;
		fre_num++;
	}
}

void find()
{
	int i = 0, j = 1;
	Cd.push_back(1);
	Cd.push_back(2);
	Cd2.push_back(2);
	Cd2.push_back(1);
	while (j < S.size())
	{
		if (S[j] > S[i])   //12模式
		{
			Z.push_back(j);

		}
		else if (S[j] != S[i])                //21模式
		{

			Z2.push_back(j);
		}
		i++;
		j++;
	}
	judge_fre2(Z.size(), Cd, Z);
	Cd.clear();
	judge_fre2(Z2.size(), Cd2, Z2);
	Cd2.clear();
}

int read_file()
{
	int i = 0;
	float num;

	//char filename[] = "..\\dataset\\Italian-tem.txt";//SDB1
	//char filename[] = "..\\dataset\\Italian-temperature.txt";//SDB2
	//char filename[] = "..\\dataset\\Italian-temperature2.txt";//SDB2
	//char filename[] = "..\\dataset\\1WTl-2.txt";//SDB3
	//char filename[] = "..\\dataset\\Crude Oil.txt";//SDB4
	//char filename[] = "..\\dataset\\random2.txt";
   //char filename[] = "..\\dataset\\股票Russell2000（1987.9.10~2019.12.27）2.txt";//SDB5
	char filename[] = "..\\dataset\\股票Nas（1971.3.1~2019.10.31）.txt";//SDB6
	//char filename[] = "..\\dataset\\Nas2.txt";//SDB6
	//char filename[] = "..\\dataset\\股票sp500（1928.2.1~2019.10.31）.txt";//SDB7
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan.txt";//SDB8
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_5000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_10000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_15000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_20000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_25000.txt";
	//char filename[] = "..\\dataset\\论文.txt";
	//char filename[] = "..\\dataset\\论文2.txt";
	//char filename[] = "..\\dataset\\论文3.txt";
	//char filename[] = "..\\dataset\\random2.txt";
	//char filename[] = "..\\dataset\\李超然温度.txt";
	//char filename[] = "..\\dataset\\wuc\\1.txt";
	//char filename[] = "..\\dataset\\wuc\\2.txt";
	//char filename[] = "..\\dataset\\wuc\\3.txt";
	//char filename[] = "..\\dataset\\wuc\\4.txt";
	//char filename[] = "..\\dataset\\wuc\\5.txt";
	//char filename[] = "..\\dataset\\wuc\\6.txt";
	//char filename[] = "..\\dataset\\wuc\\7.txt";
	//char filename[] = "..\\dataset\\wuc\\8.txt";
	//char filename[] = "..\\dataset\\wuc\\9.txt";
	//char filename[] = "..\\dataset\\wuc\\10.txt";
	//char filename[] = "..\\dataset\\wuc\\11.txt";
	//char filename[] = "..\\dataset\\wuc\\12.txt";
	//char filename[] = "..\\dataset\\wuc\\13.txt";
	//char filename[] = "..\\dataset\\wuc\\14.txt";
	//char filename[] = "..\\dataset\\wuc\\15.txt";
	//char filename[] = "..\\dataset\\wuc\\16.txt";
	//char filename[] = "..\\dataset\\wuc\\17.txt";
	//char filename[] = "..\\dataset\\wuc\\18.txt";
	//char filename[] = "..\\dataset\\wuc\\19.txt";
	//char filename[] = "..\\dataset\\wuc\\20.txt";
	//char filename[] = "..\\dataset\\wuc\\21.txt";
	//char filename[] = "..\\dataset\\wuc\\22.txt";
	//char filename[] = "..\\dataset\\wuc\\23.txt";
	//char filename[] = "..\\dataset\\wuc\\24.txt";
	//char filename[] = "..\\dataset\\wuc\\25.txt";
	//char filename[] = "..\\dataset\\wuc\\26.txt";
	//char filename[] = "..\\dataset\\wuc\\27.txt";
	//char filename[] = "..\\dataset\\wuc\\28.txt";
	//char filename[] = "..\\dataset\\wuc\\29.txt";
	//char filename[] = "..\\dataset\\wuc\\30.txt";
	//char filename[] = "..\\dataset\\wuc\\31.txt";
	//char filename[] = "..\\dataset\\wuc\\32.txt";
	//char filename[] = "..\\dataset\\wuc\\33.txt";
	//char filename[] = "..\\dataset\\wuc\\34.txt";
	//char filename[] = "..\\dataset\\wuc\\35.txt";
	//char filename[] = "..\\dataset\\wuc\\36.txt";
	//char filename[] = "..\\dataset\\wuc\\37.txt";
	//char filename[] = "..\\dataset\\wuc\\38.txt";
	//char filename[] = "..\\dataset\\wuc\\39.txt";
	//char filename[] = "..\\dataset\\wuc\\40.txt";
	//char filename[] = "..\\dataset\\wuc\\41.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\1.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\2.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\3.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\4.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\5.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\6.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\7.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\8.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\9.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\10.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\11.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\12.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\13.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\14.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\15.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\1.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\2.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\3.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\4.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\5.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\6.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\7.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\8.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\9.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\10.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\11.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\12.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\13.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\14.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Car\\15.txt";

	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\1.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\2.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\3.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\4.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\5.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\6.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\7.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\8.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\9.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\10.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\11.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\12.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\13.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\14.txt";
	//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Meat\\15.txt";

//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\1.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\2.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\3.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\4.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\5.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\6.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\7.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\8.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\9.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\10.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\11.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\12.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\13.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\14.txt";
//char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\15.txt";
	

	FILE* fin = fopen(filename, "rt");
	if (fin == NULL)
	{
		printf("无法打开数据文件:%f\n", filename);
		return 1;
	}
	while (fscanf(fin, "%f", &num) == 1)
	{
		S.push_back(num);
		//sDB.S[i++] = num;
	}
	fclose(fin);
	return 0;
}

uint32_t main() {

	fflush(stdout);
	read_file();

	DWORD begintime = GetTickCount();
	//char rulefilename[] = "..\\规则文档\\minsup=30\\股票Russell2000（1987.9.10~2019.12.27）.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\Italian-tem.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\Italian-temperature.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\1WTl-2.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\Crude Oil.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\random1.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\股票Nas（1971.3.1~2019.10.31）.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\股票sp500（1928.2.1~2019.10.31）.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\PRSA_Data_Nongzhanguan.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\PRSA_Data_Nongzhanguan_5000.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\PRSA_Data_Nongzhanguan_10000.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\PRSA_Data_Nongzhanguan_15000.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\PRSA_Data_Nongzhanguan_20000.txt";
	//char rulefilename[] = "..\\规则文档\\minsup=30\\PRSA_Data_Nongzhanguan_25000.txt";
	//char rulefilename[] = "..\\规则文档\\SDB3\\(12,0.45).txt";
	//char rulefilename[] = "..\\规则文档\\temp.txt";


	//char rulefilename[] = "..\\规则文档\\1.txt";
	//char rulefilename[] = "..\\规则文档\\2.txt";
	//char rulefilename[] = "..\\规则文档\\3.txt";
	//char rulefilename[] = "..\\规则文档\\4.txt";
	//char rulefilename[] = "..\\规则文档\\5.txt";
	//char rulefilename[] = "..\\规则文档\\6.txt";
	//char rulefilename[] = "..\\规则文档\\7.txt";
	//char rulefilename[] = "..\\规则文档\\8.txt";
	//char rulefilename[] = "..\\规则文档\\9.txt";
	//char rulefilename[] = "..\\规则文档\\10.txt";
	//char rulefilename[] = "..\\规则文档\\11.txt";
	//char rulefilename[] = "..\\规则文档\\12.txt";
	//char rulefilename[] = "..\\规则文档\\13.txt";
	//char rulefilename[] = "..\\规则文档\\14.txt";
	//char rulefilename[] = "..\\规则文档\\15.txt";
	//char rulefilename[] = "..\\规则文档\\16.txt";
	//char rulefilename[] = "..\\规则文档\\17.txt";
	//char rulefilename[] = "..\\规则文档\\18.txt";
	//char rulefilename[] = "..\\规则文档\\19.txt";
	//char rulefilename[] = "..\\规则文档\\20.txt";
	//char rulefilename[] = "..\\规则文档\\21.txt";
	//char rulefilename[] = "..\\规则文档\\22.txt";
	//char rulefilename[] = "..\\规则文档\\23.txt";
	//char rulefilename[] = "..\\规则文档\\24.txt";
	//char rulefilename[] = "..\\规则文档\\25.txt";
	//char rulefilename[] = "..\\规则文档\\26.txt";
	//char rulefilename[] = "..\\规则文档\\27.txt";
	//char rulefilename[] = "..\\规则文档\\28.txt";
	//char rulefilename[] = "..\\规则文档\\29.txt";
	//char rulefilename[] = "..\\规则文档\\30.txt";
	//char rulefilename[] = "..\\规则文档\\31.txt";
	//char rulefilename[] = "..\\规则文档\\32.txt";
	//char rulefilename[] = "..\\规则文档\\33.txt";
	//char rulefilename[] = "..\\规则文档\\34.txt";
	//char rulefilename[] = "..\\规则文档\\35.txt";
	//char rulefilename[] = "..\\规则文档\\36.txt";
	//char rulefilename[] = "..\\规则文档\\37.txt";
	//char rulefilename[] = "..\\规则文档\\38.txt";
	//char rulefilename[] = "..\\规则文档\\39.txt";
	//char rulefilename[] = "..\\规则文档\\40.txt";
	char rulefilename[] = "..\\规则文档\\41.txt";
	


	ofile.open(rulefilename);


	find();
	while (fre_num)
		generate_fre();

	DWORD endtime = GetTickCount();


	ofile.close();
	printf("The time-consuming:%d\n", endtime - begintime);
	printf("The number of frequent patterns:%d\n", frequent_num);
	printf("The number of candidate patterns:%d\n", cd_num);
	printf("The number of rule number:%d\n", rulenum);
//	printf("The number of all rule number:%d\n", allrulenum);
	return 0;
}
