#pragma warning(disable:4996) 
#include <stdio.h>
#include <string.h>
#include <string>
#include <stdint.h>
#include <time.h>
#include <stdlib.h>
#include <malloc.h>
#include <windows.h>


/* size of text and pattern 1 million numbers*/
#define TXT_SIZE 50000
#define PATTERN_SIZE 10000
#define MAX_LINE 60000
#define MAXSIZE 50000
const int MAX = 50000;
#define Max 256

//int minsup = 2;
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
//int minsup = 12;

//int minsup = 3;
int minsup = 12;
//int minsup = 75;
//int minsup = 375;
//int minsup = 1875;



int count;
int candidate_num = 0;
int compnum = 2;
int L2[700][700] = { 0 };
int L[700][700] = { 0 };
int scan_num = 0;
int read_num = 0;


int C[2000][2000] = { 0 };

int Snum;
int frequent_num;

void radix_sort(uint32_t* p, uint32_t length);
void BNDM(int* txt, int* pat, uint32_t txt_length, uint32_t pat_length);
void SBNDM(int* txt, int* pat, uint32_t txt_length, uint32_t pat_length);
void transform_text(float* txt, uint32_t txt_length);
void transform_pattern(int* pat, uint32_t pat_length);
void gen_aux(uint32_t* arr, uint32_t length);
uint32_t generate_fre(int min[], int fre[][1000]);
void Cancalute(int max[]);
int read_file();
uint32_t LEN = 0;


float text[TXT_SIZE];


/*pattern to be found inside text*/
int pattern[PATTERN_SIZE];

/*sorted pattern*/
uint32_t sorted_pat[PATTERN_SIZE];

/*auxiliary table to store relative position*/
uint32_t aux[PATTERN_SIZE];

/* transformed text array which stores binary value */
int trans_text[TXT_SIZE - 1];
/* transformed pattern array which stores binary value */
int trans_pattern[PATTERN_SIZE - 1];
uint32_t pattern_num = 0;

struct seqdb
{
	float S[MAX_LINE];              // sequence
	int seqlen;
} sDB;


uint32_t matching1(float* text, int* pattern, uint32_t txt_size, uint32_t pattern_size)
{

	uint32_t i;

	/* copy to array for radix sort*/
	for (i = 0; i < pattern_size; i++) {
		sorted_pat[i] = pattern[i];
	}
	//perform radix sort
	radix_sort(sorted_pat, pattern_size);
	//generate auxiliary table
	gen_aux(aux, pattern_size);
	//generate binary array
	transform_text(text, txt_size - 1);
	transform_pattern(pattern, pattern_size - 1);
	BNDM(trans_text, trans_pattern, txt_size - 1, pattern_size - 1);
	return  pattern_num;
}

uint32_t matching2(float* text, int* pattern, uint32_t txt_size, uint32_t pattern_size)
{

	uint32_t i;

	/* copy to array for radix sort*/
	for (i = 0; i < pattern_size; i++) {
		sorted_pat[i] = pattern[i];
	}
	//perform radix sort
	radix_sort(sorted_pat, pattern_size);
	//generate auxiliary table
	gen_aux(aux, pattern_size);
	//generate binary array
	transform_text(text, txt_size - 1);
	transform_pattern(pattern, pattern_size - 1);
	SBNDM(trans_text, trans_pattern, txt_size - 1, pattern_size - 1);
	return  pattern_num;

}

uint32_t generate_candL2(int m[])
{
	int i, j, support_full = 0, k = 0;

	int	C2[2][2] = { {1,2},{2,1} };

	for (j = 0; j < 2; j++)
	{
		scan_num++;
		memcpy(m, C2[j], 12);
		DWORD begintime = GetTickCount();
		support_full = matching1(sDB.S, m, sDB.seqlen, 2);
		
		if (support_full >= minsup)
		{
			count++;
			frequent_num++;

			for (int x = 0; x < 2; x++) 
			{
				L2[j][x] = C2[j][x];
			}

		}
	}
	return 0;
}

int* sort(int src[]) {
	int k, slen = 0, y = 0;
	int level = 1;
	int* sort_array;

	while (y < 50)
	{
		if (src[y] != 0)
			slen++;
		y++;
	}

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

uint32_t generate_fre(int min[], int fre[][700])
{

	int slen = 0;
	int Q[100] = { 0 };
	int R[100] = { 0 };
	int* q;
	int* r;
	int y = 0, j = 0;



	while (y < 50)
	{
		if (fre[0][y] != 0)
			slen++;
		y++;
	}



	for (int i = 0; i < frequent_num; i++)
	{

		memcpy(Q, fre[i] + 1, (slen - 1) * sizeof(int));//求后缀
		q = sort(Q);
		for (int j = 0; j < frequent_num; j++)
		{
			memcpy(R, fre[j], (slen - 1) * sizeof(int));//求前缀
			r = sort(R);
			if (memcmp(q, r, (slen - 1) * sizeof(int)))
			{
				//printf("排名不一样\n");		
			}
			else
			{
				//printf("排名一样\n");

				if (fre[i][0] == fre[j][slen - 1])	           //最前最后位置相等，拼接成两个模式			
				{
					C[candidate_num][0] = fre[i][0];
					C[candidate_num + 1][0] = fre[i][0] + 1;
					C[candidate_num][slen] = fre[i][0] + 1;
					C[candidate_num + 1][slen] = fre[i][0];
					for (int t = 1; t < slen; t++)
					{
						if (fre[i][t] > fre[j][slen - 1])
						{
							//中间位置增长
							C[candidate_num][t] = fre[i][t] + 1;
							C[candidate_num + 1][t] = fre[i][t] + 1;
						}
						else
						{
							C[candidate_num][t] = fre[i][t];
							C[candidate_num + 1][t] = fre[i][t];
						}
					}

					candidate_num += 2;
					compnum += 2;
					scan_num += 2;

				}
				else if (fre[i][0] < fre[j][slen - 1])    //第一个位置比最后一个位置小
				{

					C[candidate_num][0] = fre[i][0];              //小的不变
					C[candidate_num][slen] = fre[j][slen - 1] + 1;  //大的加一

					for (int t = 1; t < slen; t++)
					{
						if (fre[i][t] > fre[j][slen - 1])
						{
							//fre[i][t]+=1;   //中间位置增长
							C[candidate_num][t] = fre[i][t] + 1;

						}
						else
						{
							C[candidate_num][t] = fre[i][t];

						}
					}
					//printf("%d+%d=%d\n",fre[i],fre[j],C[candidate_num]);	
					candidate_num += 1;
					compnum += 1;
					scan_num += 1;


				}
				else {

					C[candidate_num][0] = fre[i][0] + 1;              //大的加一
					C[candidate_num][slen] = fre[j][slen - 1];       //小的不变


					for (int t = 0; t < slen - 1; t++)
					{
						if (fre[j][t] > fre[i][0])
						{

							C[candidate_num][t + 1] = fre[j][t] + 1;   //中间位置增长

						}
						else
						{

							C[candidate_num][t + 1] = fre[j][t];

						}
					}
					//printf("%d+%d=%d\n",fre[i],fre[j],C[candidate_num]);
					candidate_num += 1;
					compnum += 1;
					scan_num += 1;

				}

			}

		}

	}

	y, slen = 0;

	return 0;
}

void Cancalute(int max[])
{
	int len = 0, support_full, r = 0;
	frequent_num = 0;
	while (candidate_num != 0)
	{

		while (r < 50)
		{
			if (C[0][r] != 0)
				len++;
			r++;
		}


		for (int v = 0; v < candidate_num; v++)
		{

			memcpy(max, C[v], (len) * sizeof(int));
			/*
				printf("(");

					for(int z=0;z<len;z++)
					{

						printf("%d",C[v][z]);
						if(z!=len-1)
						{
							printf(",");
						}
					}
					printf(")");
					printf("候选");
					printf("\n");


					printf("support_full : = %d\n",support_full);
					printf("-----------------------------------------\n");
			*/
			support_full = matching2(sDB.S, C[v], sDB.seqlen, len);
			//	printf("-----------------------------------------\n");
			if (support_full >= minsup)
			{
				count++;
				memcpy(L[frequent_num], C[v], (len) * sizeof(int));

				

				printf("(");

				for (int z = 0; z < len; z++)
				{

					printf("%d", L[frequent_num][z]);
					if (z != len - 1)
					{
						printf(",");
					}
				}
				printf(")");
				printf("频繁");
				printf("\n");
				
				printf("support_full : = %d\n", support_full);
				//printf("-----------------------------------------\n");
				
				frequent_num++;
			}
		}
		r = 0;
		len = 0;

		memset(C, 0, sizeof(C));
		candidate_num = 0;

		generate_fre(max, L);
		memset(L, 0, sizeof(L));
		frequent_num = 0;
	}


}

void transform_text(float* txt, uint32_t txt_length)
{
	uint32_t loop;
	for (loop = 0; loop < txt_length; loop++)
	{
		if (txt[loop] < txt[loop + 1])
		{
			trans_text[loop] = '1';
		}
		else
		{
			trans_text[loop] = '0';
		}
	}
}

void transform_pattern(int* pat, uint32_t pat_length)
{
	uint32_t loop;
	for (loop = 0; loop < pat_length; loop++)
	{
		if (pat[loop] < pat[loop + 1])
		{
			trans_pattern[loop] = '1';


		}
		else
		{
			trans_pattern[loop] = '0';
		}

	}

}

void BNDM(int* txt, int* pat, uint32_t txt_length, uint32_t pat_length)
{
	pattern_num = 0;
	uint32_t flag = 0, f = 0;
	unsigned int B[Max] = { 0 };
	int pos = 0;
	int lmp = 0;


	for (int i = 0; i < pat_length; i++)
		B[pat[i]] |= 1 << (pat_length - i - 1);

	while (pos <= txt_length - pat_length)
	{
		read_num++;
		int j = pat_length - 1;
		int last = pat_length;
		unsigned int D = -1;

		while (D)
		{
			D = D & B[txt[pos + j]];

			if ((D & (1 << (pat_length - 1))) != 0)
			{
				if (j > 0)
					last = j;
				else {


					uint32_t len_cand = pos + pat_length;
					//	printf("len_cand=%d\n",len_cand);
					uint32_t x, k = 0;
					uint32_t cand = pos;
					//	printf("cand=%d\n",cand);
					//conditions checked proposed by paper 
					for (x = pos; x < len_cand; x++) {
						if (sDB.S[cand - 1 + aux[k]] >= sDB.S[cand - 1 + aux[k + 1]]) {
							f = 0;
							break;
						}
						else {
							f = 1;
						}
						k++;
					}


					if (f > 0) {
						flag = 1;
						//printf("%d(", pos - pat_length + 1);//输出起始位置
						//printf(")");
						lmp = pos - pat_length + 2;
						//	printf("%d,", lmp);
							/*
							printf("%d(",pos-pat_length+1);
							for(int v=(pos-pat_length)+1;v<len_cand+1;v++){
								printf("%f",sDB.S[v]);
								if(v!=len_cand){
									printf(",");
								}
							}

							printf(")\n");

							*/

						pattern_num++;
					}

				}
			}
			j--;
			D = D << 1;
		}
		pos += last;
	}
}

void SBNDM(int* txt, int* pat, uint32_t txt_length, uint32_t pat_length)
{


	int pos, D, k, j, q;
	pattern_num = 0;
	uint32_t flag = 0, f = 0;
	unsigned int B[Max] = { 0 };


	for (j = 0; j < pat_length; j++)
	{
		B[pat[j]] = B[pat[j]] | (1 << (pat_length - j - 1));
		read_num++;
	}


	pos = pat_length - 1;



	while (pos <= txt_length - 1) {
		//read_num++;

		D = (B[txt[pos - 1]]) & (B[txt[pos]] << 1);



		if (D != 0)

		{

			j = pos - pat_length + 1;

			do
			{



				pos = pos - 1;

				if (pos == 0) {

					D = 0;

				}
				else {

					D = (D << 1) & B[txt[pos - 1]];
				}


			} while (D != 0);


			if (j == pos)
			{

				uint32_t len_cand = j + pat_length;
				//printf("len_cand=%d\n",len_cand);
				uint32_t x, k = 0;
				uint32_t cand = j;
				//	printf("cand=%d\n",cand);
				//conditions checked proposed by paper 
				for (x = j; x < len_cand; x++) {
					if (sDB.S[cand - 1 + aux[k]] >= sDB.S[cand - 1 + aux[k + 1]]) {
						f = 0;
						break;
					}
					else {
						f = 1;
					}
					k++;
				}


				if (f > 0) {
					flag = 1;


					//	printf("%d(",j);

					/*
						for(int v=j;v<len_cand+1;v++){
							printf("%f",sDB.S[v]);
							if(v!=len_cand){
								printf(",");
							}
						}

						printf(")\n");

					 */

					 //	printf("%d(", j + pat_length);

					 //	printf(")");


						 //		printf(")\n");

					pattern_num++;
				}

				pos = pos + 1;
			}

		}
		pos = pos + pat_length - 1;
	}

}


void radix_sort(uint32_t* arr, uint32_t length) {

	uint8_t pass;

	/* dont touch i and keep it signed to avoid faults*/
	int32_t i;

	/* Arrays to store count and final sorted array */
	uint8_t countArr[256];

	//allocating memory for temporary array
	uint32_t* copyArr = (uint32_t*)malloc(length * sizeof(uint32_t));
	memset(copyArr, 0, length * sizeof(uint32_t));

	/*four passes*/
	for (pass = 0; pass < 4; pass++) {

		//setting zero in counting array
		memset((void*)countArr, 0, 256 * sizeof(uint8_t));

		/* counting sort */
		for (i = 0; i < length; i++) {
			countArr[(arr[i] >> 8 * pass) & 255]++;
		}
		for (i = 1; i < 256; i++) {
			countArr[i] += countArr[i - 1];
		}
		for (i = length - 1; i >= 0; i--) {
			copyArr[--countArr[(arr[i] >> 8 * pass) & 255]] = arr[i];
		}

		/* copy array value to run next pass*/
		for (i = 0; i < length; i++) {
			arr[i] = copyArr[i];
		}
	}
	free(copyArr);
}

/* generate auxiliary table */
void gen_aux(uint32_t* arr, uint32_t length) {

	uint32_t i, j;

	for (i = 0; i < length; i++) {
		for (j = 0; j < length; j++) {
			if (sorted_pat[i] == pattern[j]) {
				arr[i] = j + 1;
			}
		}
	}

}

int read_file()
{

	int i, n = 0;
	float num;
	float a[MAX];
	//char filename[] = "..\\..\\Data-Nov\\Gold.txt";
	//char filename[] = "..\\..\\Data-Nov\\Vix.txt";
	//char filename[] = "..\\..\\Data-Nov\\Wanshouxigong.txt";
	//char filename[] = "..\\..\\大哥数据集\\Crude Oil(20000112-20201012.txt";
	//char filename[] = "..\\..\\Data-Nov\\Gold-1490.txt";
	//char filename[] = "..\\..\\Data-Nov\\Gold-2738.txt";
	//char filename[] = "..\\..\\Data-Nov\\Gold-3982.txt";
	//char filename[] = "..\\..\\Data-Nov\\Gold-5060.txt";
	//char filename[] = "..\\..\\Data-Nov\\random.txt";
	//char filename[] = "..\\..\\Data-Nov\\股票Nas（1971.3.1~2019.10.31）.txt";
	//char filename[] = "..\\..\\Data-Nov\\股票DAO（1900.1.2~2019.11.29）.txt";
	//char filename[] = "..\\..\\Data-Nov\\股票Russell2000（1987.9.10~2019.12.27）.txt";
	//char filename[] = "..\\..\\Data-Nov\\股票sp500（1928.2.1~2019.10.31）.txt";
	//char filename[] = "..\\..\\Data-Nov\\天气Gucheng_20130301-20170228.txt";
	//char filename[] = "..\\..\\Data-Nov\\天气Huairou_20130301-20170228.txt";
	//char filename[] = "..\\..\\Data-Nov\\天气Shunyi_20130301-20170228.txt";
	//char filename[] = "..\\..\\Data-Nov\\天气Tiantan.txt";

	//char filename[] = "..\\dataset\\Italian-tem.txt";  //SDB1
	//char filename[] = "..\\dataset\\Italian-temperature.txt";  //SDB2
	//char filename[] = "..\\dataset\\1WTl-2.txt";//SDB3
	//char filename[] = "..\\dataset\\Crude Oil.txt";//SDB4
	//char filename[] = "..\\dataset\\股票Russell2000（1987.9.10~2019.12.27）.txt";//SDB5
	//char filename[] = "..\\dataset\\股票Nas（1971.3.1~2019.10.31）.txt";//SDB6
	//char filename[] = "..\\dataset\\股票sp500（1928.2.1~2019.10.31）.txt";//SDB7
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan.txt";//SDB8
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_5000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_10000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_15000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_20000.txt";
	//char filename[] = "..\\dataset\\PRSA_Data_Nongzhanguan_25000.txt";
	//char filename[] = "..\\dataset\\李超然温度.txt";
	//char filename[] = "..\\dataset\\不同数据规模\\90.txt";
	//char filename[] = "..\\dataset\\不同数据规模\\900.txt";
	//char filename[] = "..\\dataset\\不同数据规模\\9000.txt";
	//char filename[] = "..\\dataset\\不同数据规模\\90000.txt";
	//char filename[] = "..\\dataset\\不同数据规模\\900000.txt";

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

  // char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\Beef\\1.txt";
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
	char filename[] = "E:\\Contrast_min\\保序规则算法\\Case study dataset\\15.txt";


	FILE* fin = fopen(filename, "rt");
	if (fin == NULL)
	{
		printf("无法打开数据文件:%f\n", filename);
		return 1;
	}
	while (fscanf(fin, "%f", &num) == 1)
	{
		a[n++] = num;
	}
	fclose(fin);
	for (i = 0; i < n; ++i) {
		// if(i && i % 10 == 0) 
		   // printf("\n");
		 //printf("%f\n",a[i]);
		sDB.S[i] = a[i];
		//printf("%f\n",sDB.S[i]);
	}
	sDB.seqlen = n;
	//printf("hhhhhhhhh%d\n",n);
	return 0;
}













uint32_t main() {
	uint32_t support;

	fflush(stdout);

	read_file();

	DWORD begintime = GetTickCount();
	support = generate_candL2(pattern);

	generate_fre(pattern, L2);
	Cancalute(pattern);
	DWORD endtime = GetTickCount();
	printf("The time-consuming:%d\n", endtime - begintime);
	printf("The number of frequent patterns:%d\n", count);
	printf("The number of calcation patterns:%d\n", compnum);
	printf("The number of scan sequence:%d\n", scan_num);
	printf("The number of read sequence:%d\n", read_num);


	return 0;



}