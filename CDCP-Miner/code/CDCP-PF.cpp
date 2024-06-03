///* next+3种剪枝 */
//
//#include <map>
//#include <unordered_map>
//#include <set>
//#include <vector>
//#include <string>
//#include <iostream>
//#include <stdlib.h>
//#include <fstream>
//#include <queue>
//#include <cmath>
//#include <sstream>
//#include <ctime>
//#include <memory>
//#include <algorithm>
//#include <ctime>
//#include <iomanip>
//#include <windows.h>
//#include <psapi.h> // For memory usage
//using namespace std;
//
//double raurau = 0.06;
//int k = 10;
//int filetype =1;       //1为有lable  0为无lable
////有标签：BC BF credit Gene letter
//#if defined(WIN32) || defined(_WIN32) || defined(__WIN32) && !defined(__CYGWIN__)
//string fileName = "d:/组内算法/pattern-mining-master/scp-miner/dataset/gene.txt";
//#else
//string fileName = "/Users/haha/Desktop/代码/DataSet/promoters.txt";
//#endif // __WINDOWS_
//
//// 压缩方法的next，存序列每个字符所有的出现位置
//typedef unordered_map<char, vector<int>*> compressed_next;
////typedef map<char, vector<int> *> compressed_next;
//
//// 改进：map的value存数组下标，实际数据放在vector里
//typedef unordered_map<char, int> elem_pos;
//typedef vector<vector<int>*> next_v2;
//
//time_t calc_next_time;
//
//// 模式中的单个字符在序列中出现的位置
//struct SigmaInstance
//{
//    char sigma;     // 当前字符
//    vector<int> sigmaInstance;   //字符在序列中出现的位置
//};
//
//struct PatternInfo
//{
//    string P;           // 当前模式
//    double RatePos;
//    double RateNeg;
//    double Contrast;    // 模式的c
//
//    bool operator<(const PatternInfo& p) const {
//        return Contrast < p.Contrast;
//    }
//};
//
//struct temp {
//    bool operator() (PatternInfo a, PatternInfo b) {
//        return a.Contrast > b.Contrast;
//    }
//};
//set<char> InitSigma;
//priority_queue<PatternInfo, vector<PatternInfo>, temp > F1, F2, F;
//int total_condidate_pattern_count = 0;
//
//// 为什么要有Sigma呢，因为InitSigma是set结构，不好遍历或者关联到对应的对比度
//vector<PatternInfo> Sigma;   // 序列存在的字符集
//vector<string> PositiveSeq, NegativeSeq, TotalSeq;    // 正数据集&负数据集
//vector<compressed_next*> PositiveNext, NegativeNext;
//double CalcPatternContrast(string pattern, double raurau);
//double CalcPatternRate(string pattern, vector<string> sequenceSet, vector<compressed_next*>& nextSet, double raurau);
//double CalcPatternDimension(string pattern, string sequence);
//double CalcPatternDimensionWithCompressed(string pattern, string sequence, compressed_next* next);
//void GenerateCandidatePatterns(double raurau);
//compressed_next* CalcSequenceCompressedNext(string sequence);
//
//bool PatternInfoGreater(PatternInfo p1, PatternInfo p2)
//{
//    return p1.Contrast > p2.Contrast;
//}
//
//
////计算对比度
//double CalcPatternContrast(string pattern, double raurau)
//{
//    double r1 = CalcPatternRate(pattern, PositiveSeq, PositiveNext, raurau);
//    double r2 = CalcPatternRate(pattern, NegativeSeq, NegativeNext, raurau);
//    cout << "r1: " << r1 << ", r2: " << r2 << endl;
//    return r1 - r2;
//}
//
//double CalcPatternDimensionWithCompressed(string pattern, string sequence)
//{
//    int seqlen = sequence.length();
//    int thre = seqlen * raurau;
//    if (sequence.length() == 0) {
//        return 0;
//    }
//    if (pattern.length() >= sequence.length()) {
//        return 0;
//    }
//    int support = 0;
//    vector<SigmaInstance> pf;
//    for (int i = 0; i < pattern.length(); i++) {
//        SigmaInstance SI;
//        pf.push_back(SI);
//    }
//    for (int i = 0; i < sequence.length(); i++) {
//        for (int j = 0; j < pattern.length(); j++) {
//            if (sequence[i] == pattern[j]) {
//                if (j > 0 && pf[j - 1].sigmaInstance.size() > 0 && i > pf[j - 1].sigmaInstance[0]) {
//                    pf[j].sigmaInstance.push_back(i);
//                    pf[j].sigma = pattern[j];
//                }
//                else if (j > 0) {
//                    continue;
//                }
//                else if (j == 0) {
//                    pf[0].sigmaInstance.push_back(i);
//                    pf[0].sigma = pattern[0];
//                }
//                if (j == pattern.length() - 1) {
//                    if (pattern == "IBJI" && sequence == "IJDEBIHCJJBHIIJABJBJIHIBIIH") {
//                        cout << "haha" << endl;
//                    }
//                    support++;
//                    if (support > thre)
//                        return 1;  //1  表示出现
//                    int pos = 0;
//                    pos = pf[pattern.length() - 1].sigmaInstance[0];
//                    for (int k = 0; k < pattern.length(); k++) {
//                        for (auto i = pf[k].sigmaInstance.begin(); i != pf[k].sigmaInstance.end();) {
//                            //bool is_delete = false;
//
//                            if (*i <= pos) {
//                                i = pf[k].sigmaInstance.erase(i);
//                                // is_delete = true;
//                            }
//                        }
//                    }
//                    for (int k = 0; k < pattern.length() - 1; k++) {
//                        auto i = pf[k].sigmaInstance.begin();
//                        if (i == pf[k].sigmaInstance.end()) {
//                            for (int m = k + 1; m < pattern.length(); m++) {
//                                auto n = pf[m].sigmaInstance.begin();
//                                while (n != pf[m].sigmaInstance.end())
//                                    n = pf[m].sigmaInstance.erase(n);
//                            }
//                            continue;
//                        }
//                        auto j = pf[k + 1].sigmaInstance.begin();
//                        while (i != pf[k].sigmaInstance.end() && j != pf[k + 1].sigmaInstance.end()) {
//                            if (*i >= *j) {
//                                //i = pf[k].sigmaInstance.erase(i);
//                                j = pf[k + 1].sigmaInstance.erase(j);
//                            }
//
//                            else {
//                                i++, j++;
//                            }
//                        }
//                    }
//                }
//            }
//        }
//    }
//    if (pattern == "IBJI") {
//        cout << "sequence: " << sequence << ", support: " << support << endl;
//    }
//    return double(support) / sequence.length(); //这这这这这
//}
//
//// 计算当前模式在序列集下的count和r
//double CalcPatternRate(string pattern, vector<string> sequenceSet, vector<compressed_next*>& nextSet, double raurau)
//{
//    if (sequenceSet.size() == 0) {
//        return 0;
//    }
//
//
//    int count = 0;
//    int has_valid = 0;
//    for (int i = 0; i < sequenceSet.size(); i++) {
//        if (pattern.length() <= sequenceSet[i].length()) {
//            has_valid = 1;
//            break;
//        }
//    }
//    if (has_valid == 0)
//        return 0;
//    //cout << "size:" << sequenceSet.size();
//    for (int i = 0; i < sequenceSet.size(); i++) {
//        double rau_next;
//        if (false) {
//            rau_next = double((*(*nextSet[i])[pattern[0]]).size()) / sequenceSet[i].size();
//        }
//        else {
//            rau_next = CalcPatternDimensionWithCompressed(pattern, sequenceSet[i]);
//        }
//        if (rau_next >= raurau) {
//            count++;
//        }
//    }
//    return double(count) / sequenceSet.size();
//}
//
//
//
//
//double Top_k_Positive(double raurau, int k)
//{
//    int condidate_pattern_count = 0;
//    // 生成候选模式的大顶堆，
// queue<PatternInfo> G;
//    // 符合要求的sigma集合
//    vector<PatternInfo> E;
//    // top-k模式，最终的结果集，按照对比度降序计算前k个模式
//    // F是小顶堆，每次需要拿F中最小的和要加入的做对比
//    PatternInfo* minPattern = nullptr;
//    // 第一趟遍历初始的sigma集合，计算支持度放到堆里
//    for (auto i = Sigma.begin(); i != Sigma.end(); ++i) {
//        (*i).RatePos = CalcPatternRate((*i).P, PositiveSeq, PositiveNext, raurau);   //计算正类的r
//        (*i).RateNeg = CalcPatternRate((*i).P, NegativeSeq, NegativeNext, raurau);   //计算负类的r
//        (*i).Contrast = (*i).RatePos - (*i).RateNeg;
//        if (minPattern == nullptr || i->Contrast < minPattern->Contrast) {    //得到F中的最小值
//            minPattern = &(*i);
//        }
//        if (i->RatePos > 0 && i->RatePos > minPattern->Contrast) {
//            G.push(*i);
//            condidate_pattern_count++;
//        }
//        if (i->RatePos > 0) {
//            E.push_back(*i);
//        }
//        if ((F1.size() < k && (*i).Contrast > 0) || (F1.size() >= k && (*i).Contrast > F1.top().Contrast)) {
//            if (F1.size() >= k) {
//                F1.pop();
//            }
//            F1.push((*i));
//        }
//    }
//    // E        ֧ ֶȽ       
//    
//    while (!G.empty()) {
//        PatternInfo p = G.front();
//        G.pop();
//        for (auto j = E.begin(); j != E.end(); ++j) {
//            PatternInfo q;
//            q.P = p.P + j->P;
//            q.RatePos = CalcPatternRate(q.P, PositiveSeq, PositiveNext, raurau);
//            if (q.RatePos == 0 || (F1.size() >= k && q.RatePos <= F1.top().Contrast)) {
//                continue;
//            }
//            q.RateNeg = CalcPatternRate(q.P, NegativeSeq, NegativeNext, raurau);
//            q.Contrast = q.RatePos - q.RateNeg;
//            p.Contrast = p.RatePos - p.RateNeg;
//            if (q.Contrast <= p.Contrast) {
//                //Fx.push(q);
//                G.push(q);//先加入到候选模式中
//                condidate_pattern_count++;
//            }
//            else {
//                G.push(q);
//                condidate_pattern_count++;
//                if ((F1.size() < k && q.Contrast > 0) || (F1.size() >= k && q.Contrast > F1.top().Contrast)) {
//                    if (F1.size() >= k) {
//                        F1.pop();
//                    }
//                    F1.push(q);
//                }
//            }
//        }
//        //G.pop();
//    }
//    double result=0;
//    	if (F1.size() != 0) {
//		 result = F1.top().Contrast;//记录下来最小对比度
//	}
//   
//    total_condidate_pattern_count += condidate_pattern_count;
//    while (!F1.empty()) {
//        cout << "F1.top()" << F1.top().P << ": " << F1.top().Contrast << endl;
//        F.push(F1.top());
//        F1.pop();
//    }
//    cout << "生成的正向候选模式总数：" << condidate_pattern_count << endl;
//    return result;
// 
//}
//
//void Top_k_Negative(double raurau, int k, double pos_min_contrast) {
//    int condidate_pattern_count = 0;
//    // 生成候选模式的大顶堆，
//    queue<PatternInfo> G;
//    // 符合要求的sigma集合
//    vector<PatternInfo> E;
//    // top-k模式，最终的结果集，按照对比度降序计算前k个模式
//    // F是小顶堆，每次需要拿F中最小的和要加入的做对比
//
//    PatternInfo* minPattern = nullptr;
//    // 第一趟遍历初始的sigma集合，计算支持度放到堆里
//    for (auto i = Sigma.begin(); i != Sigma.end(); ++i) {
//        (*i).RatePos = CalcPatternRate((*i).P, PositiveSeq, PositiveNext, raurau);   //计算正类的r
//        (*i).RateNeg = CalcPatternRate((*i).P, NegativeSeq, NegativeNext, raurau);   //计算负类的r
//        (*i).Contrast = (*i).RateNeg - (*i).RatePos;
//        if (minPattern == nullptr || i->Contrast < minPattern->Contrast) {    //得到F中的最小值
//            minPattern = &(*i);
//        }
//        if (i->RateNeg > 0 && i->RateNeg > minPattern->Contrast && i->RateNeg > pos_min_contrast) {
//            G.push(*i);
//            condidate_pattern_count++;
//        }
//        if (i->RateNeg > 0) {
//            E.push_back(*i);
//        }
//        if ((F2.size() < k && (*i).Contrast > 0) || (F2.size() >= k && (*i).Contrast > F2.top().Contrast)) {
//            // 如果当前模式的支持度大于正向集top_k最小的支持度，才放到F中
//            if ((*i).RateNeg > pos_min_contrast) {
//                if (F2.size() >= k) {
//                    F2.pop();
//                }
//                F2.push((*i));
//            }
//        }
//    }
//    // E        ֧ ֶȽ       
//  
//    while (!G.empty()) {
//        PatternInfo p = G.front();
//        G.pop();
//        for (auto j = E.begin(); j != E.end(); ++j) {
//            PatternInfo q;
//            q.P = p.P + j->P;
//            q.RateNeg = CalcPatternRate(q.P, NegativeSeq, NegativeNext, raurau);
//            if (q.RateNeg == 0 || q.RateNeg <= pos_min_contrast || (F2.size() >= k && q.RateNeg <= F2.top().Contrast)) {
//                continue;
//            }
//            q.RatePos = CalcPatternRate(q.P, PositiveSeq, PositiveNext, raurau);
//            q.Contrast = q.RateNeg - q.RatePos;
//            p.Contrast = p.RateNeg - p.RatePos;
//            if (q.Contrast <= p.Contrast) {
//
//                G.push(q);//先加入到候选模式中
//                condidate_pattern_count++;
//            }
//            else {
//                G.push(q);
//                condidate_pattern_count++;
//                if ((F2.size() < k && q.Contrast > 0) || (F2.size() >= k && q.Contrast > F2.top().Contrast)) {
//                    if (F2.size() >= k) {
//                        F2.pop();
//                    }
//                    F2.push(q);
//                }
//            }
//        }
//        //G.pop();
//    }
//    total_condidate_pattern_count += condidate_pattern_count;
//    while (!F2.empty()) {
//        cout << "F2.top()" << F2.top().P << ": " << F2.top().Contrast << endl;
//        if ((F.size() < k && F2.top().Contrast > 0) || (F.size() >= k && F2.top().Contrast > F.top().Contrast)) {
//            if (F.size() >= k) {
//                F.pop();
//            }
//            F.push(F2.top());
//        }
//        F2.pop();
//    }
//    cout << "生成的负向候选模式总数：" << condidate_pattern_count << endl;
//}
//
//void CalcSigma()
//{
//    for (int i = 0; i < TotalSeq.size(); i++) {
//        for (int j = 0; j < TotalSeq[i].length(); j++) {
//            InitSigma.insert(TotalSeq[i][j]);
//        }
//    }
//    for (auto i = InitSigma.begin(); i != InitSigma.end(); ++i) {
//        stringstream stream;
//        stream << (*i);
//        string str = stream.str();
//        PatternInfo temp;
//        temp.P = str;
//        Sigma.push_back(temp);
//    }
//    for (auto i = Sigma.begin(); i != Sigma.end(); ++i) {
//        cout << (*i).P << endl;
//    }
//}
//
//// 用来计算单个序列的compressed_next
//compressed_next* CalcSequenceCompressedNext(string sequence)
//{
//    compressed_next* next = new compressed_next;
//    for (int i = 0; i < sequence.length(); i++) {
//        if ((*next).find(sequence[i]) == (*next).end()) {
//            vector<int>* v = new vector<int>;
//            v->push_back(i);
//            (*next)[sequence[i]] = v;
//        }
//        else {
//            (*next)[sequence[i]]->push_back(i);
//        }
//    }
//
//    return next;
//}
//
//next_v2* CalcCompressedNextV2(string sequence)
//{
//    next_v2* next = new next_v2;
//
//    return next;
//}
//
//
//void ReadFile()
//{
//    fstream dataSetFile;
//    string temp;
//    cout << "fileName:" << fileName << endl;
//    dataSetFile.open(fileName, ios::in);
//    while (dataSetFile >> temp) {
//        TotalSeq.push_back(temp);
//    }
//    dataSetFile.close();
//    if (filetype == 1) {
//        for (int i = 0; i < TotalSeq.size(); i++) {
//            if (TotalSeq[i][0] == '1') {
//                string s1 = TotalSeq[i].substr(1);
//                PositiveSeq.push_back(s1);
//                compressed_next* next = CalcSequenceCompressedNext(s1);
//                PositiveNext.push_back(next);
//            }
//            if (TotalSeq[i][0] == '2') {
//                string s1 = TotalSeq[i].substr(1);
//                NegativeSeq.push_back(s1);
//                compressed_next* next = CalcSequenceCompressedNext(s1);
//                NegativeNext.push_back(next);
//            }
//        }
//    }
//    else {
//        for (int i = 0; i < TotalSeq.size(); i++) {
//            if (i < 100) {
//                PositiveSeq.push_back(TotalSeq[i]);
//                compressed_next* next = CalcSequenceCompressedNext(TotalSeq[i]);
//                PositiveNext.push_back(next);
//            }
//            else {
//                NegativeSeq.push_back(TotalSeq[i]);
//                compressed_next* next = CalcSequenceCompressedNext(TotalSeq[i]);
//                NegativeNext.push_back(next);
//            }
//        }
//    }
//}
//void PrintMemoryUsage()
//{
//    PROCESS_MEMORY_COUNTERS pmc;
//    GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc));
//    std::cout << "Memory Usage: " << std::fixed << std::setprecision(2) << pmc.WorkingSetSize / (1024.0 * 1024.0) << " MB" << std::endl;
//}
//int main()
//{
//    ReadFile();     // 从文件读取数据集
//
//    CalcSigma();    // 计算序列的字符集
//    clock_t start, end;//定义clock_t变量
//    start = clock();//开始时间
//    double pos_res = Top_k_Positive(raurau, k);
//    Top_k_Negative(raurau, k, pos_res);
//    cout << "生成的双向候选模式总数: " << total_condidate_pattern_count << endl;
//    while (!F.empty()) {
//        cout << "F.top()" << F.top().P << ": " << F.top().Contrast << endl;
//        F.pop();
//    }
//    end = clock();   //结束时间
//    cout << "time = " << double(end - start) / CLOCKS_PER_SEC << "s" << endl;  //输出时间（单位：ｓ）
//    cout << "calc next time: " << double(calc_next_time) / CLOCKS_PER_SEC << "s" << endl;
//    //    string pattern = "IBI";
//    //    string sequence = "AJBDBEJJBJIIAHIHIBJBJAIBIHAGIBJ";
//    //    compressed_next* next = CalcSequenceCompressedNext(sequence);
//    //    double rau = CalcPatternDimensionWithCompressed(pattern, sequence, next);
//    //    //        cout << "sequence[" << i << "]: " << PositiveSeq[i] << endl;
//    //    cout << "rau" << ": "<< rau << endl;
//
//    //    for (int i = 0; i < NegativeSeq[i].length();i++) {
//    //        double rau = CalcPatternDimensionWithCompressed(pattern, NegativeSeq[i], NegativeNext[i]);
//    //        cout << "rau[" << i << "]: "<< rau << endl;
//    //        cout << "sequence[" << i << "]: " << NegativeSeq[i] << endl;
//    //    }
//
//
//
//    //    next_type next = CalcSequenceNext("abcab");
//    //    for (int i = 0; i < next.size(); i++) {
//    //        for (auto j = next[i].begin(); j != next[i].end(); ++j) {
//    //            cout << "next[" << i << "][" << j->first << "]=" << j->second << endl;
//    //        }
//    //    }
//    PrintMemoryUsage(); // Output memory usage
//    return 0;
//}
//
//
//
//
//
//
