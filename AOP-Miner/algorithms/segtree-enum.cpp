#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include<vector>
#include <stdio.h>
#include <string.h>
#include <string>
#include <stdint.h>
#include <time.h>
#include <stdlib.h>
#include<crtdbg.h>
#include <math.h>
#include <map>
#include <malloc.h>
#include<fstream>
#include<strstream>
#include <windows.h>
using namespace std;
unsigned int delta, gamma, sup;
vector<float> s1;
bool fil = false;
bool stop = false;
vector < vector<float>> final;
map<vector<float>, vector<float>> midret1;
map<vector<float>, vector<vector<float>>> result;
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
map<int, int> sign(map<int, int>& t, vector<float>& a)
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

map<vector<float>, vector<float>> match2(map<vector<float>, vector<vector<float>>>& a, map<vector<float>, vector<float>>& b)
{
	float index, rankb, ranke, del, gam, j, k, p,number = 0;
	vector<float> can;
	vector<float> pos;
	vector<float> s;
	map<int, int> tmp;
	//map<int, int> tp;
	vector<float> sub;
	map<vector<float>, vector<vector<float>>>::iterator it1;
	//map<vector<float>, vector<vector<float>>>::iterator i1;
	vector<float> kk;
	map<float, float> f;
	//map<float, float> f1;
	map<vector<float>, vector<float>> apos;

	for (it1 = a.begin(); it1 != a.end(); it1++)
	{

		for (p = 0; p < it1->second.size(); p++)
		{
			can = it1->second[p];
			sign(tmp, can);
			kk = b[it1->first];
			for (int m = 0; m < kk.size(); m++)
			{
				for (j = kk[m]; j < kk[m] + it1->second[p].size() && j <= s1.size() - 1; j++)
				{
					if (find(s.begin(), s.end(), s1[j]) == s.end())

					{

						s.push_back(s1[j]);

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
				index = sort(s);
				rankb = 1;
				ranke = rankb + it1->second[p].size();
				del = 0;
				gam = 0;
				for (rankb; rankb < ranke; rankb++)
				{
					del = fabs(rankb - tmp[index]);
					gam = gam + del;
					if (del > delta || gam > gamma) break;
					index = sort(s);
				}
				if (rankb > it1->second[p].size())
				{
					pos.push_back(kk[m]);
					f[kk[m]] = 1;
					number++;
				}
				s.clear();
			}
			//cout << number << endl;
			//kk.clear();
			//kk = b[it1->second[1]];
			for (int n = 0; n < kk.size(); n++)
			{

				if (kk[n] > 0 && f.find(kk[n] - 1) == f.end())
				{

					for (k = kk[n] - 1; k < kk[n] + it1->second[p].size()-1 && k <= s1.size() - 1; k++)
					{
						if (find(s.begin(), s.end(), s1[k]) == s.end())

						{

							s.push_back(s1[k]);

						}
						else
						{
							fil = true;
							break;
						}
					}


				}
				else  continue;
				if (fil == true)
				{
					fil = false;
					s.clear();
					continue;
				}




				index = sort(s);
				rankb = 1;
				ranke = rankb + it1->second[p].size();
				del = 0;
				gam = 0;
				for (rankb; rankb < ranke; rankb++)
				{
					del = fabs(rankb - tmp[index]);
					gam = gam + del;
					if (del > delta || gam > gamma) break;
					index = sort(s);
				}
				if (rankb > it1->second[p].size())
				{
					pos.push_back(kk[n] - 1);
					number++;
				}
				s.clear();
			}

			//cout << number << endl;

			if (number >= sup)

			{

				apos[it1->second[p]] = pos;
				final.push_back(it1->second[p]);
			}

			//cout << p << endl;
			number = 0;
			tmp.clear();
			can.clear();
			kk.clear();
			pos.clear();
			f.clear();


		}


	}

	


	/*map<vector<int>, vector<int>>::iterator it;
	for (it = apos.begin(); it != apos.end(); ++it) {
		for (int o = 0; o < it->first.size(); o++)
			cout << it->first[o];
		   cout << endl;
		   for (int u = 0; u < it->second.size(); u++)
			   cout << it->second[u];
		   cout << endl;
	}*/

	if (apos.size() == 0)
		stop = true;

	//cout << apos.size() << endl;

	return apos;


}





map<vector<float>, vector<float>> match(vector<vector<float>>& b)
{
	float index, len, i, m, loop = 0, k, rankb, ranke, number = 0;
	double del = 0, gam = 0;
	vector<float> s;
	vector<float> can;
	vector<float> pos;
	map<int, int> tmp;
	map<vector<float>, vector<float>> apos;
	for (k = 0; k < b.size(); k++)
	{
		len = b[k].size();
		can = b[k];
		sign(tmp, can);
		for (loop; loop <= s1.size() - len; loop++)
		{
			i = loop;
			m = i + len;
			s.clear();
			for (i; i < m; i++)
			{
				if (find(s.begin(), s.end(), s1[i]) == s.end())

				{

					s.push_back(s1[i]);

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
				vector<float>().swap(s);
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
			if (rankb > len)
			{
				number++;
				pos.push_back(loop);
			}
		}
		if (number >= sup)

		{

			apos[b[k]] = pos;
			final.push_back(b[k]);
		}

		pos.clear();
		tmp.clear();
		number = 0;
		can.clear();
		loop = 0;
	}


	/*map<vector<int>, vector<int>>::iterator it;
	for (it = apos.begin(); it != apos.end(); ++it) {
		cout << it->first[0] << it->first[1] << " " << it->second.size() << endl;
		for(int u=0;u< it->second.size();u++)
		cout <<it->second[u]<< endl;
	}*/




	return apos;
}



vector<vector<float>> trans(map<vector<float>, vector<float>>& cand)
{
	vector<vector<float>> tran;
	map<vector<float>, vector<float>>::iterator it;
	for (it = cand.begin(); it != cand.end(); it++)
		tran.push_back(it->first);
	return tran;

}


map<vector<float>, vector<vector<float>>>  cand_gene(vector<vector<float>>& cand)
{
	float i, j, k, m;
	map<int, int> tmp1, tmp2;
	//map<int, int> tmp3, tmp4;
	vector<float> pre, suf, tem;
	vector<vector<float>>  source;
	//map<vector<float>, vector<vector<float>>> result;
	for (i = 0; i < cand.size(); i++)
	{
		for (k = 1; k <= cand[i].size() + 1; k++)
		{
			for (j = 0; j < cand[i].size(); j++)
			{
				if (cand[i][j] >= k)
					tem.push_back(cand[i][j] + 1);
				else
					tem.push_back(cand[i][j]);


			}
			tem.push_back(k);
			source.push_back(tem);
			tem.clear();
		}
		result[cand[i]] = source;
		candidate = candidate + source.size();
		//cout << source.size() << endl;
		source.clear();


	}



	return result;
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
	//map<vector<float>, vector<float>> midret1;
	//map<vector<float>, vector<float>> midret3;
	//map<vector<float>, vector<vector<float>>> midret2;
	//vector<vector<float>> tran1;



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
	//cout << s1.size() << endl;

	DWORD begintime = GetTickCount();


	//midret1 = match(cand2);


	//midret3 = midret1;


	for (int lop = 2; lop < s1.size() - 1; lop++)
	{
		map<vector<float>, vector<vector<float>>> midret2;
		map<vector<float>, vector<float>> midret3;
		vector<vector<float>> tran1;
		if (lop == 2)
		{
			midret1 = match(cand2);
		}
		else
		{
			midret3 = midret1;
			tran1 = trans(midret1);
			midret2 = cand_gene(tran1);
			result.clear();
			midret1.clear();
			midret1 = match2(midret2, midret3);
			if (stop == true) break;
		}

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










