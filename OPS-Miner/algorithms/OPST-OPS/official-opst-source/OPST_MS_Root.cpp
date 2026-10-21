
#include <iostream>
#include <string>
#include <sdsl/wavelet_trees.hpp>
#include <fstream>


//#include "Successor.h"
//#include "Predecessor.h"

#include "OPST_MS.h"

//#include "baseline.h"
#include "oracle.h"
using namespace std;
using namespace sdsl;
#include <filesystem>
//#define terminate_label 0
//#include "cmdline.h"
#include "malloc.h"



void readfile(const string &filename, std::vector<int> &normalVec){
    std::ifstream f(filename);
    if (!f) {
        std::cerr << "Unable to open file: " << filename << std::endl;
        return;
    }


    int c;
    while (f >> c) {
        normalVec.push_back(c);
    }
    f.close();

}
std::string get_filename(const std::string& path) {

    size_t last_slash_idx = path.find_last_of("/\\");
    if (last_slash_idx == std::string::npos) {
        return path;
    }
    return path.substr(last_slash_idx + 1);
}

std::string get_grandparent_directory(const std::string& path) {
    // 找到最后一个斜杠的位置
    size_t last_slash_idx = path.find_last_of("/\\");
    if (last_slash_idx == std::string::npos) {
        return "";  // 没有斜杠，没有上级目录
    }
    // 获取去掉最后一个斜杠后的子串，并再次寻找斜杠
    size_t second_last_slash_idx = path.substr(0, last_slash_idx).find_last_of("/\\");
    if (second_last_slash_idx == std::string::npos) {
        return "";  // 只有一个斜杠，没有上级的上级目录
    }
    return path.substr(0, second_last_slash_idx);  // 返回第二个最后斜杠之前的部分
}



// input: suffix tree built from input_vecA, input_vecB oracle
// output: vector<int> ms_table, ms[i]: the longest length of  T[i..] could match with P

void compute_matching_statistics(OPST_MS& OP, oracle &B_oracle, vector<int> &ms_table) {
    auto root = OP.root;
    stNode* v = root;
    int matched = 0;
    int i = 0;
    while (i < ms_table.size()) {
        stNode* u = v;


        int distance_below_u = 0;

        while (i +  matched < ms_table.size()) {
            int j = 0;
            int next_char = B_oracle.LastCodeInt(i , i + matched);
            stNode* child = u->getChild(next_char);
            if (!child) break;
            j++; // the match of length is at least 1

            // current length of edge = child->depth - u->depth
            int edge_len = child->depth - u->depth;


            while (j < edge_len && i + matched + j < ms_table.size()) {

                int T_char = B_oracle.LastCodeInt(i, i +  matched + j);
                int P_char = OP.LastCodeInt(child->start , child->start + matched + j);

                if (T_char != P_char) break;
                j++;


            }

            matched += j;

            if (j < edge_len) {
                distance_below_u = matched - u->depth;
                break;  // cannot match the whole edge
            }
            u = child; // match the whole edge，u -> child
        }

        ms_table[i] = matched;

        // 设置下一轮的起始节点和匹配长度
        if (matched == 0 || u == root) {
            v = root;
            matched = 0;
        } else if (u->slink) {
            v = u->slink;
            matched = matched - 1 - distance_below_u;
            assert(matched >= 0);
        } else {
            while (u->slink == NULL){
                u = u->parent;
            }
            v = u->slink;
            matched = v->depth;
        }

        i++;
    }
}






void forward_search(OPST_MS& OP, oracle &B_oracle, vector<int> &ms_table) {
    auto root = OP.root;
    stNode* v = root;
    int matched = 0;

    int i = 0;
    while (i < ms_table.size()) {
        stNode* u = v;

        while (i +  matched < ms_table.size()) {
            int j = 0;
            int next_char = B_oracle.LastCodeInt(i , i + matched);
            stNode* child = u->getChild(next_char);
            if (!child) break;
            j++; // the match of length is at least 1

            int edge_len = child->depth - u->depth;


            while (j < edge_len && i + matched + j < ms_table.size()) {

                int T_char = B_oracle.LastCodeInt(i, i +  matched + j);
                int P_char = OP.LastCodeInt(child->start , child->start + matched + j);

                if (T_char != P_char) break;
                j++;

//                cout<<"-------------------------"<<endl;

            }

            matched += j;

            if (j < edge_len) break;  // 匹配未走完整条边，终止
            u = child; // 边匹配完，进入 child 节点
        }

        ms_table[i] = matched;


        v = root;
        matched = 0;
        i++;
    }
}


vector<pair<int, int>> pattern_matching_MS(
        oracle& P_oracle,
        oracle& T_oracle,
        int_vector<>& SA,
        int* LCP,
        rmq_succinct_sct<>& rmq,
        vector<int>& ms_table
) {
    int m = P_oracle.n;
    int n = T_oracle.n;
    vector<pair<int, int>> match_pos(m);  // 每个 i 返回 (匹配位置, 匹配长度)

    for (int i = 0; i < m; ++i) {
        int d = -1, ld = 0;
        int f = n, lf = 0;
        int best_len = 0;
        int best_pos = -1;

        while (d + 1 < f) {
            int mid = (d + f) / 2;

            int lcpif = (f == n) ? 0 : LCP[rmq(mid + 1, f)];
            int lcpdi = (mid == n) ? 0 : LCP[rmq(d + 1, mid)];

            if ((ld <= lcpif) && (lcpif < lf)) {
                d = mid; ld = lcpif;
            } else if ((ld <= lf) && (lf < lcpif)) {
                f = mid;
            } else if ((lf <= lcpdi) && (lcpdi < ld)) {
                f = mid; lf = lcpdi;
            } else if ((lf <= ld) && (ld < lcpdi)) {
                d = mid;
            } else {
                int l = std::max(ld, lf);

                while ((i + l < m) && (SA[mid] + l < n) &&
                       P_oracle.LastCodeInt(i, i + l) == T_oracle.LastCodeInt(SA[mid], SA[mid] + l)) {
                    l++;
                }

                if (l > best_len) {
                    best_len = l;
                    best_pos = SA[mid];
                }

                if ((SA[mid] + l < n) &&
                    P_oracle.LastCodeInt(i, i + l) > T_oracle.LastCodeInt(SA[mid], SA[mid] + l)) {
                    d = mid; ld = l;
                } else {
                    f = mid; lf = l;
                }
            }
        }

        ms_table[i] = best_len;
        match_pos[i] = {best_pos, best_len};
    }

    return match_pos;
}


//
//pair<int,int> compute_ms_with_binary(oracle& P_oracle, oracle& T_oracle, int* SA, int* LCP, rmq_succinct_sct<>& rmq, vector<int>& ms_table, int i) {
//    int d = -1;        // 二分搜索左边界
//    int ld = 0;        // 左边界匹配长度
//    int f = T_oracle.n;  // 二分搜索右边界
//    int lf = 0;        // 右边界匹配长度
//
//    pair<int,int> interval;
//
//    // 二分搜索
//    while (d + 1 < f) {
//        int mid = (d + f) / 2;
//
//        // 计算mid与两个边界之间的LCP
//        int lcpif = (f == T_oracle.n) ? 0 : LCP[rmq(mid + 1, f)];
//        int lcpdi = (mid == T_oracle.n) ? 0 : LCP[rmq(d + 1, mid)];
//
//        if ((ld <= lcpif) && (lcpif < lf)) {
//            d = mid;
//            ld = lcpif;
//        }
//        else if ((ld <= lf) && (lf < lcpif)) {
//            f = mid;
//        }
//        else if ((lf <= lcpdi) && (lcpdi < ld)) {
//            f = mid;
//            lf = lcpdi;
//        }
//        else if ((lf <= ld) && (ld < lcpdi)) {
//            d = mid;
//        }
//        else {
//            // 计算当前位置的匹配长度
//            int l = std::max(ld, lf);
//            int matched = 0;
//
//            while (i + matched < T_oracle.n) {
//                int T_char = T_oracle.LastCodeInt(i, i + matched);
//                int P_char = P_oracle.LastCodeInt(mid, mid + matched);
//
//                if (T_char != P_char) break;
//                matched++;
//            }
//
//            l += matched;
//
//            if (l == T_oracle.n - i) {
//                d = mid;
//                ld = l;
//            }
//            else {
//                f = mid;
//                lf = l;
//            }
//
//            // 更新MS值
//            ms_table[i] = std::max(ms_table[i], l);
//        }
//    }
//
//    interval.first = d + 1;
//    interval.second = f - 1;
//    return interval;
//}
//


unsigned int LCParray( oracle & text, int n,sdsl::int_vector<>& SA, int * ISA, int * LCP )
{
    int i=0, j=0;

    LCP[0] = 0;
    for ( i = 0; i < n; i++ ) // compute LCP[ISA[i]]
        if ( ISA[i] != 0 )
        {
            if ( i == 0) j = 0;
            else j = (LCP[ISA[i-1]] >= 2) ? LCP[ISA[i-1]]-1 : 0;
            while ( text.LastCodeInt(i,i+j) == text.LastCodeInt(SA[ISA[i]-1], SA[ISA[i]-1]+j)){
                j++;
            }
            LCP[ISA[i]] = j;
        }

    return ( 1 );
}


int main(int argc, char *argv[])
{


    cmdline::parser parser;
    parser.add<string>("filepathW", 'w', "the path to input file W", false, "inputW.txt");
    parser.add<string>("filepathP", 'p', "the path to input file P", false, "inputP.txt");


    parser.add<int>("rangeThreshold", 'r', "the range of (a,b) determines call the naive or wavelet tree method", false, 512);


    parser.parse_check(argc, argv);

    string filenameW = parser.get<string>("filepathW");
    string filenameP = parser.get<string>("filepathP");
    int rangeThreshold = parser.get<int>("rangeThreshold");



    cout<<"--------------------------------------------Information Board--------------------------------------------------------"<<endl;

    cout<<"Enabling OPST maximal method"<<endl;

    cout<< "Comparing "<<filenameW<<" and "<<filenameP<<endl;


    // read file A to input_vecA
    vector<int> input_vecA;
    readfile(filenameW, input_vecA);

    // read file A to input_vecB
    vector<int> input_vecB;
    readfile(filenameP, input_vecB);


    long long IndexSpace_start = memory_usage();

//    vector<int> MS_table(input_vecB.size(), 0);
    vector<int> MS_table2(input_vecB.size(), 0);

//    vector<int> MS_table3(input_vecB.size(), 0);

    // OPST construction of input A
    auto Construction_start = std::chrono::high_resolution_clock::now();

    OPST_MS OP(input_vecA, rangeThreshold);

    auto Construction_end = std::chrono::high_resolution_clock::now();
    double time_Construction = std::chrono::duration_cast < std::chrono::microseconds > (Construction_end - Construction_start).count()*0.000001;


    cout<<"The size of input W: "<<input_vecA.size()<<endl;
    cout<<"The size of input P: "<<input_vecB.size()<<endl;
//    cout<<"Terminate_label (2 * n + 1) $ = " << OP.terminate_label<<endl;

    cout<<"Runtime for only OPST construction of Input W = "<<time_Construction<<" s."<<endl;

//    OP.exportSuffixTreeToDot("max_no", false);
//    OP.exportSuffixTreeToDot("max", true);

    oracle B_oracle(input_vecB, rangeThreshold);


//    auto MS_start1 = std::chrono::high_resolution_clock::now();
//
//
//    compute_matching_statistics(OP, B_oracle, MS_table);
//
//    auto MS_end1 = std::chrono::high_resolution_clock::now();
//    double MS_Construction1 = std::chrono::duration_cast < std::chrono::microseconds > (MS_end1 - MS_start1).count()*0.000001;
//
//


    // search from the root everytime


    auto MS_start2 = std::chrono::high_resolution_clock::now();


    forward_search(OP, B_oracle, MS_table2);


    auto MS_end2 = std::chrono::high_resolution_clock::now();
    double MS_Construction2 = std::chrono::duration_cast < std::chrono::microseconds > (MS_end2 - MS_start2).count()*0.000001;
    long long IndexSpace_end = memory_usage();

    long long memory_Index = IndexSpace_end - IndexSpace_start;


    // independent pattern matching
//
//    auto MS_start3 = std::chrono::high_resolution_clock::now();
//
//
//    auto MS_end3 = std::chrono::high_resolution_clock::now();
//    double MS_Construction3 = std::chrono::duration_cast < std::chrono::microseconds > (MS_end3 - MS_start3).count()*0.000001;


//    for (int i = 0; i < MS_table.size(); ++i) {
//        if (MS_table[i] != MS_table3[i]) {
//            cout << "\n❌ Error at index " << i << ": MS = " << MS_table[i] << ", MS2 = " << MS_table3[i] << endl;
//
//            cout << "\n=== input_vecA (A) ===" << endl;
//            for (int x : input_vecA) cout << x << endl;
//            cout << "\n\n=== input_vecB (B) ===" << endl;
//            for (int x : input_vecB) cout << x << endl;
//            cout << "\n\n=== MS_table (ground truth) ===" << endl;
//            for (int x : MS_table) cout << x << " ";
//            cout << "\n\n=== MS_table2 (to be checked) ===" << endl;
//            for (int x : MS_table3) cout << x << " ";
//
//            cout << endl << "\n❗ Exiting due to mismatch." << endl;
//            exit(1);
//        }
//    }

//    cout<<"Terminate_label (2 * n + 1) $ = " << OP.terminate_label<<endl;

//    cout<<"Runtime for MS construction of our method (starting from root)= "<<MS_Construction1<<" s."<<endl;
    cout<<"Runtime for only MS construction of the competitor (starting from root)= "<<MS_Construction2<<" s."<<endl;
    cout<<"Total time for MS construction of the competitor (starting from root)= "<<MS_Construction2 + time_Construction<<" s."<<endl;

    cout<<"Index memory of counting: "<< memory_Index / (1024.0 * 1024.0)<<"MB"<<endl;



    cout<<"---------------------------------------------------------------------------------------------------------------------"<<endl;






    return 0;
}








