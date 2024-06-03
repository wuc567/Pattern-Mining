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
//#include <iomanip>
//#include <string>
////改文件名，改正负界限
//using namespace std;
//time_t calc_next_time;
////一些定义
//double r = 0.035;
//int k = 10;
//string file = "d:/组内算法/pattern-mining-master/scp-miner/dataset/BC.txt";
//int classified = 1;//表明已经分类
//vector<string> totalseq, posseq, negseq, dataseq;//后三个数据集用于数据挖掘
//typedef unordered_map<char, vector<int>*> inverted_index;
//vector< inverted_index*> posindex, negindex, totalindex;
//set<char> single_pattern;//构建一个set容器变量，这样可以保证挖掘出来的模式不重复！
//struct Pattern {
//	string P;
//	double RatePos;
//	double RateNeg;
//	double Contrast;
//
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
//priority_queue<Pattern, vector<Pattern>, rule>F1, F2, F, Fx, Fy, Ft;
//bool PatternGreater(Pattern& p1, Pattern& p2) {
//	return p1.Contrast > p2.Contrast;
//}
//set<string> addedPatterns;
//
//int total_candidate_count = 0;
//
//double eps = 1e-9;
//
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
//
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
//				dataseq.push_back(s);
//				inverted_index* index = createindex(s);
//				posindex.push_back(index);
//				totalindex.push_back(index);
//
//
//			}
//			if (totalseq[i][0] == '2') {
//				string s = totalseq[i].substr(1);
//				negseq.push_back(s);
//				dataseq.push_back(s);
//				inverted_index* index = createindex(s);
//				negindex.push_back(index);
//				totalindex.push_back(index);
//			}
//		}
//	}
//	else {
//		for (int i = 0; i < totalseq.size(); i++) {
//			if (i < 25) {
//				posseq.push_back(totalseq[i]);
//				inverted_index* index = createindex(totalseq[i]);
//				posindex.push_back(index);
//				totalindex.push_back(index);
//				//printIndexReverse(index);
//			}
//			else {
//				negseq.push_back(totalseq[i]);
//				inverted_index* index = createindex(totalseq[i]);
//				negindex.push_back(index);
//				totalindex.push_back(index);
//			}
//		}
//	}
//}
//
//void character_mining() {
//	for (int i = 0; i < totalseq.size(); i++) {
//		for (int j = 0; j < totalseq[i].length(); j++) {
//			if (isalpha(totalseq[i][j])) {
//				single_pattern.insert(totalseq[i][j]);//将待挖掘序列存入set容器中
//			}
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
//
//
//double  CalcPatternDensity(string pattern, string sequence, inverted_index* index)//计算密度
//{
//	int support = 0;
//	int* s = new int[pattern.length()]();//记录每个字符的位置数组
//	for (auto i = 0; i < pattern.length(); i++) {
//		s[i] = 0;
//	}
//	int pos = 0;//都没找到
//	while (true)
//	{
//		for (int i = 0; i < pattern.length(); i++)
//		{
//			auto m = (*index).find(pattern[i]);//记录当前字符所指向的倒排索引
//
//			if (m == (*index).end()) {//找不到
//				delete[] s;
//				return double(support) / sequence.length();
//			}
//			if ((*m).second->size() < (s[i] + 1)) {//越界
//				delete[] s;
//				return double(support) / sequence.length();
//			}
//			if (i == 0)//如果是第一个字符
//			{
//				if (sequence.length() - pos < pattern.length()) {//如果现在后面的字符个数小于模式字符个数
//					delete[] s;
//					return double(support) / sequence.length();
//				}
//				while (pos >= (*(*m).second)[s[i]])//如果说pos比当前第一个字符位置要大，指针后移。注意倒排索引我设置的是从1开始的(*(*m).second)[s[0]])刚开始是1
//				{
//					s[i]++;
//					if ((*m).second->size() < (s[i] + 1)) {//只要后移就要判断是否越界
//						delete[] s;
//						return double(support) / sequence.length();
//					}
//				}
//			}
//
//			auto n = m;
//			if (i > 0) {
//				n = (*index).find(pattern[i - 1]);//定义前一个字符的倒排索引
//			}
//
//			auto condition = i > 0 && (*(*m).second)[s[i]] <= (*(*n).second)[s[i - 1]]; //后一个字符位置要比前一个大
//
//			while (condition) {
//				s[i]++;
//				if ((*m).second->size() < (s[i] + 1)) {
//					delete[] s;
//					return double(support) / sequence.length();
//				}
//				condition = i > 0 && (*(*m).second)[s[i]] <= (*(*n).second)[s[i - 1]];
//			}
//			if (i == (pattern.length() - 1))//记录下来 每个模式最后一个字符出现的位置
//			{
//				pos = (*(*m).second)[s[i]];
//			}
//
//		}
//		support++;
//
//	}
//}
//
//
////计算模式的密度和支持率，传入模式、当前序列集、当前序列集的倒排索引集、参数r
//double CalcPatternRate(string& pattern, vector<string>& sequenceSet, vector<inverted_index*>& indexset, double r) {
//	if (sequenceSet.size() == 0) {
//		return 0;
//	}
//	int count = 0;
//	int exist = 0;//如果不包含
//	for (int i = 0; i < sequenceSet.size(); i++) {
//		if (pattern.length() <= sequenceSet[i].length()) {
//			exist = 1;
//			break;//一旦存在包含关系，跳出循环执行下面的
//		}
//	}
//	if (exist == 0)
//		return 0;
//	for (int i = 0; i < sequenceSet.size(); i++) {
//		double temp_r;
//		temp_r = CalcPatternDensity(pattern, sequenceSet[i], indexset[i]);
//		if (temp_r >= r) {//密度大于给定值的，记录一个count
//			count++;
//		}
//	}
//	double x = double(count) / sequenceSet.size();
//
//	return x;
//}
//
////计算模式的支持度，如果密度大于r，就在对应的数组上填1，否则0
//void saveSup(string& pattern, vector<string>& sequenceSet, vector<inverted_index*>& indexset, vector<int>& array) {
//	double den = 0;
//	for (int i = 0; i < sequenceSet.size(); i++) {
//		den = CalcPatternDensity(pattern, sequenceSet[i], indexset[i]);
//		//cout << "sup:" << sup << endl;
//		if (den > r) {
//			array[i] = 1;
//		}
//		else {
//			array[i] = 0;
//		}
//	}
//	//cout << "一个模式的密度结束" << pattern<<endl;
//}
//
//double cosine_similarity(vector<int>& v1, vector<int>& v2) {
//	double dot_product = 0;
//	double norm_v1 = 0;
//	double norm_v2 = 0;
//
//	for (int i = 0; i < v1.size(); i++) {
//		dot_product += v1[i] * v2[i];
//		norm_v1 += v1[i] * v1[i];
//		norm_v2 += v2[i] * v2[i];
//	}
//
//	if (norm_v1 == 0 || norm_v2 == 0) {
//		return 0;
//	}
//	else {
//		return dot_product / (sqrt(norm_v1) * sqrt(norm_v2));
//	}
//}
//
//double calculateCosineSimilarity(Pattern& newPattern, Pattern& topPattern) {
//	string pattern1 = newPattern.P;
//	string pattern2 = topPattern.P;
//
//	vector<int> array1;
//	vector<int> array2;
//	for (int i = 0; i < totalseq.size(); i++) {
//		array1.push_back(0);
//		array2.push_back(0);
//	}
//	if (classified == 1) {
//		saveSup(pattern1, dataseq, totalindex, array1);
//		saveSup(pattern2, dataseq, totalindex, array2);
//	}
//	else {
//		saveSup(pattern1, totalseq, totalindex, array1);
//		saveSup(pattern2, totalseq, totalindex, array2);
//	}
//
//	/*cout << "pattern1: "<<pattern1<<" ";
//	for (int val : array1) {
//		cout << val << " ";
//	}
//	cout << endl;
//
//	cout << "pattern2: "<<pattern2 << " ";
//	for (int val : array2) {
//		cout << val << " ";
//	}
//	cout << endl;*/
//
//	double similarity = cosine_similarity(array1, array2);
//	return similarity;
//}
////对比度不相等或者是对比度相等但相似度不是1
//void flag0(Pattern& p1) {
//	Pattern newPattern = p1;
//	Ft.push(newPattern);
//	while (!Ft.empty()) {
//		F1.push(Ft.top());
//		Ft.pop();
//	}
//}
////对比度相等且相似度也相等，保留原样
//void replace0() {
//	while (!Ft.empty()) {
//		F1.push(Ft.top());
//		Ft.pop();
//	}
//}
////新生成的模式更频繁
//void newpattern(Pattern& p3, string spattern) {
//	Pattern newPattern = p3;
//	Ft.push(newPattern);
//	while (!Ft.empty()) {
//		std::string s = Ft.top().P;
//		if (s == spattern) {
//			Ft.pop();
//			continue;
//		}
//		F1.push(Ft.top());
//		Ft.pop();
//	}
//}
//
//double Top_k_Pos(double& r, int& k) {
//	int candidate_count = 0;
//	priority_queue<Pattern> G;//大顶堆
//	vector<Pattern> E;//所有size=1的且支持率大于0的模式集合
//
//	bool flag = 0;//flag=0表示新模式和栈里模式不冲突，都可以加入
//	//flag=1表示新模式和栈里模式冲突，有的需要去掉
//	string spattern = "spattern";//表示会发生相似的模式
//	bool replace = 0;//replace=0表示不需要移动栈里元素
//	//replace=1表示需要替换栈里元素
//
//	for (auto i = pattern.begin(); i != pattern.end(); i++) {
//		int f = 0;
//		(*i).RatePos = CalcPatternRate((*i).P, posseq, posindex, r);
//		(*i).RateNeg = CalcPatternRate((*i).P, negseq, negindex, r);
//		(*i).Contrast = (*i).RatePos - (*i).RateNeg;//计算所有字符的对比度
//		if (i->RatePos > 0) {
//			G.push(*i);
//			candidate_count++;
//		}if (i->RatePos > 0) {//正向零剪枝策略
//			E.push_back(*i);
//		}
//		if ((F1.size() < k && (*i).Contrast > 0) || (F1.size() >= k && (*i).Contrast > F1.top().Contrast)) {
//			if (F1.size() == 0) {
//				F1.push(*i);
//			}
//			else {
//				flag = 0;
//				replace = 0;
//				Pattern popPattern = F1.top();
//				if (F1.size() >= k) {
//					F1.pop();
//					f = 1;
//				}
//				if ((*i).Contrast >= 0.8) {
//					F1.push(*i);
//				}
//				else {
//					while (!F1.empty()) {
//						Pattern newPattern = (*i);
//						Pattern topPattern = F1.top();
//						Ft.push(topPattern);
//						F1.pop();
//						if (abs(newPattern.Contrast - topPattern.Contrast) < eps) {
//							double c = calculateCosineSimilarity(newPattern, topPattern);
//							if ((1 - c) < eps) {
//								flag = 1;//对比度相等、相似度为1
//								string spattern = topPattern.P;
//								if (newPattern.RatePos > topPattern.RatePos) {
//									replace = 1;
//								}
//								break;//一旦有对比度相等、相似度为1就可以break了
//							}
//						}
//					}
//					if (flag == 0) {
//						flag0((*i));
//					}
//					else {
//						if (replace == 0) {
//							if (f == 1) {
//								Ft.push(popPattern);
//							}
//							replace0();
//							//cout << (*i).P << endl;
//						}
//						else {
//							newpattern((*i), spattern);
//						}
//					}
//				}
//			}
//		}
//	}
//	sort(E.begin(), E.end(), PatternGreater);//小顶堆
//	while (!G.empty()) {//只要候选模式集合不为空，就用它进行枚举
//		Pattern p = G.top();
//		G.pop();
//		for (auto j = E.begin(); j != E.end(); j++) {
//			int f = 0;
//			Pattern q;
//			q.P = p.P + j->P;
//			q.RatePos = CalcPatternRate(q.P, posseq, posindex, r);
//			if (q.RatePos == 0 || (F1.size() >= k && q.RatePos <= F1.top().Contrast)) {
//				continue;//进行正向挖掘，如果说它的正向支持率等于0或者F1已经满了，且正向支持率小于等于F1的栈顶元素的对比度，剪枝。
//			}
//			q.RateNeg = CalcPatternRate(q.P, negseq, negindex, r);
//			q.Contrast = q.RatePos - q.RateNeg;
//			if (q.Contrast <= p.Contrast) {
//				Fx.push(q);
//				G.push(q);//先加入到候选模式中
//				candidate_count++;
//			}
//			else {
//				G.push(q);//先加入到候选模式中
//				candidate_count++;
//				if ((F1.size() < k && q.Contrast > 0) || (F1.size() >= k && q.Contrast > F1.top().Contrast)) {
//					if (F1.size() == 0) {
//						F1.push(q);
//					}
//					else {
//						Pattern popPattern = F1.top();
//						flag = 0;
//						replace = 0;
//						if (F1.size() >= k) {
//							F1.pop();
//							f = 1;
//						}
//						if (q.Contrast >= 0.8) {
//							F1.push(q);
//						}
//						else {
//							while (!F1.empty()) {
//								Pattern newPattern = q;
//								Pattern topPattern = F1.top();
//								Ft.push(topPattern);
//								F1.pop();
//								if (abs(newPattern.Contrast - topPattern.Contrast) < eps) {
//									double c = calculateCosineSimilarity(newPattern, topPattern);
//									if ((1 - c) < eps) {
//										flag = 1;//对比度相等、相似度为1
//										spattern = topPattern.P;
//										if (newPattern.RatePos > topPattern.RatePos) {
//											replace = 1;
//										}
//										break;
//									}
//								}
//							}
//							if (flag == 0) {
//								flag0(q);
//							}
//							else {
//								if (replace == 0) {
//									if (f == 1) {
//										Ft.push(popPattern);
//									}
//									replace0();
//								}
//								else {
//									newpattern(q, spattern);
//								}
//							}
//						}
//
//					}
//				}
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
////对比度不相等或者是对比度相等但相似度不是1
//void flag00(Pattern& p4) {
//	Pattern newPattern = p4;
//	Ft.push(newPattern);
//	while (!Ft.empty()) {
//		F2.push(Ft.top());
//		Ft.pop();
//	}
//}
////对比度相等且相似度也相等,保留原样
//void replace00() {
//	while (!Ft.empty()) {
//		F2.push(Ft.top());
//		Ft.pop();
//	}
//}
////新生成的模式更频繁
//void newpattern1(Pattern& p6, string spattern) {
//	Pattern newPattern = p6;
//	Ft.push(newPattern);
//	while (!Ft.empty()) {
//		std::string s = Ft.top().P;
//		if (s == spattern) {
//			Ft.pop();
//			continue;
//		}
//		F2.push(Ft.top());
//		Ft.pop();
//	}
//}
//
//
//void Top_k_Neg(double& r, int& k, double& pos_minContrast) {
//	int candidate_count = 0;
//	priority_queue<Pattern>G;
//	vector<Pattern> E;
//
//	bool flag = 0;//flag=0表示新模式和栈里模式不冲突，都可以加入
//	//flag=1表示新模式和栈里模式冲突，有的需要去掉
//	string spattern = "spattern";//表示会发生相似的模式
//	bool replace = 0;//replace=0表示不需要移动栈里元素
//	//replace=1表示需要替换栈里元素
//
//	for (auto i = pattern.begin(); i != pattern.end(); i++) {
//		int f = 0;
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
//				if (F2.size() == 0) {
//					F2.push((*i));
//				}
//				else {
//					Pattern popPattern = F2.top();
//					flag = 0;
//					replace = 0;
//					if (F2.size() >= k) {
//						F2.pop();
//						f = 1;
//					}
//					if ((*i).Contrast >= 0.8) {
//						F2.push(*i);
//					}
//					else {
//						while (!F2.empty()) {
//							Pattern newPattern = (*i);
//							Pattern topPattern = F2.top();
//							Ft.push(topPattern);
//							F2.pop();
//							if (abs(newPattern.Contrast - topPattern.Contrast) < eps) {
//								double c = calculateCosineSimilarity(newPattern, topPattern);
//								if ((1 - c) < eps) {
//									flag = 1;//对比度相等、相似度为1
//									spattern = topPattern.P;
//									if (newPattern.RateNeg > topPattern.RateNeg) {
//										replace = 1;
//									}
//									break;
//								}
//							}
//						}
//						if (flag == 0) {
//							flag00((*i));
//						}
//						else {
//							if (replace == 0) {
//								if (f == 1) {
//									Ft.push(popPattern);
//								}
//								replace00();
//							}
//							else {
//								newpattern1((*i), spattern);
//							}
//						}
//					}
//				}
//			}
//		}
//	}
//	sort(E.begin(), E.end(), PatternGreater);
//	while (!G.empty()) {
//		Pattern p = G.top();
//		G.pop();
//		for (auto j = E.begin(); j != E.end(); ++j) {
//			int f = 0;
//			Pattern q;
//			q.P = p.P + j->P;
//			q.RateNeg = CalcPatternRate(q.P, negseq, negindex, r);
//			if (q.RateNeg == 0 || q.RateNeg <= pos_minContrast || (F2.size() >= k && q.RateNeg <= F2.top().Contrast)) {
//				continue;
//			}
//			q.RatePos = CalcPatternRate(q.P, posseq, posindex, r);
//			q.Contrast = q.RateNeg - q.RatePos;
//			p.Contrast = p.RateNeg - p.RatePos;
//			if (q.Contrast <= p.Contrast) {
//				Fx.push(q);
//				G.push(q);//先加入到候选模式中
//				candidate_count++;
//			}
//			else {
//				G.push(q);
//				candidate_count++;
//				if ((F2.size() < k && q.Contrast > 0) || (F2.size() >= k && q.Contrast > F2.top().Contrast)) {
//					if (F2.size() == 0) {
//						F2.push(q);
//					}
//					else {
//						Pattern popPattern = F2.top();
//						flag = 0;
//						replace = 0;
//						if (F2.size() >= k) {
//							F2.pop();
//							f = 1;
//						}
//						if (q.Contrast >= 0.8) {
//							F2.push(q);
//						}
//						else {
//							while (!F2.empty()) {
//								Pattern newPattern = q;
//								Pattern topPattern = F2.top();
//								Ft.push(topPattern);
//								F2.pop();
//								if (abs(newPattern.Contrast - topPattern.Contrast) < eps) {
//									double c = calculateCosineSimilarity(newPattern, topPattern);
//									if ((1 - c) < eps) {
//										flag = 1;//对比度相等、相似度为1
//										spattern = topPattern.P;
//										if (newPattern.RateNeg > topPattern.RateNeg) {
//											replace = 1;
//										}
//										break;
//									}
//								}
//							}
//							if (flag == 0) {
//								flag00(q);
//							}
//							else {
//								if (replace == 0) {
//									if (f == 1) {
//										Ft.push(popPattern);
//									}
//									replace00();
//								}
//								else {
//									newpattern1(q, spattern);
//								}
//							}
//						}
//					}
//				}
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
//			cout << "string pattern" << i << "=" << "\"" << F.top().P << "\"" << "; " << F.top().Contrast << endl;
//			F.pop();
//		}
//	}
//	end = clock();   //结束时间
//	cout << "time = " << double(end - start) / CLOCKS_PER_SEC << "s" << endl;  //输出时间（单位：ｓ）
//	system("pause");
//	return 0;
//}