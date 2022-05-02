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
using namespace std;

vector<float> S;  // sequence

typedef struct LNode {
	int data;
	struct LNode* next;
} LNode;

vector<int> Cd;//��ѡģʽ
vector<int> Cd2;
vector<int> Z;//�����±�
vector<int> Z2;

vector<vector<int>> P;//����Ϊm��Ƶ��ģʽ�����±꼯��
vector<vector<int>>L;//����Ϊm��Ƶ��ģʽ����

vector<vector<int>> Pc;//����Ϊm�������±꼯��
vector<vector<int>>Lc;//����Ϊm��ģʽ����

//int minsup =2;
//int minsup = 5;
//int minsup = 6;
//int minsup = 7;
//int minsup = 10;
//int minsup = 12;
//int minsup = 15;
//int minsup = 17;
//int minsup = 20;
//int minsup = 22;
//int minsup = 25;
//int minsup = 27;
//int minsup = 30;
//int minsup = 40;
//int minsup = 50;
//int minsup = 75;
//int minsup = 100;
//int minsup = 125;
//int minsup = 150;
//int minsup = 175;
//int minsup = 200;
//int minsup = 250;
//int minsup = 300;

//int minsup = 3;
//int minsup = 15;
//int minsup = 75;
//int minsup = 375;
//int minsup = 1875;
int minsup = 12;

int match_count = 0;//������Ԫ��ƥ��Ĵ���


int frequent_num = 0;//�ܵ�Ƶ��ģʽ����
int fre_num = 0;//����Ϊm��Ƶ��ģʽ����
int cd_num = 2;//��ѡģʽ����
int scan_num = 1;
int read_num = 0;



int read_file();
void find();
void judge_fre(int sup_num, vector<int> Cd, vector<int> Z);
void enumerate();
int* sort(vector<int> src);
uint32_t grow_BaseP1(vector<int> postion, LNode* L);
uint32_t grow_BaseP2(int slen, vector<int> postion, LNode* L, int flag);


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

//��ȡ�ļ�
int read_file()
{
	int i = 0;
	float num;
	
	//char filename[] = "..\\dataset\\Italian-tem.txt";
	//char filename[] = "..\\dataset\\Italian-temperature.txt";
	//char filename[] = "..\\dataset\\1WTl-2.txt";
	//char filename[] = "..\\dataset\\Crude Oil.txt";
	//char filename[] = "..\\dataset\\��ƱRussell2000��1987.9.10~2019.12.27��.txt";
	//char filename[] = "..\\dataset\\��ƱNas��1971.3.1~2019.10.31��.txt";
	//char filename[] = "..\\dataset\\��Ʊsp500��1928.2.1~2019.10.31��.txt";
	char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_5000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_10000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_15000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_20000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_25000.txt";

	//char filename[] = "..\\dataset\\��ͬ���ݹ�ģ\\90.txt";
	//char filename[] = "..\\dataset\\��ͬ���ݹ�ģ\\900.txt";
	//char filename[] = "..\\dataset\\��ͬ���ݹ�ģ\\9000.txt";
	//char filename[] = "..\\dataset\\��ͬ���ݹ�ģ\\90000.txt";
	//char filename[] = "..\\dataset\\��ͬ���ݹ�ģ\\900000.txt";

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

//2����ģʽ��ȡĩλ
void find()
{
	int i = 0, j = 1;
	Cd.push_back(1);
	Cd.push_back(2);
	Cd2.push_back(2);
	Cd2.push_back(1);
	while (j < S.size())
	{
		if (S[j] > S[i]) //12ģʽ
		{
			Z.push_back(j);
		}
		else if (S[j] != S[i]) //21ģʽ
		{
			Z2.push_back(j);
		}
		i++;
		j++;
	}
	Lc.push_back(Cd);
	Pc.push_back(Z);
	Lc.push_back(Cd2);
	Pc.push_back(Z2);
	judge_fre(Z.size(), Cd, Z);
	Cd.clear();
	judge_fre(Z2.size(), Cd2, Z2);
	Cd2.clear();
}


//�ж��Ƿ���Ƶ��ģʽ
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
		frequent_num++;
		fre_num++;
	}
}

//ö�ٷ����ɺ�ѡģʽ
void enumerate()
{
	vector<vector<int>> Lcd;//����Ϊm��ģʽ����
	vector<vector<int>> Pcd;//����Ϊm��ĩλ����
	vector<vector<int>> Ld;//����Ϊm��Ƶ��ģʽ����
	vector<vector<int>> Pd;//����Ϊm��Ƶ��ģʽ��������

	Lcd = Lc;
	Pcd = Pc;
	Ld = L;
	Pd = P;

	Lc.clear();
	Pc.clear();
	L.clear();
	P.clear();

	int i = 0, j, k, f;
	int temp;
	int len = Ld[0].size();
	Cd.resize(len + 1);

	int size = Lcd.size();
	vector<int> Q;

	int* q;
	int* r;

	LNode* Node;
	LNode* p, * s;

	fre_num = 0;

	while (i < Ld.size())
	{
		Node = (LNode*)malloc(sizeof(LNode));
		s = Node;
		Node->data = Pd[i].size();
		for (f = 0; f < Pd[i].size(); f++)
		{
			p = (LNode*)malloc(sizeof(LNode));
			p->data = Pd[i][f];
			s->next = p;
			s = p;
		}
		s->next = NULL;

		for (temp = 1; temp <= len + 1; temp++)
		{
		
		//	if (Node->data >= minsup)
			{
				//���ɳ�ģʽ
				for (j = 0; j < len; j++)
			{
				if (Ld[i][j] < temp)
				{
					Cd[j] = Ld[i][j];
				}
				else
				{
					Cd[j] = Ld[i][j] + 1;
				}
			}
			Cd[len] = temp;
			Lc.push_back(Cd);
			cd_num = cd_num + 1;

			//��ģʽCd������֧�ֶ�
			Q.assign(Cd.begin() + 1, Cd.end());
			q = sort(Q);
			for (k = 0; k < size; k++)
			{
				r = sort(Lcd[k]);
				if (memcmp(q, r, len * sizeof(int)))
				{
					;//��һ��
				}
				else
				{	//һ��
					//p[0]!=q[max]
					if (Ld[i][0] != Lcd[k][len - 1])
						grow_BaseP1(Pcd[k], Node);
					//p[0]=q[max]
					else
					{
						if (Cd[0] < Cd[len])
						{
							grow_BaseP2(len, Pcd[k], Node, 1);
						}
						else
						{
							grow_BaseP2(len, Pcd[k], Node, 2);
						}
					}
				}
			}

			}
		}
		i++;
	}
}

uint32_t grow_BaseP1(vector<int> postion, LNode* L)
{
	int  m = 0;
	int size = postion.size();
	LNode* p = L;
	Z.clear();

	while (p->next != NULL && m < size)
	{
		if (postion[m] == p->next->data + 1)
		{
			Z.push_back(postion[m]);
			m++;
			p->next = p->next->next;
		}
		else if (p->next->data < postion[m])
		{
			p = p->next;
		}
		else
		{
			m++;
		}
		match_count += 1;
	}
	L->data = L->data - Z.size();
	Pc.push_back(Z);
	judge_fre(Z.size(), Cd, Z);
	return 0;
}

uint32_t grow_BaseP2(int slen, vector<int> postion, LNode* L, int flag)
{
	int m = 0;
	int lst, fri;
	int size = postion.size();
	LNode* p = L;
	Z.clear();
	Z2.clear();
	while (p->next != NULL && m < size)
	{
		if (postion[m] == p->next->data + 1)
		{
			lst = postion[m];
			fri = postion[m] - slen;
			read_num++;
			if (flag == 1)
			{
				if (S[lst] > S[fri])
				{
					Z.push_back(postion[m]);
					p->next = p->next->next;
				}
			}
			else if (S[lst] < S[fri])
			{
				Z.push_back(postion[m]);
				p->next = p->next->next;
			}
			m++;
		
		}
		else if (p->next->data < postion[m])
		{
			p = p->next;
		}
		else
		{
			m++;
		}
		match_count += 1;
	}
	Pc.push_back(Z);
	L->data = L->data - Z.size();
	judge_fre(Z.size(), Cd, Z);
	return 0;
}


int main()
{
	fflush(stdout);

	read_file();

	DWORD begintime = GetTickCount();
	find();
	while (fre_num)
		enumerate();


	DWORD endtime = GetTickCount();
	printf("The time-consuming:%d\n", endtime - begintime);
	printf("The number of frequent patterns:%d\n", frequent_num);
	printf("The number of candidate patterns:%d\n", cd_num);
	printf("The number of scan sequence:%d\n", scan_num);
	printf("The number of read sequence:%d\n", read_num);
	printf("The number of match count:%d\n", match_count);

	return 0;
}