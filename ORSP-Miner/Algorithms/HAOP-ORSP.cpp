#include<iostream>
#include<unordered_map>
#include<vector>
#include<map>
#include<fstream>
#include<string>
#include<ctime>
#include<sstream>
#include<queue>
#include <windows.h>
#include <psapi.h> // For memory usage
#include <iomanip>
using namespace std;
#define M 100//模式的数量
int minsup = 50;//最小支持度
int maxsup = 200;//最大支持度
int maxlen = 4;//生成模式的最大长度
int num;//每个模式在数据库中的支持度
typedef unordered_map<string, vector<int>*> index_reverse;//定义倒排索引

vector <vector<string>> SDB;
vector <vector<string>>* canArr = new vector <vector<string>>[M];//存储候选模式
vector <string>* subcanArr = new vector <string>[M];//存储候选模式
vector <vector<string>> candidate;

vector <vector<string>> result;
vector <vector<string>> resultfuben;
vector<string>subresult;
//
int s_length;
struct pant_p         //nettree node
{
	string name;     //The corresponding position of node in sequence
	queue<int> que_pan;
};
vector <pant_p> link_pan;
int ptn_len;
int occnum = 0;
vector<string> S;
//
//函数声明
void Creat_ptn(vector<string> p, int ptn_len);
int no_que(int len_s, int len_p);
vector<string> extractStrings(const vector<string>& arr, int m, int k);
int compareArrays(const vector<string>& a, const vector<string>& b);
//index_reverse* create_index_reverse(vector<string> sequence);//创建倒排索引
//int CalcPatternSupport(vector<string> pattern, vector<string> sequence, index_reverse* index);//支持度计算
void min_rareItem();//统计一长度稀有模式
int binary_search(int level, vector<string> cand, int low, int high);//通过二分查找，查找在canArr[level-1]中R出现的首个位置
void gen_candidate(int level);//候选模式生成
void readFile(const string& filename);//读取数据库  

void Creat_ptn(vector<string> p, int ptn_len) {
	for (int i = 0; i < ptn_len; i++) {
		pant_p  pan;
		memset(&pan, 0, sizeof(pan));
		pan.name = string(p[i]);
		link_pan.push_back(pan);
	}

}
int no_que(int len_s, int len_p) {
	occnum = 0;
	int k = 0;
	for (int i = 0; i < len_s; i++)
	{
		if (S[i] == link_pan[0].name)
		{
			k = i;
			break;
		}
	}
	
	for (; k < len_s; k++)
	{

		int postion = 0;
		for (int m = ptn_len - 1; m > 0; m--)//
		{
			//cout << S[k] <<k<< link_pan[m].name<< m<< link_pan[m].que_pan.size() << link_pan[m - 1].que_pan.size() << endl;
			if (S[k] == link_pan[m].name && link_pan[m].que_pan.size() < link_pan[m - 1].que_pan.size())
			{
				link_pan[m].que_pan.push(k);
				postion = m;
				break;
			}

		}
		if (postion == 0 && S[k] == link_pan[0].name) {
			link_pan[0].que_pan.push(k);
		}
		if (postion == ptn_len - 1) {

			occnum++;
		}
	}
	//	link_pan.clear();
		/*
		for ( k = 0; k < link_pan.size();k++)
		{
			clear_vector_que(link_pan[k].que_pan);
		}
		//cout << occnum << endl;
		*/
	return occnum;
}

vector<string> extractStrings(const vector<string>& arr, int m, int k) {
	vector<string> result;
	for (int i = m; i < m + k && i < arr.size(); ++i) {
		result.push_back(arr[i]);
	}
	return result;
}

int compareArrays(const vector<string>& a, const vector<string>& b) {
	if (std::lexicographical_compare(a.begin(), a.end(), b.begin(), b.end())) {
		return -1;  // a < b
	}
	else if (std::lexicographical_compare(b.begin(), b.end(), a.begin(), a.end())) {
		return 1;   // a > b
	}
	else {
		return 0;   // a == b
	}
}


void min_rareItem()//将一长度的模式添加到候选集
{
	map<string, int> counter;//这里类型使用string的原因是为了加入到canArr的键中，类型需要匹配
	string mine;
	for (size_t j = 0; j < SDB.size(); j++)
	{
		for (size_t i = 0; i < SDB[j].size(); i++)
		{
			mine = SDB[j][i];
			counter[mine]++;
		}
	}
	int cand1 = 0;
	for (map<string, int>::iterator it = counter.begin(); it != counter.end(); it++)
	{
		cout << it->first << "出现次数为：" << it->second << endl;
		if (it->second >= minsup)
		{
			subcanArr[0].push_back(it->first);
			canArr[0].push_back(subcanArr[0]);
			cand1++;
		}
		if (it->second >= minsup && it->second <= maxsup)
		{
			subresult.push_back(it->first);
			result.push_back(subresult);
		}
		subcanArr[0].clear();
		subresult.clear();
	}
	cout << "一长度候选模式数量：" << cand1 << endl;
}

int binary_search(int level, vector<string> cand, int left, int right)
{
	int result = -1;
	while (left <= right) {
		int mid = left + (right - left) / 2;

		if (compareArrays(cand, extractStrings(canArr[level - 1][mid], 0, level - 1)) == 0) {
			result = mid;
			right = mid - 1;
		}
		else if (compareArrays(cand, extractStrings(canArr[level - 1][mid], 0, level - 1)) > 0) {
			left = mid + 1;
		}
		else {
			right = mid - 1;
		}
	}
	return result;
}

void gen_candidate(int level)
{
	int size = canArr[level - 1].size();
	int start = 0;
	//cout << "canArr size:" << size << endl;
	for (int i = 0; i < size; i++)
	{
		vector<string> Q = { " " }, R = { " " };
		//R = canArr[level - 1][i].substr(1, level - 1);  //suffix pattern of freArr[level-1][i] 第1个位置后面level-1个字符赋给R
		//Q = canArr[level - 1][start].substr(0, level - 1);   //prefix pattern of freArr[level-1][start]
		R = extractStrings(canArr[level - 1][i], 1, level - 1);
		Q = extractStrings(canArr[level - 1][start], 0, level - 1);
		if (Q != R)
		{
			start = binary_search(level, R, 0, size - 1);	//通过二分查找，查找在canArr[level-1]中R出现的首个位置
		}
		if (start < 0 || start >= size)
		{
			start = 0;
		}
		else
		{
			Q = extractStrings(canArr[level - 1][start], 0, level - 1);//找到新的起始位置
			while (Q == R)
			{

				vector<string> candPrefix = extractStrings(canArr[level - 1][i], 0, level);
				vector<string> candSuffix = extractStrings(canArr[level - 1][start], level - 1, 1);
				//cand = cand + canArr[level - 1][start].substr(level - 1, 1);//模式连接
				candPrefix.insert(candPrefix.end(), candSuffix.begin(), candSuffix.end());
				candidate.push_back(candPrefix);	//自动将cand插入向量candidate末尾

				start = start + 1;
				if (start >= size)
				{
					start = 0;
					break;
				}
				Q = extractStrings(canArr[level - 1][start], 0, level - 1);//后移一个字符串
			}
		}
	}
}

void readFile(const string& filename)
{
	ifstream file(filename);  // 打开文件
	if (file.is_open()) {
		string line;
		while (getline(file, line)) {
			vector<string> tokens;
			istringstream iss(line);
			string token;
			while (iss >> token) {
				tokens.push_back(token);
			}
			SDB.push_back(tokens);
		}
		file.close();  // 关闭文件
	}
	else {
		cout << "打开文件错误";
		// 如果打开文件失败，可以在这里处理错误
		// 例如输出错误信息或抛出异常
	}
}
void PrintMemoryUsage()
{
	PROCESS_MEMORY_COUNTERS pmc;
	GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc));
	cout << "Memory Usage: " << fixed << setprecision(2) << pmc.WorkingSetSize / (1024.0 * 1024.0) << " Mb" << endl;
}
int main()
{
	readFile("D:\\研究生(李昊)\\my code\\my dataset\\Ocancer.txt");  // 将文件内容读入到向量中
	clock_t start = clock();
	min_rareItem();
	int level = 1;
	/*index_reverse** index = new index_reverse * [SDB.size() + 1];

	for (size_t i = 0; i < SDB.size(); i++)
	{
		index[i] = create_index_reverse(SDB[i]);
	}*/

	while (true)
	{
		gen_candidate(level);
		int candidatenum = 0;
		for (size_t i = 0; i < candidate.size(); i++)
		{
			num = 0;
			vector<string> p = candidate[i];
			ptn_len = p.size();
			
			for (size_t j = 0; j < SDB.size(); j++)
			{
				
				Creat_ptn(p, ptn_len);
				S = SDB[j];
				s_length = S.size();
				num+= no_que(s_length, ptn_len);
				link_pan.clear();
			}
			
		
			if (num >= minsup && num <= maxsup)
			{
				result.push_back(candidate[i]);
				//cout << candidate[i] << "在数据库中的支持度为：" << num << endl;
			}
			if (num >= minsup)
			{
				canArr[level].push_back(candidate[i]);
				candidatenum++;
				//cout << "候选模式  " << candidate[i] << endl;
			}
		}
		cout << "候选模式数量：" << candidatenum << endl;
		level++;
		candidate.clear();
		if (level >= maxlen)
		{
			break;
		}
	}
	PrintMemoryUsage();
	clock_t end = clock();
	double timeInSeconds = double(end - start);//CLOCKS_PER_SEC
	cout << "运行时间" << timeInSeconds << "ms" << endl;
	cout << "结果集：" << endl;
	int resultsum = 0;
	for (auto it1 = result.begin(); it1 != result.end(); it1++)
	{
		for (auto it2 = it1->begin(); it2 != it1->end(); it2++)
		{
			cout << *it2 << " ";
		}
		cout << endl;
		resultsum++;
	}
	cout << "结果集个数：" << resultsum << endl;
	cout << "SDB " << SDB.size() << endl;

}