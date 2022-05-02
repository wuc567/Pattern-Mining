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

//int minsup = 1;
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
int minsup = 12;
//int minsup = 75;
//int minsup = 375;
//int minsup = 1875;



int frequent_num = 0;  //�ܵ�Ƶ��ģʽ����
int fre_num = 0;
int cd_num = 2;//��ѡģʽ��
int scan_num = 1;
int read_num = 0;
int match_count = 0;//������Ԫ��ƥ��Ĵ���


vector<vector<int>> P;//���ĩλ������
vector<vector<int>> L;//���ÿ�����ɵ�Ƶ��ģʽ
vector<int> Z;//��ű������ɵ�ĩλ����
vector<int> Z2;

vector<int> Cd;//��ű������ɵ�ģʽ
vector<int> Cd2;


void judge_fre(int sup_num, vector<int> Cd, vector<int> Z);


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

int grow_BaseP1(vector<int> postion, LNode* L)
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
	judge_fre(Z.size(), Cd, Z);
	return 0;
}

int grow_BaseP2(int slen, vector<int> postion, LNode* L)
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
			read_num = read_num + 1;
			if (S[lst] > S[fri])
			{
				Z.push_back(postion[m]);
				p->next = p->next->next;
			}
			else if (S[lst] != S[fri])
			{
				Z2.push_back(postion[m]);
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

	int* q;
	int* r;
	int j = 0;
	int fre_number = 0;
	int t = 0;
	int k = 0;

	slen = L[0].size();//ģʽ����

	fre.clear();
	pos.clear();
	fre = L;
	L.clear();
	fre_number = fre_num;
	fre_num = 0;

	pos = P;
	P.clear();

	Cd.resize(slen + 1);
	Cd2.resize(slen + 1);

	for (int i = 0; i < fre_number; i++)
	{
		Q.assign(fre[i].begin() + 1, fre[i].end());//���׺

		q = sort(Q);

		//��������
		LNode* L;
		LNode* p, * s;
		int size = pos[i].size();
		L = (LNode*)malloc(sizeof(LNode));
		s = L;
		s->next = NULL;
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
			R = fre[j];
			R.pop_back();   //��ǰ׺
			r = sort(R);
			if (memcmp(q, r, (slen - 1) * sizeof(int)))
			{
				;//printf("������һ��\n");		
			}
			else
			{
				vector <int> postion;
				postion = pos[j];
				//printf("����һ��\n");
				if (fre[i][0] == fre[j][slen - 1])	           //��ǰ���λ����ȣ�ƴ�ӳ�����ģʽ			
				{
					Cd[0] = fre[i][0];
					Cd2[0] = fre[i][0] + 1;
					Cd[slen] = fre[i][0] + 1;
					Cd2[slen] = fre[i][0];
					for (int t = 1; t < slen; t++)
					{
						if (fre[i][t] > fre[j][slen - 1])
						{
							Cd[t] = fre[i][t] + 1;
							Cd2[t] = fre[i][t] + 1;
						}
						else
						{
							Cd[t] = fre[i][t];
							Cd2[t] = fre[i][t];
						}
					}
					cd_num = cd_num + 2;
					grow_BaseP2(Cd.size() - 1, postion, L);
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
					grow_BaseP1(postion, L);
					cd_num = cd_num + 1;
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
					//printf("%d+%d=%d\n",fre[i][0],fre[j][0],Cd[0]);
					grow_BaseP1(postion, L);
					cd_num = cd_num + 1;
				}
			}
		}
	}
	return 0;

}


void judge_fre(int sup_num, vector<int> Cd, vector<int> Z)
{
	int i = 0;
	int j = 0;
	int len = Cd.size();

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
			printf("%d,", *it +1);
		}
		printf("\n\n");
	*/
		frequent_num++;
		fre_num++;
	}

}

//ģʽ1 2��ģʽ2 1�Ľ��
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
	judge_fre(Z.size(), Cd, Z);
	Cd.clear();
	judge_fre(Z2.size(), Cd2, Z2);
	Cd2.clear();
}

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
	//char filename[] = "..\\dataset\\����.txt";
	//char filename[] = "..\\dataset\\����2.txt";


	//char filename[] = "..\\dataset\\��ͬ���ݹ�ģ\\90.txt";
//	char filename[] = "..\\dataset\\��ͬ���ݹ�ģ\\900.txt";
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

uint32_t main() {

	fflush(stdout);

	read_file();

	DWORD begintime = GetTickCount();
	find();
	while (fre_num)
		generate_fre();





	DWORD endtime = GetTickCount();
	printf("The time-consuming:%d\n", endtime - begintime);
	printf("The number of frequent patterns:%d\n", frequent_num);
	printf("The number of candidate patterns:%d\n", cd_num);
	printf("The number of scan sequence:%d\n", scan_num);
	printf("The number of read sequence:%d\n", read_num);
	printf("The number of matching count:%d\n", match_count);

	return 0;
}
