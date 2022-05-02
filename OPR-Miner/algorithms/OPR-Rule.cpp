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


vector<int> rule_left;//����ǰ��
vector<int> rule_right;//������
int rule_leftnum;//����ǰ��֧�ֶ�
int rule_rightnum;//������֧�ֶ�


int allrulenum = 0;



ofstream ofile;

//int minsup = 3;
//int minsup = 5;
//int minsup = 6;
//int minsup = 7;
//int minsup = 10;
int minsup = 12;
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


int frequent_num = 0;  //�ܵ�Ƶ��ģʽ����
int fre_num = 0;
int cd_num = 2; //��ѡģʽ����



vector<vector<int>> P;  //���ĩλ������
vector<vector<int>> L;  //���ÿ�����ɵ�Ƶ��ģʽ
vector<int> Z;  //��ű������ɵ�ĩλ����
vector<int> Z2;

vector<int> Cd;  //��ű������ɵ�ģʽ
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


uint32_t generate_fre()   //ģʽƴ��
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

	slen = L[0].size();//ģʽ����

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
		Q.assign(fre[i].begin() + 1, fre[i].end());//���׺
		q = sort(Q);
		//��������
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
				R.pop_back();   //��ǰ׺
				r = sort(R);
				if (memcmp(q, r, (slen - 1) * sizeof(int)))
				{
					;//printf("������һ��\n");		
				}
				else
				{
					//	vector <int> postion;
					//	postion = pos[j];
						//printf("����һ��\n");
					if (fre[i][0] == fre[j][slen - 1])	           //��ǰ���λ����ȣ�ƴ�ӳ�����ģʽ			
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
								//�м�λ������
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
					else if (fre[i][0] < fre[j][slen - 1])    //��һ��λ�ñ����һ��λ��С
					{
						Cd[0] = fre[i][0];              //С�Ĳ���
						Cd[slen] = fre[j][slen - 1] + 1;  //��ļ�һ

						for (int t = 1; t < slen; t++)
						{
							if (fre[i][t] > fre[j][slen - 1])
							{
								//fre[i][t]+=1;   //�м�λ������
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
						Cd[0] = fre[i][0] + 1;              //��ļ�һ
						Cd[slen] = fre[j][slen - 1];       //С�Ĳ���
						for (int t = 0; t < slen - 1; t++)
						{
							if (fre[j][t] > fre[i][0])
							{
								Cd[t + 1] = fre[j][t] + 1;   //�м�λ������

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


void recommend(int sup_begin, float sup_end, vector<int> Cd_begin, vector<int> Cd_end)  //�Ƽ�ģʽ
{
	
	/*
		printf("ģʽ");
		for (vector<int>::iterator it = Cd_begin.begin(); it != Cd_begin.end(); it++)
		{
			printf("%d", *it);
			//	ofile << *it << ",";
		}

		printf("=>");
		//ofile << " ";
		for (vector<int>::iterator it = Cd_end.begin(); it != Cd_end.end(); it++)
		{
			printf("%d", *it);
			//	ofile << *it << ",";
		}
		printf("���Ŷ�Ϊ��%f", sup_end / sup_begin);
		printf("\n");
		//ofile <<sup_end / sup_begin;
		//ofile << endl;
		*/
	
	
}

void judge_fre(int sup_num, vector<int> Cd, vector<int> Z)
{
	if (sup_num >= minsup)
	{
		P.push_back(Z);
		L.push_back(Cd);
		/*
		printf("Ƶ��ģʽ��");
		for (vector<int>::iterator it = Cd.begin(); it != Cd.end(); it++)
		{
			printf("%d,", *it);
		}
		printf("֧�ֶ�Ϊ��%d\n", sup_num);


		printf("���ַ����г��ֵ�λ�ã�");
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
void judge_fre2(int sup_num, vector<int> Cd, vector<int> Z)
{
	if (sup_num >= minsup)
	{
		P.push_back(Z);
		L.push_back(Cd);
		/*
		printf("Ƶ��ģʽ��");
		for (vector<int>::iterator it = Cd.begin(); it != Cd.end(); it++)
		{
			printf("%d,", *it);
		}
		printf("֧�ֶ�Ϊ��%d\n", sup_num);


		printf("���ַ����г��ֵ�λ�ã�");
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
		if (S[j] > S[i])   //12ģʽ
		{
			Z.push_back(j);

		}
		else if (S[j] != S[i])                //21ģʽ
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
	char filename[] = "..\\dataset\\1WTl-2.txt";//SDB3
	//char filename[] = "..\\dataset\\Crude Oil.txt";//SDB4
	//char filename[] = "..\\dataset\\random1.txt";
    //char filename[] = "..\\dataset\\��ƱRussell2000��1987.9.10~2019.12.27��.txt";//SDB5
	//char filename[] = "..\\dataset\\��ƱNas��1971.3.1~2019.10.31��.txt";//SDB6
	//char filename[] = "..\\dataset\\��Ʊsp500��1928.2.1~2019.10.31��.txt";//SDB7
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan.txt";//SDB8
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_5000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_10000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_15000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_20000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_25000.txt";
	//char filename[] = "..\\dataset\\����2.txt";
	//char filename[] = "..\\dataset\\random2.txt";
	FILE* fin = fopen(filename, "rt");
	if (fin == NULL)
	{
		printf("�޷��������ļ�:%f\n", filename);
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
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\��ƱRussell2000��1987.9.10~2019.12.27��.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\Italian-tem.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\Italian-temperature.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\1WTl-2.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\Crude Oil.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\random1.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\��ƱNas��1971.3.1~2019.10.31��.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\��Ʊsp500��1928.2.1~2019.10.31��.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\PRSA_Data_Nongzhanguan.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\PRSA_Data_Nongzhanguan_5000.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\PRSA_Data_Nongzhanguan_10000.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\PRSA_Data_Nongzhanguan_15000.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\PRSA_Data_Nongzhanguan_20000.txt";
	//char rulefilename[] = "..\\�����ĵ�\\minsup=30\\PRSA_Data_Nongzhanguan_25000.txt";
	//char rulefilename[] = "..\\�����ĵ�\\SDB3\\(12).txt";


	//ofile.open(rulefilename);


	find();
	while (fre_num)
		generate_fre();

	DWORD endtime = GetTickCount();


	ofile.close();
	printf("The time-consuming:%d\n", endtime - begintime);
	printf("The number of frequent patterns:%d\n", frequent_num);
	printf("The number of candidate patterns:%d\n", cd_num);

	printf("The number of all rule number:%d\n", allrulenum);
	return 0;
}
