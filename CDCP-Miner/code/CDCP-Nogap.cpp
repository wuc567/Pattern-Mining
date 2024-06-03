﻿//#include<iostream>
//#include<unordered_map>
//#include<vector>
//#include <map>
//#include<set>
//#include<sstream>
//#include<fstream>
//#include<queue>
//#include <algorithm>
//#include<unordered_set>
//using namespace std;
//time_t calc_next_time;
////一些定义
//double r = 0.035;
//int k = 10;
//string file = "d:/组内算法/pattern-mining-master/scp-miner/dataset/RNA.txt";
//int classified = 1;//表明已经分类
//vector<string> totalseq, posseq, negseq;
//typedef unordered_map<char, vector<int>*> inverted_index;
//vector< inverted_index*> posindex, negindex;
//set<char> single_pattern;//构建一个set容器变量，这样可以保证挖掘出来的模式不重复！
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
//double CalcPatternDensity(string pattern, string sequence, inverted_index* index);
//struct rule {
//	bool operator()(Pattern a, Pattern b)const {//这个顺序有什么用呢
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
////函数声明
//void readfile();
//inverted_index* createindex(string s);
//
//void character_mining();
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
//	cout << "文件名：" << file << endl;
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
//			if (i < 25) {
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
//			single_pattern.insert(totalseq[i][j]);//将待挖掘序列存入set容器中
//		}
//	}
//	pattern.reserve(single_pattern.size()); // 预分配足够的内存空间
//	for (const auto& ch : single_pattern) {//遍历set容器，将里面的字符传到vector容器中
//		Pattern temp;
//		temp.P = ch;//定义一个变量,将其存入vector容器中
//		pattern.push_back(std::move(temp)); // 使用 std::move 避免不必要的复制
//	}
//	for (const auto& pat : pattern) {
//		cout << pat.P << endl;
//	}
//	cout << endl; // 输出换行符
//}
//
//double CalcPatternDensity(string pattern, string sequence)
//{
//	int index = 0;//下标
//	double sup = 0;//次数
//	while ((index = sequence.find(pattern, index)) < sequence.length()) {
//		sup++;
//		index++;
//	}
//	return sup / sequence.length();
//}
//
//
//
//
//
//
////计算模式的密度和支持率，传入模式、当前序列集、当前序列集的倒排索引集、参数r
//// 计算当前模式在序列集下的count和r
//double CalcPatternRate(string pattern, vector<string> sequenceSet, vector<inverted_index*>& nextSet, double raurau)
//{
//	if (sequenceSet.size() == 0) {
//		return 0;
//	}
//
//
//	int count = 0;
//	int has_valid = 0;
//	for (int i = 0; i < sequenceSet.size(); i++) {
//		if (pattern.length() <= sequenceSet[i].length()) {
//			has_valid = 1;
//			break;
//		}
//	}
//	if (has_valid == 0)
//		return 0;
//	//cout << "size:" << sequenceSet.size();
//	for (int i = 0; i < sequenceSet.size(); i++) {
//		double rau_next;
//		if (false) {
//			rau_next = double((*(*nextSet[i])[pattern[0]]).size()) / sequenceSet[i].size();
//		}
//		else {
//			rau_next = CalcPatternDensity(pattern, sequenceSet[i]);
//		}
//		if (rau_next >= raurau) {
//			count++;
//		}
//	}
//	return double(count) / sequenceSet.size();
//}
//
//double Top_k_Pos(double r, int k) {
//	int candidate_count = 0;
//	priority_queue<Pattern> G;//大顶堆
//	vector<Pattern> E;//所有size=1的且支持率大于0的模式集合
//	for (auto i = pattern.begin(); i != pattern.end(); i++) {
//		(*i).RatePos = CalcPatternRate((*i).P, posseq, posindex, r);
//		(*i).RateNeg = CalcPatternRate((*i).P, negseq, negindex, r);
//		(*i).Contrast = (*i).RatePos - (*i).RateNeg;//计算所有字符的对比度
//
//		if (i->RatePos > 0) {//正向最小支持率剪枝策略
//			G.push(*i);//加入候选模式中
//			candidate_count++;
//		}
//		if (i->RatePos > 0) {//正向零剪枝策略
//			E.push_back(*i);
//		}
//		if ((F1.size() < k && (*i).Contrast > 0) || (F1.size() >= k && (*i).Contrast > F1.top().Contrast)) {//对比度优先策略
//			if (F1.size() >= k) {//如果集合F不满，只要对比度大于0就能加进来。如果已经满了，必须要大于F栈顶元素的对比度才能加进来
//				F1.pop();
//			}
//			F1.push(*i);
//		}
//	}
//	sort(E.begin(), E.end(), PatternGreater);//小顶堆
//	/*for (auto j = E.begin(); j != E.end(); j++) {
//		cout << j->P << endl;
//	}*/
//	while (!G.empty()) {//只要候选模式集合不为空，就用它进行枚举
//		
//		Pattern p = G.top();
//		//cout << p.P << ":" << p.Contrast << endl;
//		G.pop();
//		for (auto j = E.begin(); j != E.end(); j++) {
//			Pattern q;
//			q.P = p.P + j->P;
//			q.RatePos = CalcPatternRate(q.P, posseq, posindex, r);
//			if (q.RatePos == 0 || (F1.size() >= k && q.RatePos <= F1.top().Contrast)) {
//				continue;//进行正向挖掘，如果说它的正向支持率等于0或者F1已经满了，且正向支持率小于等于F1的栈顶元素的对比度，剪枝。
//			}
//			q.RateNeg = CalcPatternRate(q.P, negseq, negindex, r);
//			q.Contrast = q.RatePos - q.RateNeg;
//			G.push(q);//先加入到候选模式中
//			candidate_count++;
//			if ((F1.size() < k && q.Contrast > 0) || (F1.size() >= k && q.Contrast > F1.top().Contrast)) {
//				if (F1.size() >= k) {
//					F1.pop();
//				}
//				F1.push(q);
//			}
//		}
//	}
//	double minContrast = 0;
//	if (F1.size() != 0) {
//		minContrast = F1.top().Contrast;//记录下来最小对比度
//	}
//
//	total_candidate_count += candidate_count;
//	while (!F1.empty()) {
//		string m = F1.top().P;
//		cout << "F1.top():" << F1.top().P << ":" << F1.top().Contrast << endl;
//		F.push(F1.top());
//		F1.pop();
//		if (addedPatterns.find(m) == addedPatterns.end()) {//将他们存入一个set容器中，保证不重复
//			addedPatterns.insert(m);
//			//cout << "Adding pattern: " << m  << endl;
//		}
//	}
//	cout << "生成的正向候选模式总数：" << candidate_count << endl;
//	return minContrast;
//}
//void Top_k_Neg(double r, int k, double pos_minContrast) {
//	int candidate_count = 0;
//	priority_queue<Pattern>G;
//	vector<Pattern> E;
//	for (auto i = pattern.begin(); i != pattern.end(); i++) {
//		(*i).RateNeg = CalcPatternRate((*i).P, negseq, negindex, r);
//
//		if (i->RateNeg > 0 && i->RateNeg > pos_minContrast) {//负向支持率大于正向最小对比度才能加入进来
//			G.push(*i);
//			candidate_count++;
//		}
//		if (i->RateNeg > 0) {
//			E.push_back(*i);
//		}
//		(*i).RatePos = CalcPatternRate((*i).P, posseq, posindex, r);
//		(*i).Contrast = (*i).RateNeg - (*i).RatePos;
//		if ((F2.size() < k && (*i).Contrast > 0) || (F2.size() >= k && (*i).Contrast > F2.top().Contrast)) {
//			// 如果当前模式的支持度大于正向集top_k最小的支持度，才放到F中
//			if ((*i).RateNeg > pos_minContrast) {
//				if (F2.size() >= k) {
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
//			q.RateNeg = CalcPatternRate(q.P, negseq, negindex, r);
//			if (q.RateNeg == 0 || q.RateNeg <= pos_minContrast || (F2.size() >= k && q.RateNeg <= F2.top().Contrast)) {
//				continue;
//			}
//			q.RatePos = CalcPatternRate(q.P, posseq, posindex, r);
//			q.Contrast = q.RateNeg - q.RatePos;
//
//			G.push(q);
//			candidate_count++;
//			if ((F2.size() < k && q.Contrast > 0) || (F2.size() >= k && q.Contrast > F2.top().Contrast)) {
//				if (F2.size() >= k) {
//					F2.pop();
//				}
//				F2.push(q);
//			}
//		}
//	}
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
//	cout << "生成的负向候选模式总数：" << candidate_count << endl;
//}
//
//int main()
//{
//	readfile();
//	character_mining();
//	clock_t start, end;//定义clock_t变量
//	start = clock();//开始时间
//	double pos_res = Top_k_Pos(r, k);
//	Top_k_Neg(r, k, pos_res);
//	cout << "生成的双向候选模式总数: " << total_candidate_count << endl;
//	while (!F.empty()) {
//		for (int i = 1; i <= 10; i++) {
//			cout << "string pattern" <<i<<"="<<"\"" << F.top().P << "\""  << "; " << F.top().Contrast << endl;
//			F.pop();
//		}
//	}
//	end = clock();   //结束时间
//	cout << "time = " << double(end - start) / CLOCKS_PER_SEC << "s" << endl;  //输出时间（单位：ｓ）
//	system("pause");
//	return 0;
//}