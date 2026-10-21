#ifndef OPST_H
#define OPST_H

#include <string>
#include <map>
#include "node.h"
#include "cmdline.h"

#include <sdsl/wavelet_trees.hpp>
#include <iostream>
#include <random> // For std::mt19937 and std::uniform_int_distribution
#include <cstdlib> // For std::exit
using namespace sdsl;
//#define RANGE_THRESHOLD 10
//#define SiZE_THRESHOLD 5
//#define VERBOSE
#define NA -1

using namespace std;

class DerivedWTInt : public sdsl::wt_int<> {
public:

    using wt_int<>::wt_int;

    int rank_bit( value_type c, int i,size_type offset) const;

    int select_bit( value_type c, int i, const node_type& node) const;


};


class OPST
{
private:

//    int_vector<> w;
    vector<int> w;

    int rangeThreshold;

    DerivedWTInt wt;
    double waveletTime;
    bool waveletFlag ;


public:
//    explicit OPST(vector<int> & w, int &rangeThreshold, size_t &memory);
    explicit OPST(vector<int> & w, int &rangeThreshold);


//predecessor
    int Max(const sdsl::wt_int<>::node_type& u, int a, int b);
    int predecessorNV(int a, int b);
    int predecessorWT(const sdsl::wt_int<>::node_type& u, int a, int b);


// LastCodeInt
    int LastCodeInt(int a, int b);

    pair<int, int>  LastCode( int a, int b);



    stNode * createNode(  stNode * u, int d );
    void createLeaf(int i, stNode * u, int d );
    void ComputeSuffixLink( stNode * u );


    // Maximal
    void MaxTauDFS(int tau);
    void MaxFindNodes(std::unordered_map<stNode*, int> &MaxTauNodes);

//    void MaxFindNodes(vector<stNode*> &MaxTauNodes);
//    void ClosedFindNodes(vector<stNode*> &ClosedTauNodes);


//    Closed
    stNode* FindLCA(stNode* node);

    void ClosedTauDFS(int tau);
    void ClosedFindNodes(std::unordered_map<stNode*, int> &ClosedTauNodes);



//    std::vector<stNode*> MaxTauNodes;

    unordered_map<int,stNode*> pos2leaf;

//    int explicit_k = 0;
    int n; // the length of w
    int terminate_label;
    stNode * root;

    void deleteTreeIteratively();
    ~OPST();
};







#endif
