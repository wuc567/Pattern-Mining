#include<iostream>
#include<unordered_map>
#include<vector>
#include<map>
#include<fstream>
#include<string>
#include<ctime>
#include<sstream>
#include <cstdlib>
#include <windows.h>
#include <psapi.h> // For memory usage
#include <iomanip>
using namespace std;
#define M 100//模式的数量
int minsup = 50;//最小支持度
int maxsup = 180;//最大支持度
int maxlen = 4;//生成模式的最大长度
int num;//每个模式在数据库中的支持度
int support = 0;
typedef unordered_map<string, vector<int>*> index_reverse;//定义倒排索引

vector <vector<string>> SDB;
vector <vector<string>>* canArr = new vector <vector<string>>[M];//存储候选模式
vector <string>* subcanArr = new vector <string>[M];//存储候选模式
vector <vector<string>> candidate;

vector <vector<string>> result;
vector <vector<string>> resultfuben;
vector<string>subresult;
map<string, int> counter;//这里类型使用string的原因是为了加入到canArr的键中，类型需要匹配
int candidatenum = 0;
//函数声明
vector<string> extractStrings(const vector<string>& arr, int m, int k);
int compareArrays(const vector<string>& a, const vector<string>& b);
index_reverse* create_index_reverse(vector<string> sequence);//创建倒排索引
int CalcPatternSupport(vector<string> pattern, vector<string> sequence, index_reverse* index);//支持度计算
void min_rareItem();//统计一长度稀有模式
int binary_search(int level, vector<string> cand, int low, int high);//通过二分查找，查找在canArr[level-1]中R出现的首个位置
void gen_candidate(int level);//候选模式生成
void readFile(const string& filename);//读取数据库  

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
index_reverse* create_index_reverse(vector<string> sequence)//创建倒排索引
{
	index_reverse* index = new index_reverse;
	for (size_t i = 0; i < sequence.size(); i++)
	{
		if ((*index).find(sequence[i]) == (*index).end()) {
			vector<int>* v = new vector<int>;
			v->push_back(i + 1);//数组下标从0开始
			(*index)[sequence[i]] = v;
		}
		else {
			(*index)[sequence[i]]->push_back(i + 1);//数组下标从0开始
		}
	}
	return index;
}

//测试函数
void printIndexReverse(const index_reverse* index) {//打印倒排索引
	for (const auto& pair : *index) {
		string key = pair.first;
		const vector<int>* value = pair.second;
		cout << "Key: " << key << ", Value: ";
		for (const auto& element : *value) {
			cout << element << " ";
		}
		cout << endl;
	}
}

int CalcPatternSupport(vector<string> pattern, vector<string> sequence, index_reverse* index)
{
	map<string, int> charTimes;//单个字符的出现次数
	bool has_duplicate = false;//模式是否出现相同字符
	for (size_t i = 0; i < pattern.size(); i++) {
		if (charTimes.find(pattern[i]) == charTimes.end()) {//这行表示在map中没找到pattern[i]
			charTimes[pattern[i]] = 1;
		}
		else {
			charTimes[pattern[i]]++;
		}
	}//计算每个字母的出现次数
	//测试charTimes
	/*for (const auto& pair : charTimes) {
		string key = pair.first;
		int value = pair.second;
		cout << "Key: " << key << ", Value: " << value << endl;
	}*/
	for (auto i = charTimes.begin(); i != charTimes.end(); ++i) {
		if (i->second > 1) {
			has_duplicate = true;
		}
	}//如果模式中出现相同字母，则重复使用位，置为true


	int* steps = new int[pattern.size() + 1];//记录当前每个走到了哪里//不一样
	for (size_t i = 0; i < pattern.size(); i++)
	{
		steps[i] = 0;
	}

	vector<int>* useflag;
	if (has_duplicate) {
		useflag = new vector<int>(sequence.size() + 1, 0);
	}
	else {
		useflag = nullptr;
	}
	//测试完毕
	while (true)
	{
		for (size_t i = 0; i < pattern.size(); i++)
		{
			auto curr_next_array = (*index).find(pattern[i]);

			// next没有当前字母的vector行，整个序列没有当前字母，返回
			if (curr_next_array == (*index).end()) {
				delete[] steps;
				if (useflag != nullptr)
					delete useflag;
				return support;
			}
			// next当前字母行都用过了，后面没有当前字母，返回
			if ((*curr_next_array).second->size() <= steps[i]) {
				delete[] steps;
				if (useflag != nullptr)
					delete useflag;
				return support;
			}

			auto pre_next_array = curr_next_array;
			if (i > 0) {
				pre_next_array = (*index).find(pattern[i - 1]);
			}

			// 当前这个位置比模式前一个字母的这个位置要小，继续往后
			auto condition_1 = i > 0 && (*(*curr_next_array).second)[steps[i]] <= (*(*pre_next_array).second)[steps[i - 1] - 1];
			//有重复且当前位置被用过了，继续往后
			bool condition_2 = false;
			if (has_duplicate) {
				condition_2 = (*useflag)[(*(*curr_next_array).second)[steps[i]]] > 0;
			}

			while (condition_1 || condition_2) {
				steps[i]++;
				//如果走到了最后 返回
				if ((*curr_next_array).second->size() <= steps[i]) {
					delete[] steps;
					if (useflag != nullptr)
						delete useflag;
					return support;
				}

				//再次判断当前这个位置是否比模式前一个字母的这个位置要小
				condition_1 = i > 0 && (*(*curr_next_array).second)[steps[i]] <= (*(*pre_next_array).second)[steps[i - 1] - 1];
				//如果有重复，再次判断当前位置是否被用过了
				if (has_duplicate) {
					condition_2 = (*useflag)[(*(*curr_next_array).second)[steps[i]]] > 0;
				}
			}
			steps[i]++;
			if (has_duplicate) {
				(*useflag)[(*(*curr_next_array).second)[steps[i] - 1]]++;
			}
		}
		support++;
		if (support > maxsup - num)
		{
			return support;
		}
	}



}

void min_rareItem()//将一长度的模式添加到候选集
{

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

void rarepattern(vector<string> p, int num)
{
	index_reverse** index = new index_reverse * [SDB.size() + 1];
	for (size_t i = 0; i < SDB.size(); i++)
	{
		index[i] = create_index_reverse(SDB[i]);
	}

	vector<string> q;
	for (int k = 0; k < canArr[0].size(); k++)
	{
		vector<string> e = canArr[0][k];
		for (int j = 0; j < e.size(); j++)
		{
			q = p;
			q.push_back(e[j]);
			//cout << "e[j]:" << e[j]<<endl;
			candidatenum++;
			support = 0;

			for (size_t j = 0; j < SDB.size(); j++)
			{
				CalcPatternSupport(q, SDB[j], index[j]);
				if (support > maxsup)
				{
					break;
				}
			}
			/*cout << "pattern:";
			for (const auto& str : q) {
				cout  << str << " ";
			}*/
			//cout << "support:" << support << endl;
			if (support >= minsup && support <= maxsup)
			{
				result.push_back(q);

			}
			//cout << "q.size:" << q.size() << endl;
			if (support >= minsup && q.size() < maxlen)
			{
				rarepattern(q, support);
			}
		}
		q.clear();
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
	int b = 0;
	for (int k = 0; k < canArr[0].size(); k++)
	{
		vector<string>p;
		vector<string> e = canArr[0][k];
		for (int j = 0; j < e.size(); j++)
		{
			//cout << "主函数：" << e[j] << endl;
			p.push_back(e[j]);
		}
		int num = 0;
		rarepattern(p, num);
		p.clear();
		//cout << "b:" << b << "num:" << num << endl;
	}
	cout << "候选模式数量：" << candidatenum << endl;
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