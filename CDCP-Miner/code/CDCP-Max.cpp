//#include<iostream>
//#include<unordered_map>
//#include<vector>
//#include <map>
//#include<set>
//#include<sstream>
//#include<fstream>
//#include<queue>
//#include <algorithm>
//#include<unordered_set>
//#include <ctime>
//#include <iomanip>
//#include <windows.h>
//#include <psapi.h> // For memory usage
//using namespace std;
//time_t calc_next_time;
////һЩ����
//double r = 0.06;
//int k = 10;
//string file = "d:/�����㷨/pattern-mining-master/scp-miner/dataset/gene.txt";
//int classified = 1;//�����Ѿ�����
//vector<string> totalseq, posseq, negseq;
//typedef unordered_map<char, vector<int>*> inverted_index;
//vector< inverted_index*> posindex, negindex;
//set<char> single_pattern;//����һ��set�����������������Ա�֤�ھ������ģʽ���ظ���
//struct Pattern {
//	string P;
//	double RatePos;
//	double RateNeg;
//	double Contrast;
//	Pattern() : RatePos(0.0), RateNeg(0.0), Contrast(0.0) {}
//
//	Pattern(string p) : P(p), RatePos(0.0), RateNeg(0.0), Contrast(0.0) {}
//	bool operator<(const Pattern& p)const {
//		return Contrast < p.Contrast;
//	}
//};
//vector<Pattern> pattern;
//
//struct rule {
//	bool operator()(Pattern a, Pattern b)const {//���˳����ʲô����
//		return a.Contrast > b.Contrast;
//	}
//};
//priority_queue<Pattern, vector<Pattern>, rule>F1, F2, F;
//bool PatternGreater(Pattern& p1, Pattern& p2) {
//	return p1.Contrast > p2.Contrast;
//}
//set<string> addedPatterns;
//
//int total_candidate_count = 0;
//
////��������
//void readfile();
//inverted_index* createindex(string s);
//void character_mining();
//double CalcPatternDensity(string& pattern, string& sequence, inverted_index* index, double& r);
//double CalcPatternRate1(string& pattern, vector<string>& sequenceSet, vector<inverted_index*>& indexset, double& r, double& value);
//
//double Top_k_Pos(double r, int k);
//void Top_k_Neg(double r, int k, double pos_minContrast);
//
//inverted_index* createindex(string s) {
//	inverted_index* index = new inverted_index;
//	for (int i = 0; i < s.length(); i++) {
//		if ((*index).find(s[i]) == (*index).end()) {
//			vector<int>* v = new vector<int>;
//			v->push_back(i + 1);
//			(*index)[s[i]] = v;
//		}
//		else {
//			(*index)[s[i]]->push_back(i + 1);
//		}
//	}
//	return index;
//}
//
//void readfile()
//{
//	ifstream ifs;
//	cout << "�ļ�����" << file << endl;
//	ifs.open(file, ios::in);
//	string buf;
//	while (ifs >> buf) {
//		totalseq.push_back(buf);
//	}
//	ifs.close();
//	for (int i = 0; i < 1; i++) {
//		if (totalseq[i][0] >= 65) {
//			classified = 2;
//		}
//	}
//	if (classified == 1) {
//		for (int i = 0; i < totalseq.size(); i++) {
//			if (totalseq[i][0] == '1') {
//				string s = totalseq[i].substr(1);
//				posseq.push_back(s);
//				inverted_index* index = createindex(s);
//				posindex.push_back(index);
//			}
//			if (totalseq[i][0] == '2') {
//				string s = totalseq[i].substr(1);
//				negseq.push_back(s);
//				inverted_index* index = createindex(s);
//				negindex.push_back(index);
//			}
//		}
//	}
//	else {
//		for (int i = 0; i < totalseq.size(); i++) {
//			if (i < 100) {
//				posseq.push_back(totalseq[i]);
//				inverted_index* index = createindex(totalseq[i]);
//				posindex.push_back(index);
//			}
//			else {
//				negseq.push_back(totalseq[i]);
//				inverted_index* index = createindex(totalseq[i]);
//				negindex.push_back(index);
//			}
//		}
//	}
//}
//
//void character_mining() {
//	for (int i = 0; i < totalseq.size(); i++) {
//		for (int j = 0; j < totalseq[i].length(); j++) {
//			single_pattern.insert(totalseq[i][j]);//�����ھ����д���set������
//		}
//	}
//	pattern.reserve(single_pattern.size()); // Ԥ�����㹻���ڴ�ռ�
//	for (const auto& ch : single_pattern) {//����set��������������ַ�����vector������
//		Pattern temp;
//		temp.P = ch;//����һ������,�������vector������
//		pattern.push_back(std::move(temp)); // ʹ�� std::move ���ⲻ��Ҫ�ĸ���
//	}
//	for (const auto& pat : pattern) {
//		cout << pat.P << endl;
//	}
//	cout << endl; // ������з�
//}
//
//double  CalcPatternDensity(string& pattern, string& sequence, inverted_index* index, double& r)//�����ܶ�
//{
//	int support = 0;
//	int* s = new int[pattern.length()]();//��¼ÿ���ַ���λ������
//	for (auto i = 0; i < pattern.length(); i++) {
//		s[i] = 0;
//	}
//	int pos = 0;//��û�ҵ�
//	int seqlen = sequence.length();
//	int thre = seqlen * r;
//	while (true)
//	{
//		for (int i = 0; i < pattern.length(); i++)
//		{
//			auto m = (*index).find(pattern[i]);//��¼��ǰ�ַ���ָ��ĵ�������
//
//			if (m == (*index).end()) {//�Ҳ���
//				delete[] s;
//				return double(support) / seqlen;
//			}
//			if ((*m).second->size() < (s[i] + 1)) {//Խ��
//				delete[] s;
//				return double(support) / seqlen;
//			}
//			if (i == 0)//����ǵ�һ���ַ�
//			{
//				if (sequence.length() - pos < pattern.length()) {//������ں�����ַ�����С��ģʽ�ַ�����
//					delete[] s;
//					return double(support) / seqlen;
//				}
//				while (pos >= (*(*m).second)[s[i]])//���˵pos�ȵ�ǰ��һ���ַ�λ��Ҫ��ָ����ơ�ע�⵹�����������õ��Ǵ�1��ʼ��(*(*m).second)[s[0]])�տ�ʼ��1
//				{
//					s[i]++;
//					if ((*m).second->size() < (s[i] + 1)) {//ֻҪ���ƾ�Ҫ�ж��Ƿ�Խ��
//						delete[] s;
//						return double(support) / seqlen;
//					}
//				}
//			}
//
//			auto n = m;
//			if (i > 0) {
//				n = (*index).find(pattern[i - 1]);//����ǰһ���ַ��ĵ�������
//			}
//
//			auto condition = i > 0 && (*(*m).second)[s[i]] <= (*(*n).second)[s[i - 1]]; //��һ���ַ�λ��Ҫ��ǰһ����
//
//			while (condition) {
//				s[i]++;
//				if ((*m).second->size() < (s[i] + 1)) {
//					delete[] s;
//					return double(support) / sequence.length();
//				}
//				condition = i > 0 && (*(*m).second)[s[i]] <= (*(*n).second)[s[i - 1]];
//			}
//			if (i == (pattern.length() - 1))//��¼���� ÿ��ģʽ���һ���ַ����ֵ�λ��
//			{
//				pos = (*(*m).second)[s[i]];
//			}
//
//		}
//		support++;
//		if (support > thre) {
//			delete[] s;
//			return 1;  //1  ��ʾ����
//		}
//	}
//}
//
////����ģʽ���ܶȺ�֧���ʣ�����ģʽ����ǰ���м�����ǰ���м��ĵ���������������r
//double CalcPatternRate1(string& pattern, vector<string>& sequenceSet, vector<inverted_index*>& indexset, double& r, double& value) {
//
//	if (sequenceSet.size() == 0) {
//		return 0;
//	}
//	int count = 0;
//	int exist = 0;//���������
//	int seqsize = sequenceSet.size();
//	for (int i = 0; i < seqsize; i++) {
//		if (pattern.length() <= sequenceSet[i].length()) {
//			exist = 1;
//			break;//һ�����ڰ�����ϵ������ѭ��ִ�������
//		}
//	}
//	if (exist == 0)
//		return 0;
//	int thre = seqsize * value;
//	for (int i = 0; i < seqsize; i++) {
//		double temp_r;
//		temp_r = CalcPatternDensity(pattern, sequenceSet[i], indexset[i], r);
//		//temp_r����1������ǰ��ֹ��Ҳ�Ǵ���r
//		//cout << "sup:" << temp_r << endl;
//		if (temp_r >= r) {//�ܶȴ��ڸ���ֵ�ģ���¼һ��count
//			count++;
//			if (count > thre)
//				return 1; //����Ҳ�Ƿ���1����������ǰ��ֹ����
//		}
//	}
//	//cout << "һ��ģʽ���ܶȽ���" << pattern<<endl;
//	return double(count) / seqsize;
//}
//
//double Top_k_Pos(double r, int k) {
//	int candidate_count = 0;
//	priority_queue<Pattern> G;//�󶥶�
//	vector<Pattern> E;//����size=1����֧���ʴ���0��ģʽ����
//	for (auto i = pattern.begin(); i != pattern.end(); i++) {
//		double value = 1;
//		(*i).RatePos = CalcPatternRate1((*i).P, posseq, posindex, r, value);
//
//		if (F1.size() >= k)
//			value = (*i).RatePos - F1.top().Contrast;//ֻ�д���thre = seqsize * value���Żᱻ�������
//
//		(*i).RateNeg = CalcPatternRate1((*i).P, negseq, negindex, r, value);
//		(*i).Contrast = (*i).RatePos - (*i).RateNeg;//���������ַ��ĶԱȶ�
//
//		if (i->RatePos > 0) {//������С֧���ʼ�֦����
//			G.push(*i);//�����ѡģʽ��
//			candidate_count++;
//		}
//		if (i->RatePos > 0) {//�������֦����
//			E.push_back(*i);
//		}
//		if ((F1.size() < k && (*i).Contrast > 0) || (F1.size() >= k && (*i).Contrast > F1.top().Contrast)) {//�Աȶ����Ȳ���
//			if (F1.size() >= k) {//�������F������ֻҪ�Աȶȴ���0���ܼӽ���������Ѿ����ˣ�����Ҫ����Fջ��Ԫ�صĶԱȶȲ��ܼӽ���
//				if (i->RatePos <= F1.top().Contrast) {
//					continue;
//				}
//				F1.pop();
//			}
//			F1.push(*i);
//		}
//	}
//	sort(E.begin(), E.end(), PatternGreater);//С����
//
//	while (!G.empty()) {//ֻҪ��ѡģʽ���ϲ�Ϊ�գ�����������ö��
//
//		Pattern p = G.top();
//		//cout << p.P << ":" << p.Contrast << endl;
//		G.pop();
//		for (auto j = E.begin(); j != E.end(); j++) {
//			Pattern q;
//			q.P = p.P + j->P;
//			double  value = 1;
//			q.RatePos = CalcPatternRate1(q.P, posseq, posindex, r, value);
//			if (q.RatePos == 0 || (F1.size() >= k && q.RatePos <= F1.top().Contrast)) {
//				continue;//���������ھ����˵��������֧���ʵ���0����F1�Ѿ����ˣ�������֧����С�ڵ���F1��ջ��Ԫ�صĶԱȶȣ���֦��
//			}
//			if (F1.size() >= k)
//				value = q.RatePos - F1.top().Contrast;
//
//			q.RateNeg = CalcPatternRate1(q.P, negseq, negindex, r, value);
//			q.Contrast = q.RatePos - q.RateNeg;
//			p.Contrast = p.RatePos - p.RateNeg;
//
//			if (q.Contrast <= p.Contrast) {
//				G.push(q);//�ȼ��뵽��ѡģʽ��
//				candidate_count++;
//			}
//			else {
//				G.push(q);//�ȼ��뵽��ѡģʽ��
//				candidate_count++;
//				if ((F1.size() < k && q.Contrast > 0) || (F1.size() >= k && q.Contrast > F1.top().Contrast)) {
//					if (F1.size() >= k) {
//						/*if (q.RatePos <=F1.top().Contrast) {
//							continue;
//						}*/
//						F1.pop();
//					}
//					F1.push(q);
//				}
//			}
//		}
//			}
//	double minContrast = 0;
//	if (F1.size() != 0) {
//		minContrast = F1.top().Contrast;//��¼������С�Աȶ�
//	}
//
//	total_candidate_count += candidate_count;
//	while (!F1.empty()) {
//		string m = F1.top().P;
//		cout << "F1.top():" << F1.top().P << ":" << F1.top().Contrast << endl;
//		F.push(F1.top());
//		F1.pop();
//		if (addedPatterns.find(m) == addedPatterns.end()) {//�����Ǵ���һ��set�����У���֤���ظ�
//			addedPatterns.insert(m);
//			//cout << "Adding pattern: " << m  << endl;
//		}
//	}
//	cout << "���ɵ������ѡģʽ������" << candidate_count << endl;
//	return minContrast;
//}
//void Top_k_Neg(double r, int k, double pos_minContrast) {
//	int candidate_count = 0;
//	priority_queue<Pattern>G;
//	vector<Pattern> E;
//	for (auto i = pattern.begin(); i != pattern.end(); i++) {
//		double value = 1;
//		(*i).RateNeg = CalcPatternRate1((*i).P, negseq, negindex, r, value);
//
//		if (i->RateNeg > 0 && i->RateNeg > pos_minContrast) {//����֧���ʴ���������С�ԱȶȲ��ܼ������
//			G.push(*i);
//			candidate_count++;
//		}
//		if (i->RateNeg > 0) {
//			E.push_back(*i);
//		}
//		if (F2.size() >= k)
//			value = (*i).RateNeg - pos_minContrast;//F2.top().Contrast;
//
//		(*i).RatePos = CalcPatternRate1((*i).P, posseq, posindex, r, value);
//		(*i).Contrast = (*i).RateNeg - (*i).RatePos;
//		if ((F2.size() < k && (*i).Contrast > 0) || (F2.size() >= k && (*i).Contrast > F2.top().Contrast)) {
//			// �����ǰģʽ��֧�ֶȴ�������top_k��С��֧�ֶȣ��ŷŵ�F��
//			if ((*i).RateNeg > pos_minContrast) {
//				if (F2.size() >= k) {
//					if (i->RateNeg <= F2.top().Contrast) {
//						continue;
//					}
//					F2.pop();
//				}
//				F2.push((*i));
//			}
//		}
//	}
//	sort(E.begin(), E.end(), PatternGreater);
//	while (!G.empty()) {
//		Pattern p = G.top();
//		G.pop();
//		for (auto j = E.begin(); j != E.end(); ++j) {
//			Pattern q;
//			q.P = p.P + j->P;
//			double value = 1;
//
//			q.RateNeg = CalcPatternRate1(q.P, negseq, negindex, r, value);
//			if (q.RateNeg == 0 || q.RateNeg <= pos_minContrast || (F2.size() >= k && q.RateNeg <= F2.top().Contrast)) {
//				continue;
//			}
//			if (F2.size() >= k)
//				value = q.RateNeg - pos_minContrast;// F2.top().Contrast;
//
//			q.RatePos = CalcPatternRate1(q.P, posseq, posindex, r, value);
//			q.Contrast = q.RateNeg - q.RatePos;
//			p.Contrast = p.RateNeg - p.RatePos;
//
//			if (q.Contrast <= p.Contrast) {
//
//				G.push(q);//�ȼ��뵽��ѡģʽ��
//				candidate_count++;
//			}
//			else {
//				G.push(q);
//			candidate_count++;
//			if ((F2.size() < k && q.Contrast > 0) || (F2.size() >= k && q.Contrast > F2.top().Contrast)) {
//				if (F2.size() >= k) {
//					/*if (q.RateNeg <= F2.top().Contrast) {
//						continue;
//					}*/
//					F2.pop();
//				}
//				F2.push(q);
//			}
//		}
//	}
//			}
//	total_candidate_count += candidate_count;
//	while (!F2.empty()) {
//		cout << "F2.top()" << F2.top().P << ": " << F2.top().Contrast << endl;
//		string m = F2.top().P;
//		if ((F.size() < k && F2.top().Contrast > 0) || (F.size() >= k && F2.top().Contrast > F.top().Contrast)) {
//			if (addedPatterns.find(m) == addedPatterns.end()) {
//				if (F.size() >= k) {
//					F.pop();
//				}
//				F.push(F2.top());
//			}
//		}
//		F2.pop();
//	}
//	cout << "���ɵĸ����ѡģʽ������" << candidate_count << endl;
//}
//void PrintMemoryUsage()
//{
//	PROCESS_MEMORY_COUNTERS pmc;
//	GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc));
//	std::cout << "Memory Usage: " << std::fixed << std::setprecision(2) << pmc.WorkingSetSize / (1024.0 * 1024.0) << " MB" << std::endl;
//}
//int main()
//{
//	readfile();
//	character_mining();
//	clock_t start, end;//����clock_t����
//	start = clock();//��ʼʱ��
//	double pos_res = Top_k_Pos(r, k);
//	Top_k_Neg(r, k, pos_res);
//	cout << "���ɵ�˫���ѡģʽ����: " << total_candidate_count << endl;
//	while (!F.empty()) {
//		for (int i = 1; i <= 10; i++) {
//			cout << "string pattern" << i << "=" << "\"" << F.top().P << "\"" << "; " << F.top().Contrast << endl;
//			F.pop();
//		}
//	}
//	end = clock();   //����ʱ��
//	cout << "time = " << double(end - start) / CLOCKS_PER_SEC << "s" << endl;  //���ʱ�䣨��λ����
//	PrintMemoryUsage(); // Output memory usage
//	system("pause");
//	return 0;
//}