#include<iostream>
#include<unordered_map>
#include<vector>
#include<map>
#include<fstream>
#include<string>
#include<ctime>
#include<sstream>
#include <windows.h>
#include <psapi.h> // For memory usage
#include <iomanip>
using namespace std;
#define M 100//模式的数量
int minsup = 50;//最小支持度
int maxsup = 200;//最大支持度
int maxlen = 4;//生成模式的最大长度
int num;//每个模式在数据库中的支持度
//
// 每个序列的字符以及使用标识
vector<string> gapstr;
string str = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

vector <int> tempUsed;
struct sequence
{
	string c;
	bool used;

};
//
typedef unordered_map<string, vector<int>*> index_reverse;//定义倒排索引

vector <vector<string>> SDB;
vector <vector<string>>* canArr = new vector <vector<string>>[M];//存储候选模式
vector <string>* subcanArr = new vector <string>[M];//存储候选模式
vector <vector<string>> candidate;

vector <vector<string>> result;
vector <vector<string>> resultfuben;
vector<string>subresult;
//函数声明
void InitSequence(vector<string> s, vector<sequence>& seq);
int getStore(vector<string> SS, vector<string> pattern);
vector<string> extractStrings(const vector<string>& arr, int m, int k);
int compareArrays(const vector<string>& a, const vector<string>& b);
index_reverse* create_index_reverse(vector<string> sequence);//创建倒排索引
int CalcPatternSupport(vector<string> pattern, vector<string> sequence, index_reverse* index);//支持度计算
void min_rareItem();//统计一长度稀有模式
int binary_search(int level, vector<string> cand, int low, int high);//通过二分查找，查找在canArr[level-1]中R出现的首个位置
void gen_candidate(int level);//候选模式生成
void readFile(const string& filename);//读取数据库  
//
// 初始化单个序列
void InitSequence(vector<string> s, vector<sequence>& seq) {
	int l = s.size();
	int i = 0;
	while (i < l)
	{
		sequence se;
		se.c = s[i];
		se.used = false;
		seq.push_back(se);
		i++;
	}
}
int getStore(vector<string> SS, vector<string> pattern) {
	int store = 0;
	int S_len = SS.size();//母串长度
	int P_len = pattern.size();//子串长度
	vector<sequence> sq;
	InitSequence(SS, sq);// 用S初始化队列
	int occc[100];
	//return S_len + P_len;
	int ii = 0;
	for (int j = 0; j < P_len; j++)
	{
		bool gapstr_flag = true;

		int flag = -1;
		while (ii < S_len)
		{
			if (sq[ii].c == pattern[j] && sq[ii].used == false)
			{
				if (j >= 1) {

					for (int xh = occc[j - 1] + 1; xh < ii; xh++) {
						gapstr_flag = false;
						for (int gi = 0; gi < gapstr.size(); gi++) {
							if (gapstr[gi] == sq[xh].c) {
								gapstr_flag = true;
								break;
							}
						}
						if (gapstr_flag == false) {
							break;
						}
					}
					if (gapstr_flag == false) {
						//cout<<"哈哈哈哈哈哈哈"<<endl;
						ii = occc[0] + 1;
						j = -1;
						for (int h = 0; h < P_len; h++)
						{
							occc[h] = 0;
						}
						while (tempUsed.size() > 0) {
							sq[tempUsed.back()].used = false;
							tempUsed.pop_back();
						}
						break;
					}
				}

				flag = 1;
				occc[j] = ii; //保存当前未使用字符的位置
				sq[ii].used = true;
				tempUsed.push_back(ii);
				break;
			}

			ii++;
		}//while
		if (gapstr_flag == false)
			continue;

		if (j == P_len - 1 && ii < S_len)
		{
			tempUsed.clear();
			ii = occc[0]; //你把指针i给重新赋值了，导致了错误
			//cout<<"<";
			for (int h = 0; h < P_len; h++)
			{
				//cout<<occc[h]+1<<",";
				occc[h] = 0;
			}
			//cout<<">"<<endl;
			j = -1;
			store++;
		}

		if (flag == 1)
		{
			ii++;
		}

		if (ii >= S_len)
		{
			break;
		}
	}///for
	//cout<<store<<endl;
	return store;
}
//
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
//index_reverse* create_index_reverse(vector<string> sequence)//创建倒排索引
//{
//	index_reverse* index = new index_reverse;
//	for (size_t i = 0; i < sequence.size(); i++)
//	{
//		if ((*index).find(sequence[i]) == (*index).end()) {
//			vector<int>* v = new vector<int>;
//			v->push_back(i + 1);//数组下标从0开始
//			(*index)[sequence[i]] = v;
//		}
//		else {
//			(*index)[sequence[i]]->push_back(i + 1);//数组下标从0开始
//		}
//	}
//	return index;
//}

////测试函数
//void printIndexReverse(const index_reverse* index) {//打印倒排索引
//	for (const auto& pair : *index) {
//		string key = pair.first;
//		const vector<int>* value = pair.second;
//		cout << "Key: " << key << ", Value: ";
//		for (const auto& element : *value) {
//			cout << element << " ";
//		}
//		cout << endl;
//	}
//}

//int CalcPatternSupport(vector<string> pattern, vector<string> sequence, index_reverse* index)
//{
//	map<string, int> charTimes;//单个字符的出现次数
//	bool has_duplicate = false;//模式是否出现相同字符
//	for (size_t i = 0; i < pattern.size(); i++) {
//		if (charTimes.find(pattern[i]) == charTimes.end()) {//这行表示在map中没找到pattern[i]
//			charTimes[pattern[i]] = 1;
//		}
//		else {
//			charTimes[pattern[i]]++;
//		}
//	}//计算每个字母的出现次数
//	//测试charTimes
//	/*for (const auto& pair : charTimes) {
//		string key = pair.first;
//		int value = pair.second;
//		cout << "Key: " << key << ", Value: " << value << endl;
//	}*/
//	for (auto i = charTimes.begin(); i != charTimes.end(); ++i) {
//		if (i->second > 1) {
//			has_duplicate = true;
//		}
//	}//如果模式中出现相同字母，则重复使用位，置为true
//
//	int support = 0;
//	int* steps = new int[pattern.size() + 1];//记录当前每个走到了哪里//不一样
//	for (size_t i = 0; i < pattern.size(); i++)
//	{
//		steps[i] = 0;
//	}
//
//	vector<int>* useflag;
//	if (has_duplicate) {
//		useflag = new vector<int>(sequence.size() + 1, 0);
//	}
//	else {
//		useflag = nullptr;
//	}
//	//测试完毕
//	while (true)
//	{
//		for (size_t i = 0; i < pattern.size(); i++)
//		{
//			auto curr_next_array = (*index).find(pattern[i]);
//
//			// next没有当前字母的vector行，整个序列没有当前字母，返回
//			if (curr_next_array == (*index).end()) {
//				delete[] steps;
//				if (useflag != nullptr)
//					delete useflag;
//				return support;
//			}
//			// next当前字母行都用过了，后面没有当前字母，返回
//			if ((*curr_next_array).second->size() <= steps[i]) {
//				delete[] steps;
//				if (useflag != nullptr)
//					delete useflag;
//				return support;
//			}
//
//			auto pre_next_array = curr_next_array;
//			if (i > 0) {
//				pre_next_array = (*index).find(pattern[i - 1]);
//			}
//
//			// 当前这个位置比模式前一个字母的这个位置要小，继续往后
//			auto condition_1 = i > 0 && (*(*curr_next_array).second)[steps[i]] <= (*(*pre_next_array).second)[steps[i - 1] - 1];
//			//有重复且当前位置被用过了，继续往后
//			bool condition_2 = false;
//			if (has_duplicate) {
//				condition_2 = (*useflag)[(*(*curr_next_array).second)[steps[i]]] > 0;
//			}
//
//			while (condition_1 || condition_2) {
//				steps[i]++;
//				//如果走到了最后 返回
//				if ((*curr_next_array).second->size() <= steps[i]) {
//					delete[] steps;
//					if (useflag != nullptr)
//						delete useflag;
//					return support;
//				}
//
//				//再次判断当前这个位置是否比模式前一个字母的这个位置要小
//				condition_1 = i > 0 && (*(*curr_next_array).second)[steps[i]] <= (*(*pre_next_array).second)[steps[i - 1] - 1];
//				//如果有重复，再次判断当前位置是否被用过了
//				if (has_duplicate) {
//					condition_2 = (*useflag)[(*(*curr_next_array).second)[steps[i]]] > 0;
//				}
//			}
//			steps[i]++;
//			if (has_duplicate) {
//				(*useflag)[(*(*curr_next_array).second)[steps[i] - 1]]++;
//			}
//		}
//		support++;
//		if (support > maxsup - num)
//		{
//			return support;
//		}
//	}
//}

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
		gapstr.push_back(it->first);//
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
	/*for (int i = 0; i < str.length(); i++) {
		gapstr.push_back(string(1, str[i]));
	}
	gapstr.push_back("NA");*/
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
			for (size_t j = 0; j < SDB.size(); j++)
			{
				//index_reverse* index = create_index_reverse(SDB[j]);
				//printIndexReverse(index);
				//cout << candidate[i] << "在事务"<<j<<"中的支持度" << CalcPatternSupport(candidate[i], SDB[j], index[j])<<endl;
				//num += CalcPatternSupport(candidate[i], SDB[j], index[j]);
				num += getStore(SDB[j], candidate[i]);
				//if (num > maxsup)
				//{
				//	canArr[level].push_back(candidate[i]);
				//	candidatenum++;
				//	break;
				//	//cout << "候选模式  " << candidate[i] << endl;
				//}
			}

			//if (num >= minsup && num <= maxsup)
			//{
			//	canArr[level].push_back(candidate[i]);
			//	candidatenum++;
			//	result.push_back(candidate[i]);
			//	//result[candidate[i]] = num;
			//	//cout << candidate[i] << "在数据库中的支持度为：" << num << endl;
			//}
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
	//聚类数据处理
	/*resultfuben.push_back({ "D" });
	resultfuben.push_back({ "E" });
	resultfuben.push_back({ "B","A","C"});
	resultfuben.push_back({ "C","B","C" });
	resultfuben.push_back({ "C","C","C" });*/
	//vector<vector<int>> aa;//存放每个稀有模式在序列si中的支持度
	//vector<int> a;
	//for (size_t i = 0; i < SDB.size(); i++)
	//{
	//	for (auto it = result.begin(); it != result.end(); it++)
	//	{
	//		vector<string> key = *it;
	//		a.push_back(CalcPatternSupport(key, SDB[i], index[i]));
	//	}
	//	aa.push_back(a);
	//	a.clear();
	//}

	//ofstream outFile("Ocancer.txt");
	//for (const auto& innerVec : aa) {
	//	for (auto it = innerVec.begin(); it != innerVec.end(); ++it) {
	//		outFile << *it;
	//		if (std::next(it) != innerVec.end()) {
	//			outFile << " ";
	//		}
	//	}
	//	outFile << std::endl;
	//}
	//outFile.close();  // 关闭文件流
	//cout << "数据已成功写入文件。" << endl;



}