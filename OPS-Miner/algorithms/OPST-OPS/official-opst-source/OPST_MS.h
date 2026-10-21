#ifndef OPST_MS_H
#define OPST_MS_H


#include <string>
#include <map>
#include "node.h"
#include "cmdline.h"

//#include "Predecessor.h"
//#include "Successor.h"

#include <iostream>
#include <random> // For std::mt19937 and std::uniform_int_distribution
#include <cstdlib> // For std::exit
#include "DerivedWTInt.h"
#include "oracle.h"

#include <sdsl/bit_vectors.hpp>					  // include header for bit vectors
#include <sdsl/rmq_support.hpp>					  //include header for range minimum queries
//#include "stack.h"        					  // include header for stack structure

using namespace std;
using namespace sdsl;
//#define RANGE_THRESHOLD 10
//#define SiZE_THRESHOLD 5
//#define VERBOSE
#define NA -1
extern long long memory_usage();

using namespace std;




class OPST_MS{
private:

//    int_vector<> w;
    vector<int> w;

    int rangeThreshold;

    DerivedWTInt wt;
    double waveletTime;
    bool waveletFlag ;


public:
//    explicit OPST(vector<int> & w, int &rangeThreshold, size_t &memory);
    explicit OPST_MS(vector<int> & w, int &rangeThreshold);

    int * forward_search( oracle &B_tmp);

//predecessor
    int Max(const sdsl::wt_int<>::node_type& u, int a, int b);
    int predecessorNV(int a, int b);
    int predecessorWT(const sdsl::wt_int<>::node_type& u, int a, int b);

// LastCodeInt
    int LastCodeInt(int a, int b);

    pair<int, int>  LastCode( int a, int b);



    stNode * createNode(  stNode * u, int d );
    void createLeaf(int i, stNode * u, int d );
//    void ComputeSuffixLink( stNode * u );

    void ComputeSuffixLinkBP( stNode * u );
    void ComputeSuffixLink( stNode * u );

    // Maximal
//    void MaxTauDFS(int tau);
//    void MaxFindNodes(std::unordered_map<stNode*, int> &MaxTauNodes);

//    void MaxFindNodes(vector<stNode*> &MaxTauNodes);
//    void ClosedFindNodes(vector<stNode*> &ClosedTauNodes);


//    Closed
//    stNode* FindLCA(stNode* node);

//    void ClosedTauDFS(int tau);
//    void ClosedFindNodes(std::unordered_map<stNode*, int> &ClosedTauNodes);



//    std::vector<stNode*> MaxTauNodes;

    unordered_map<int,stNode*> pos2leaf;

//    int explicit_k = 0;
    int n; // the length of w
    int terminate_label;
    stNode * root;


    // Visualization
    unordered_map<int, pair<int, int>> int2ps;

    void int2psInsert(int a, int b);
    void exportSuffixTreeToDot(const std::string& filename,bool suf);
    void generateDot(stNode* node, std::ofstream& dotFile, bool suf);
    void generateCount(stNode* node, std::ofstream& dotFile, bool suf);




    void deleteTreeIteratively();
    ~OPST_MS();
};















#endif
