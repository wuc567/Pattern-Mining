#include<iostream>
#include<unordered_map>
#include<vector>
#include <map>
#include<set>
#include<sstream>
#include<fstream>
#include<queue>
#include <algorithm>
#include<unordered_set>
using namespace std;
time_t calc_next_time;
//һЩ����
double r = 0.035;
int k = 10;
string file = "d:/�����㷨/pattern-mining-master/scp-miner/dataset/BF.txt";
int classified = 1;//�����Ѿ�����
vector<string> totalseq, posseq, negseq;
typedef unordered_map<char, vector<int>*> inverted_index;
vector< inverted_index*> posindex, negindex;
set<char> single_pattern;//����һ��set�����������������Ա�֤�ھ������ģʽ���ظ���
struct Pattern {
	string P;
	double RatePos;
	double RateNeg;
	double Contrast;

	bool operator<(const Pattern& p)const {
		return Contrast < p.Contrast;
	}
};
vector<Pattern> pattern;
double CalcPatternDensity(string pattern, string sequence, inverted_index* index);
struct rule {
	bool operator()(Pattern a, Pattern b)const {//���˳����ʲô����
		return a.Contrast > b.Contrast;
	}
};
priority_queue<Pattern, vector<Pattern>, rule>F1, F2, F;
bool PatternGreater(Pattern& p1, Pattern& p2) {
	return p1.Contrast > p2.Contrast;
}
set<string> addedPatterns;

int total_candidate_count = 0;

//��������
void readfile();
inverted_index* createindex(string s);
void printindex(inverted_index* index);
void character_mining();
double CalcPatternRate(string pattern, vector<string> sequenceSet, vector<inverted_index*>& indexset, double r);


inverted_index* createindex(string s) {
	inverted_index* index = new inverted_index;
	for (int i = 0; i < s.length(); i++) {
		if ((*index).find(s[i]) == (*index).end()) {
			vector<int>* v = new vector<int>;
			v->push_back(i + 1);
			(*index)[s[i]] = v;
		}
		else {
			(*index)[s[i]]->push_back(i + 1);
		}
	}
	return index;
}

void readfile()
{
	ifstream ifs;
	cout << "�ļ�����" << file << endl;
	ifs.open(file, ios::in);
	string buf;
	while (ifs >> buf) {
		totalseq.push_back(buf);
	}
	ifs.close();
	for (int i = 0; i < 1; i++) {
		if (totalseq[i][0] >= 65) {
			classified = 2;
		}
	}
	if (classified == 1) {
		for (int i = 0; i < totalseq.size(); i++) {
			if (totalseq[i][0] == '1') {
				string s = totalseq[i].substr(1);
				posseq.push_back(s);
				inverted_index* index = createindex(s);
				posindex.push_back(index);


			}
			if (totalseq[i][0] == '2') {
				string s = totalseq[i].substr(1);
				negseq.push_back(s);
				inverted_index* index = createindex(s);
				negindex.push_back(index);
			}
		}
	}
	else {
		for (int i = 0; i < totalseq.size(); i++) {
			if (i < 14) {
				posseq.push_back(totalseq[i]);
				inverted_index* index = createindex(totalseq[i]);
				posindex.push_back(index);
			}
			else {
				negseq.push_back(totalseq[i]);
				inverted_index* index = createindex(totalseq[i]);
				negindex.push_back(index);
			}
		}
	}
}

void character_mining() {
	for (int i = 0; i < totalseq.size(); i++) {
		for (int j = 0; j < totalseq[i].length(); j++) {
			single_pattern.insert(totalseq[i][j]);//�����ھ����д���set������
		}
	}
	pattern.reserve(single_pattern.size()); // Ԥ�����㹻���ڴ�ռ�
	for (const auto& ch : single_pattern) {//����set��������������ַ�����vector������
		Pattern temp;
		temp.P = ch;//����һ������,�������vector������
		pattern.push_back(std::move(temp)); // ʹ�� std::move ���ⲻ��Ҫ�ĸ���
	}
	for (const auto& pat : pattern) {
		cout << pat.P << endl;
	}
	cout << endl; // ������з�
}

double  CalcPatternDensity(string pattern, string sequence, inverted_index* index)//�����ܶ�
{
	int support = 0;
	int* s = new int[pattern.length()]();//��¼ÿ���ַ���λ������
	for (auto i = 0; i < pattern.length(); i++) {
		s[i] = 0;
	}
	int pos = 0;//��û�ҵ�
	while (true)
	{
		for (int i = 0; i < pattern.length(); i++)
		{
			auto m = (*index).find(pattern[i]);//��¼��ǰ�ַ���ָ��ĵ�������

			if (m == (*index).end()) {//�Ҳ���
				delete[] s;
				return double(support) / sequence.length();
			}
			if ((*m).second->size() < (s[i] + 1)) {//Խ��
				delete[] s;
				return double(support) / sequence.length();
			}
			if (i == 0)//����ǵ�һ���ַ�
			{
				if (sequence.length() - pos < pattern.length()) {//������ں�����ַ�����С��ģʽ�ַ�����
					delete[] s;
					return double(support) / sequence.length();
				}
				while (pos >= (*(*m).second)[s[i]])//���˵pos�ȵ�ǰ��һ���ַ�λ��Ҫ��ָ����ơ�ע�⵹�����������õ��Ǵ�1��ʼ��(*(*m).second)[s[0]])�տ�ʼ��1
				{
					s[i]++;
					if ((*m).second->size() < (s[i] + 1)) {//ֻҪ���ƾ�Ҫ�ж��Ƿ�Խ��
						delete[] s;
						return double(support) / sequence.length();
					}
				}
			}

			auto n = m;
			if (i > 0) {
				n = (*index).find(pattern[i - 1]);//����ǰһ���ַ��ĵ�������
			}

			auto condition = i > 0 && (*(*m).second)[s[i]] <= (*(*n).second)[s[i - 1]]; //��һ���ַ�λ��Ҫ��ǰһ����

			while (condition) {
				s[i]++;
				if ((*m).second->size() < (s[i] + 1)) {
					delete[] s;
					return double(support) / sequence.length();
				}
				condition = i > 0 && (*(*m).second)[s[i]] <= (*(*n).second)[s[i - 1]];
			}
			if (i == (pattern.length() - 1))//��¼���� ÿ��ģʽ���һ���ַ����ֵ�λ��
			{
				pos = (*(*m).second)[s[i]];
			}

		}
		support++;

	}
}


//double  CalcPatternDensity(string pattern, string sequence, inverted_index* index)//�����ܶ�
//{
//	int support = 0;
//	int* s = new int[pattern.length()]();//��¼ÿ���ַ���λ������
//	for (auto i = 0; i < pattern.length(); i++) {
//		s[i] = 0;
//	}
//	int pos = 0;//��û�ҵ�
//	while (true)
//	{
//		for (int i = 0; i < pattern.length(); i++)
//		{
//			auto m = (*index).find(pattern[i]);//��¼��ǰ�ַ���ָ��ĵ�������
//
//			if (m == (*index).end()) {//�Ҳ���
//				delete[] s;
//				return double(support) / sequence.length();
//			}
//			if ((*m).second->size() <= s[i]) {//Խ��
//				delete[] s;
//				return double(support) / sequence.length();
//			}
//			if (i == 0)//����ǵ�һ���ַ�
//			{
//				
//				while (pos >= (*(*m).second)[s[i]])//���˵pos�ȵ�ǰ��һ���ַ�λ��Ҫ��ָ����ơ�ע�⵹�����������õ��Ǵ�1��ʼ��(*(*m).second)[s[0]])�տ�ʼ��1
//				{
//					s[i]++;
//					if ((*m).second->size() <= s[i]) {//ֻҪ���ƾ�Ҫ�ж��Ƿ�Խ��
//						delete[] s;
//						return double(support) / sequence.length();
//					}
//				}
//			}
//
//			auto n = m;
//			if (i > 0) {
//				n = (*index).find(pattern[i - 1]);//����ǰһ���ַ��ĵ�������
//			}
//
//			auto condition = i > 0 && (*(*m).second)[s[i]] <= (*(*n).second)[s[i - 1]-1]; //��һ���ַ�λ��Ҫ��ǰһ����
//
//			while (condition) {
//				s[i]++;
//				if ((*m).second->size() <= s[i]) {
//					delete[] s;
//					return double(support) / sequence.length();
//				}
//				condition = i > 0 && (*(*m).second)[s[i]] <= (*(*n).second)[s[i - 1]-1];
//			}
//			if (i == (pattern.length() - 1))//��¼���� ÿ��ģʽ���һ���ַ����ֵ�λ��
//			{
//				pos = (*(*m).second)[s[i]];
//			}
//			s[i]++;
//		}
//		support++;
//
//	}
//}


//����ģʽ���ܶȺ�֧���ʣ�����ģʽ����ǰ���м�����ǰ���м��ĵ���������������r
double CalcPatternRate(string pattern, vector<string> sequenceSet, vector<inverted_index*>& indexset, double r) {
	if (sequenceSet.size() == 0) {
		return 0;
	}
	int count = 0;
	int exist = 0;//���������
	for (int i = 0; i < sequenceSet.size(); i++) {
		if (pattern.length() <= sequenceSet[i].length()) {
			exist = 1;
			break;//һ�����ڰ�����ϵ������ѭ��ִ�������
		}
	}
	if (exist == 0)
		return 0;
	for (int i = 0; i < sequenceSet.size(); i++) {
		double temp_r;
		temp_r = CalcPatternDensity(pattern, sequenceSet[i], indexset[i]);
		if (temp_r >= r) {//�ܶȴ��ڸ���ֵ�ģ���¼һ��count
			count++;
		}
	}
	return double(count) / sequenceSet.size();
}

void Top_k_Pos(double r, int k) {
	int candidate_count = 0;
	priority_queue<Pattern> G;//�󶥶�
	vector<Pattern> E;//����size=1����֧���ʴ���0��ģʽ����
	for (auto i = pattern.begin(); i != pattern.end(); i++) {
		(*i).RatePos = CalcPatternRate((*i).P, posseq, posindex, r);
		(*i).RateNeg = CalcPatternRate((*i).P, negseq, negindex, r);
		(*i).Contrast = (*i).RatePos - (*i).RateNeg;//���������ַ��ĶԱȶ�

		if (i->RatePos > 0) {//������С֧���ʼ�֦����
			G.push(*i);//�����ѡģʽ��
			candidate_count++;
		}
		if (i->RatePos > 0) {//�������֦����
			E.push_back(*i);
		}
		if ((F1.size() < k && (*i).Contrast > 0) || (F1.size() >= k && (*i).Contrast > F1.top().Contrast)) {//�Աȶ����Ȳ���
			if (F1.size() >= k) {//�������F������ֻҪ�Աȶȴ���0���ܼӽ���������Ѿ����ˣ�����Ҫ����Fջ��Ԫ�صĶԱȶȲ��ܼӽ���
				F1.pop();
			}
			F1.push(*i);
		}
	}
	sort(E.begin(), E.end(), PatternGreater);//С����
	while (!G.empty()) {//ֻҪ��ѡģʽ���ϲ�Ϊ�գ�����������ö��
		Pattern p = G.top();
		G.pop();
		for (auto j = E.begin(); j != E.end(); j++) {
			Pattern q;
			q.P = p.P + j->P;
			q.RatePos = CalcPatternRate(q.P, posseq, posindex, r);
			if (q.RatePos == 0 || (F1.size() >= k && q.RatePos <= F1.top().Contrast)) {
				continue;//���������ھ����˵��������֧���ʵ���0����F1�Ѿ����ˣ�������֧����С�ڵ���F1��ջ��Ԫ�صĶԱȶȣ���֦��
			}
			q.RateNeg = CalcPatternRate(q.P, negseq, negindex, r);
			q.Contrast = q.RatePos - q.RateNeg;
			G.push(q);//�ȼ��뵽��ѡģʽ��
			candidate_count++;
			if ((F1.size() < k && q.Contrast > 0) || (F1.size() >= k && q.Contrast > F1.top().Contrast)) {
				if (F1.size() >= k) {
					F1.pop();
				}
				F1.push(q);
			}
		}
	}


	total_candidate_count += candidate_count;
	while (!F1.empty()) {
		string m = F1.top().P;
		cout << "F1.top():" << F1.top().P << ":" << F1.top().Contrast << endl;
		F.push(F1.top());
		F1.pop();
		if (addedPatterns.find(m) == addedPatterns.end()) {//�����Ǵ���һ��set�����У���֤���ظ�
			addedPatterns.insert(m);
			//cout << "Adding pattern: " << m  << endl;
		}
	}
	cout << "���ɵ������ѡģʽ������" << candidate_count << endl;
}


int main()
{
	readfile();
	character_mining();
	clock_t start, end;//����clock_t����
	start = clock();//��ʼʱ��
	 Top_k_Pos(r, k);
	 	while (!F.empty()) {
 		for (int i = 1; i <= 10; i++) {
 			cout << "string pattern" << i << "=" << "\"" << F.top().P << "\"" << "; " << F.top().Contrast << endl;
 			F.pop();
 		}
 	}
	end = clock();   //����ʱ��
	cout << "time = " << double(end - start) / CLOCKS_PER_SEC << "s" << endl;  //���ʱ�䣨��λ����
	system("pause");
	return 0;
}