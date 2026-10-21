
#ifndef OPST_EXTENSION_ORACLE_H
#define OPST_EXTENSION_ORACLE_H

#include <vector>

#include "DerivedWTInt.h"
#define NA -1
using namespace std;
class oracle {

public:
    vector<int> w;

    int rangeThreshold;
    int terminate_label;
    bool waveletFlag ;
    double waveletTime;

    int n;
    DerivedWTInt wt;
    oracle(vector<int> & w, int &rangeThreshold);

    //predecessor
    int Max(const sdsl::wt_int<>::node_type& u, int a, int b);
    int predecessorNV(int a, int b);
    int predecessorWT(const sdsl::wt_int<>::node_type& u, int a, int b);


    pair<int, int> LastCode(int a , int b);
    int LastCodeInt(int a, int b);

    ~oracle();

};


#endif //OPST_EXTENSION_ORACLE_H
