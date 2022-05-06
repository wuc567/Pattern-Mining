#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include<vector>
#include <stdio.h>
#include <string.h>
#include <string>
#include <stdint.h>
#include <time.h>
#include <stdlib.h>
#include <math.h>
#include <map>
#include<fstream>
#include<strstream>
#include <windows.h>
using namespace std;
unsigned int delta, gamma, sup;
bool fil = false;
vector<float> s1;
vector < vector<float>> final;
unsigned int candidate = 0;
int sort(vector<float>& a)
{
	float tmp1, tmp2, result, len, i = 0;
	len = a.size();
	tmp1 = a[i];
	result = i;
	tmp2 = a[i];
	for (i = 1; i < len; i++)
	{
		if (a[i] < tmp1)
		{
			tmp1 = a[i];  result = i;
		}
		if (a[i] > tmp2)
			tmp2 = a[i];
	}
	a[result] = tmp2 + 1;
	return  result;
}
map<int, int>& sign(map<int, int>& t, vector<float>& a)
{
	float index, len, rank = 1;
	len = a.size();
	while (len > 0)
	{
		index = sort(a);
		t[index] = rank;
		rank++;
		len--;

	}
	return t;
}
map<vector<float>, float> match(vector<float>& a, vector<vector<float>>& b)
{
	float index, len, i, m, loop = 0, k, rankb, ranke, number = 0;
	double del = 0, gam = 0;
	vector<float> s,s5;
	vector<float> can;
	map<int, int> tmp;
	map<vector<float>, float> mret;
	for (k = 0; k < b.size(); k++)
	{
		len = b[k].size();
		can = b[k];
		sign(tmp, can);
		for (loop; loop <= a.size() - len; loop++)
		{
			i = loop;
			m = i + len;
			s.clear();


			if (i == 0 || s5.empty() == true)
			{
				for (i; i < m; i++)
				{
					if (find(s.begin(), s.end(), a[i]) == s.end())
					{
						s.push_back(a[i]);
				
				    }
			
					else
					{
						fil = true;
						break;
					}
					s5 = s;
				}
			}


			else 
			{
				for (int kl = 1; kl < s5.size(); kl++) 

					{
					s.push_back(s5[kl]);
				    }

					if (find(s.begin(), s.end(), a[m-1]) == s.end())



					{
						s.push_back(a[m-1]);
						s5.clear();
						s5 = s;

					}
           

		
					else
					{
						fil = true;


					}
			}


			if (fil == true)
			{
				fil = false;
				s.clear();
				s5.clear();
				continue;
			}
			index = sort(s);
			rankb = 1;
			ranke = rankb + len;
			del = 0;
			gam = 0;
			for (rankb; rankb < ranke; rankb++)
			{
				del = fabs(rankb - tmp[index]);
				gam = gam + del;
				if (del > delta || gam > gamma) break;
				index = sort(s);
			}
			if (rankb > len) number++;
		}
		if (number >= sup)

		{
			//cout << number << endl;
			mret[b[k]] = number;
			final.push_back(b[k]);
		}

		tmp.clear();
		number = 0;
		can.clear();
		loop = 0;
	}
	return mret;
}
/*map<vector<float>, float> match(vector<float>& a, vector<vector<float>>& b)
{
	float index, len, i, m, loop = 0, k, rankb, ranke, number = 0;
	double del = 0, gam = 0;
	vector<float> s;
	vector<float> can;
	map<int, int> tmp1;
	map<int, int> tmp2;
	map<vector<float>, float> mret;
	for (k = 0; k < b.size(); k++)
	{
		len = b[k].size();
		can = b[k];
		sign(tmp1, can);
		for (loop; loop <= a.size() - len; loop++)
		{
			i = loop;
			m = i + len;
			s.clear();
			for (i; i < m; i++)
			{
				if (find(s.begin(), s.end(), a[i]) == s.end())

				{

					s.push_back(a[i]);

				}
				else
				{
					fil = true;
					break;
				}

			}
			if (fil == true)
			{
				fil = false;
				s.clear();
				continue;
			}
			sign(tmp2, s);
			rankb = 0;
			ranke = rankb + len;
			del = 0;
			gam = 0;
			for (rankb; rankb < ranke; rankb++)
			{
				del = fabs(tmp1[rankb] - tmp2[rankb]);
				gam = gam + del;
				if (del > delta || gam > gamma) break;
			}
			if (rankb > len-1) number++;

		}
		if (number >= sup)

		{
			//cout << number << endl;
			mret[b[k]] = number;
			final.push_back(b[k]);
		}

		tmp1.clear();
		tmp2.clear();
		number = 0;
		can.clear();
		loop = 0;
	}
	return mret;
}*/
vector<vector<float>>  cand_gene(vector<vector<float>>& cand)
{
	float i, j, k, m;
	map<int, int> tmp1, tmp2;
	vector<float> pre, suf, tem;
	vector <vector<float>> result;
	for (i = 0; i < cand.size(); i++)
		for (j = 0; j < cand.size(); j++)
		{
			for (k = 1; k < cand[i].size(); k++)
				suf.push_back(cand[i][k]);
			for (m = 0; m < cand[j].size() - 1; m++)
				pre.push_back(cand[j][m]);
			tmp1 = sign(tmp1, suf);
			tmp2 = sign(tmp2, pre);
			if (tmp1 == tmp2)
			{
				if (cand[i][0] == cand[j][cand[j].size() - 1])
				{
					tem.push_back(cand[i][0] + 1);
					for (int n = 0; n < cand[j].size(); n++)
					{
						if (cand[j][n] > cand[i][0])
							tem.push_back(cand[j][n] + 1);
						else    tem.push_back(cand[j][n]);
					}
					result.push_back(tem);
					tem.clear();
					for (int h = 0; h < cand[i].size(); h++)
					{
						if (cand[i][h] > cand[j][cand[j].size() - 1])
							tem.push_back(cand[i][h] + 1);
						else   tem.push_back(cand[i][h]);
					}
					tem.push_back(cand[j][cand[j].size() - 1] + 1);
					result.push_back(tem);
					tem.clear();
					pre.clear();
					suf.clear();
					tmp1.clear();
					tmp2.clear();
				}
				else if (cand[i][0] > cand[j][cand[j].size() - 1])

				{
					tem.push_back(cand[i][0] + 1);
					for (int h = 0; h < cand[j].size(); h++)
					{
						if (cand[j][h] > cand[i][0])
							tem.push_back(cand[j][h] + 1);
						else   tem.push_back(cand[j][h]);
					}
					result.push_back(tem);
					tem.clear();
					pre.clear();
					suf.clear();
					tmp1.clear();
					tmp2.clear();
				}
				else
				{
					for (int n = 0; n < cand[i].size(); n++)
					{
						if (cand[i][n] > cand[j][cand[j].size() - 1])
							tem.push_back(cand[i][n] + 1);
						else   tem.push_back(cand[i][n]);
					}
					tem.push_back(cand[j][cand[j].size() - 1] + 1);
					result.push_back(tem);
					tem.clear();
					pre.clear();
					suf.clear();
					tmp1.clear();
					tmp2.clear();
				}
			}
			else
			{
				pre.clear();
				suf.clear();
				tmp1.clear();
				tmp2.clear();
			}
		}
	candidate = candidate + result.size();
	return result;
}
vector<vector<float>>  transform(map<vector<float>, float>& mid)
{
	vector<vector<float>> output;
	map<vector<float>, float>::iterator it1;
	for (it1 = mid.begin(); it1 != mid.end(); ++it1)
		output.push_back(it1->first);
	return output;
}
/*void read_file1(vector<int>& s)
{
	char filename[] = "ccc.txt";
	FILE *fin = fopen(filename, "rt");
	int num;
	while (fscanf(fin, "%d", &num) == 1)
	{
		s.push_back(num);
	}
	fclose(fin);
}*/
int read_file()
{
	ifstream infile;//输入流
	string str;
	float a;
	infile.open("ccc.txt");//打开文件
	while (getline(infile, str))//获得一行
	{
		char* p = strtok((char*)str.c_str(), " ");
		while (p != NULL)
		{
			a = atof(p);
			s1.push_back(a);
			p = strtok(NULL, " ");
		}
	}
	infile.close();
	return 0;
}

int main()
{
	vector<vector<float>> cand2, re;
	vector<float> t;
	map<vector<float>, float> midret1;
	vector<vector<float>> midret2;
	vector<vector<float>> midret3;
	for (int k = 1; k < 3; k++)
		t.push_back(k);
	cand2.push_back(t);
	t.clear();
	for (int k = 2; k > 0; k--)
		t.push_back(k);
	cand2.push_back(t);
	cout << "请输入delta,gamma两个参数的值:" << endl;
	cin >> delta >> gamma;
	cout << "请输入支持度:" << endl;
	cin >> sup;
	read_file();

	DWORD begintime = GetTickCount();
	midret1 = match(s1, cand2);




	for (int lop = 3; lop < s1.size(); lop++)
	{
		midret3 = transform(midret1);
		midret2 = cand_gene(midret3);
		midret3.clear();
		midret1.clear();
		midret1 = match(s1, midret2);
		midret2.clear();
	}
	DWORD endtime = GetTickCount();
	for (int m = 0; m < final.size(); m++)
		for (int n = 0; n < final[m].size(); n++)
		{
			cout << final[m][n];
			if (n == final[m].size() - 1)
				cout << endl;
		}
	cout << final.size() << endl;
	cout << candidate << endl;
	cout << "The time-consuming:" << (endtime - begintime)/60000.00 << endl;
	return 0;

}