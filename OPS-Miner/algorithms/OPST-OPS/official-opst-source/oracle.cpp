


#include <iostream>
#include <string>
#include <stack>
#include <cstring>
#include <unordered_set>

#include "oracle.h"

oracle::oracle(vector<int> & w, int &rangeThreshold){
    this->w = w;
    this->n = w.size();
    terminate_label = 2 * this->n + 1;
    waveletFlag = false;

    this->rangeThreshold = rangeThreshold;
}



int oracle::Max(const sdsl::wt_int<>::node_type& u, int a, int b) {

    if (wt.is_leaf(u)){

        return b;
    }else if (wt.rank_bit(1, a, u.offset) == wt.rank_bit(1, b, u.offset)) {
#ifdef VERBOSE
        cout<<"Max: a: "<<(int )wt.rank_bit(0, a, u.offset)<<endl;
        cout<<"Max: b: "<<(int )wt.rank_bit(0, b, u.offset)<<endl;
        cout<<"Max: "<< Max(wt.expand(u)[0], wt.rank_bit(0, a, u.offset) - 1, wt.rank_bit(0, b, u.offset) - 1)<<endl;

#endif

        return wt.select_bit(0, Max( wt.expand(u)[0], wt.rank_bit(0, a, u.offset) - 1, wt.rank_bit(0, b, u.offset) - 1) + 1, u);
    } else {
#ifdef VERBOSE

        cout<<"Max: a: "<<(int )wt.rank_bit(1, a, u.offset)<<endl;
        cout<<"Max: b: "<<(int )wt.rank_bit(1, b, u.offset)<<endl;
        cout<<"Max: "<< Max(wt.expand(u)[1], wt.rank_bit(1, a, u.offset) - 1, wt.rank_bit(1, b, u.offset) - 1)<<endl;

#endif

        return wt.select_bit(1, Max(wt.expand(u)[1], wt.rank_bit(1, a, u.offset) - 1, wt.rank_bit(1, b, u.offset) - 1) + 1, u);
    }
}





int oracle::predecessorWT(const sdsl::wt_int<>::node_type& u, int a, int b) {


    if (a == b) return NA; // predecessor does not exist

    if (!wt.is_leaf(u)) {
        auto B_u = wt.bit_vec(u); // get the bit vector of u

        auto x = B_u[b + 1];



        int pos = predecessorWT(wt.expand(u)[x], wt.rank_bit(x, a, u.offset)-1, wt.rank_bit(x, b, u.offset)-1);// For counting 1s.


        if (pos != NA) {

            return wt.select_bit(x, pos + 1, u);
        } else if (x == 0 || wt.rank_bit(0, a, u.offset) == wt.rank_bit(0, b, u.offset)) {

            return NA;
        } else {

            return wt.select_bit(0, Max( wt.expand(u)[0], wt.rank_bit(0, a, u.offset)-1, wt.rank_bit(0, b, u.offset) - 1) + 1, u);
        }
    } else {
        return b;
    }
}


int oracle::predecessorNV(int a, int b) {
    if (w.empty()) return -1; // Handle empty vector case


    int aimElement = w[b];
    int predecessorIndex = NA; // Default to "not found"
    // Find the rightmost occurrence of the smallest element greater than or equal to the aimelement
    if (b < 0){
        return predecessorIndex;
    }
    if (a < 0){
        for (int j = 0; j < b ; ++j) {
            if (w[j] <= aimElement) {
                if (predecessorIndex == NA || w[j] >= w[predecessorIndex]) {
                    predecessorIndex = j;
                }
            }
        }

    } else{

        for (int j = a; j < b ; ++j) {
            if (w[j] <= aimElement) {
                if (predecessorIndex == NA || w[j] >= w[predecessorIndex]) {
                    predecessorIndex = j;
                }
            }
        }

    }

    return predecessorIndex;
}






pair<int, int> oracle::LastCode(int a , int b){

    if ( b -a < rangeThreshold) {


        int predecessor_local = predecessorNV(a, b);


        int successor_local;

        //if predecessor_local is -1, successor is set to notEqual(0)
        if(predecessor_local<0){
            successor_local = 0;
        } else{

            successor_local = (int) (w[predecessor_local] == w[b]);

        }

        if (predecessor_local != NA) {
            predecessor_local = predecessor_local - a;
        }
//        cout<<predecessor_local<<successor_local<<endl;


        return make_pair(predecessor_local, successor_local);

    } else{

        // construct wavelet tree for LastCodeInt only when necessarily

        if (!waveletFlag){
            auto wavelet_start = std::chrono::high_resolution_clock::now();
            sdsl::int_vector<> uint64_vec;
            uint64_vec.resize(w.size());
            for(size_t i = 0; i < w.size(); ++i) {
                uint64_vec[i] = (uint64_t)w[i];
            }
            construct_im(wt,uint64_vec);
            auto wavelet_end = std::chrono::high_resolution_clock::now();

            this->waveletTime = std::chrono::duration_cast < std::chrono::milliseconds > (wavelet_end - wavelet_start).count()*0.001;
            waveletFlag = true;
//            cout<<"It is necessary to construct the wavelet tree for b-a > "<< rangeThreshold<<endl;
//            cout<<"sigma of input = "<<wt.sigma<<endl;
//            cout<< "Runtime for wavelet tree construction  = "<<waveletTime<<" s."<<endl;
//            cout<<"oracle"<<endl;
        }


        int predecessor_local = predecessorWT(wt.root(), a-1, b-1);

        int successor_local;

        //if predecessor_local is -1, successor is set to notEqual(0)

        if(predecessor_local<0){
            successor_local = 0;
        } else{

            successor_local = (int) (w[predecessor_local] == w[b]);

        }

        if (predecessor_local != NA){
            predecessor_local = predecessor_local - a;
        }
//        cout<<predecessor_local<<successor_local<<endl;
        return make_pair(predecessor_local,successor_local);

    }

}



int oracle::LastCodeInt(int a, int b) {
    // call LastCode
    // b = n, returns terminate_label: 2 * n + 1
    if (b != n){
        pair<int, int> ab = this->LastCode(a, b);
//        cout<<"Oracle of B("<<a<<","<<b<<"): "<<ab.first <<","<<ab.second<<"; LastInt: "<<ab.first * 2 + ab.second<<endl;

        return (ab.first * 2 + ab.second);

    } else{
        return terminate_label;

    }

}




oracle::~oracle(){

}
