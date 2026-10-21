
#include <malloc.h>


#include "baseline.h"

//#include "Successor.h"
//#include "Predecessor.h"
//
long long memory_usage() {
    struct mallinfo2 mi = mallinfo2();
    return mi.uordblks + mi.hblkhd;
}







namespace karp_rabin_hashing {

//=============================================================================
// Base and exponent used in Karp-Rabin hashing.
//=============================================================================
    std::uint64_t hash_variable;
    std::uint64_t mersenne_prime_exponent;

//=============================================================================
// Return (a * b) mod p, where p = (2^k) - 1.
// Requires a, b <= 2^k. Tested for k = 1, .., 63.
//=============================================================================
    std::uint64_t mul_mod_mersenne(
            const std::uint64_t a,
            const std::uint64_t b,
            const std::uint64_t k) {
        const std::uint64_t p = ((std::uint64_t)1 << k) - 1;
        __extension__ const unsigned __int128 ab =
                (unsigned __int128)a *
                (unsigned __int128)b;
        std::uint64_t lo = (std::uint64_t)ab;
        const std::uint64_t hi = (ab >>  (uint64_t) 64);
        lo = (lo & p) + ((lo >> k) + (hi << ( (uint64_t) 64 - k)));
        lo = (lo & p) + (lo >> k);
        return lo == p ?  (uint64_t) 0 : lo;
    }

//=============================================================================
// Return a mod p, where p = (2^k) - 1.
// Works for any a in [0..2^64).
// Tested for k = 1, .., 63.
//=============================================================================
    std::uint64_t mod_mersenne(
            std::uint64_t a,
            const std::uint64_t k) {
        std::uint64_t p = ((std::uint64_t)1 << k) -  (uint64_t) 1;
        if (k < (uint64_t) 32) {

            // We need to check if a <= 2^(2k).
            const std::uint64_t threshold = ((std::uint64_t)1 << (k <<  (uint64_t) 1));
            if (a <= threshold) {
                a = (a & p) + (a >> k);
                a = (a & p) + (a >> k);
                return a == p ?  (uint64_t) 0 : a;
            } else return a % p;
        } else {

            // We are guaranteed that a < 2^(2k)
            // because a < 2^64 <= 2^(2k).
            a = (a & p) + (a >> k);
            a = (a & p) + (a >> k);
            return a == p ?  (uint64_t) 0 : a;
        }
    }

//=============================================================================
// Return random number x in [0..p), where p = (2^k) - 1.
//=============================================================================
    std::uint64_t rand_mod_mersenne(const std::uint64_t k) {
        const std::uint64_t p = ((std::uint64_t)1 << k) -  (uint64_t) 1;
        return utils::random_int<std::uint64_t>(
                (std::uint64_t)0, (std::uint64_t(p -  (uint64_t) 1)));
    }

//=============================================================================
// Return (a^n) mod p, where p = (2^k) - 1.
//=============================================================================
    std::uint64_t  pow_mod_mersenne(
            const std::uint64_t a,
            std::uint64_t n,
            const std::uint64_t k) {
        std::uint64_t pow = mod_mersenne(a, k);
        std::uint64_t ret = mod_mersenne( (uint64_t) 1, k);
        while (n >  (uint64_t) 0) {
            if (n &  (uint64_t) 1)
                ret = mul_mod_mersenne(ret, pow, k);
            pow = mul_mod_mersenne(pow, pow, k);
            n >>=  (uint64_t) 1;
        }
        return ret;
    }

//=============================================================================
// Given Karp-Rabin hashes of two substrings, return
// the Karp-Rabin hash of their concatenation.
//=============================================================================
    std::uint64_t concat(
            const std::uint64_t left_hash,
            const std::uint64_t right_hash,
            const std::uint64_t right_len) {
        const std::uint64_t pow = pow_mod_mersenne(
                hash_variable, right_len, mersenne_prime_exponent);
        const std::uint64_t tmp = mul_mod_mersenne(
                left_hash, pow, mersenne_prime_exponent);
        const std::uint64_t ret = mod_mersenne(
                tmp + right_hash, mersenne_prime_exponent);
        return ret;
    }
    std::uint64_t power(const std::uint64_t k)
    {
        return pow((uint64_t)2,k);
    }
    std::uint64_t subtract(const std::uint64_t long_hash, const std::uint64_t short_hash, const std::uint64_t right_len)
    {
        const std::uint64_t pow = pow_mod_mersenne(
                hash_variable, right_len, mersenne_prime_exponent);


        //mul_mod_mersenne requires a, b <= 2^k
        uint64_t max_pow=power(mersenne_prime_exponent);
        if(short_hash > max_pow || pow > max_pow || mersenne_prime_exponent > 63)
            cout<<"Error2";

        const std::uint64_t tmp = mul_mod_mersenne(
                short_hash, pow, mersenne_prime_exponent);

        if(long_hash < tmp)cout<<"error\n";
        const std::uint64_t ret = mod_mersenne(
                long_hash-tmp, mersenne_prime_exponent);

        return ret;
    }

//=============================================================================
// Initialize the base and exponent for Karp-Rabin hashing.
//=============================================================================
    void init() {
        mersenne_prime_exponent = 61;
        hash_variable = rand_mod_mersenne(mersenne_prime_exponent);
    }

}  // namespace karp_rabin_kashing








std::string generatePatternString(const std::vector<std::pair<int, int>>& sortedArray, int x) {
    std::stringstream patternStream;
    int n = sortedArray.size();

    for (int i = 0; i < n - 1; ++i) {

        int diff_a = sortedArray[i].first - x;

        patternStream << diff_a;

        if (sortedArray[i].second == sortedArray[i + 1].second) {

            patternStream << ",1,";
        } else {

            patternStream << ",0,";
        }
    }

    int diff_last = sortedArray[n - 1].first - x;
    patternStream << diff_last;

    return patternStream.str();
}





int cubicMethodMax(std::vector<int> &w, int &tau){
    karp_rabin_hashing::init();

//    std::vector<int> w = {1,2,4,1,2,4,1,2,4};
    int cnt_maximal = 0;
    int n = w.size();

    std::vector<std::vector<uint64_t>> H(2, std::vector<uint64_t>(n, 0));

    std::vector<std::unordered_map<uint64_t, int>> HT(2);

//
    for(int i = 0; i < n; ++i) {
        H[0][i] = 0;
    }
    HT[0][0] = n;
    bool flag;

    for(int k = 1; k < n; ++k) {
        flag = false;
        for (int i = 0; i < n - k; ++i) {
            cout<<k<<": "<<i<<endl;
//
            std::cout << "the range of w " << "(" << i << "," << k + i << ")" << std::endl;
            std::vector<std::pair<int, int>> subsequence;
            for (int j = i; j <= i + k; ++j) {
                subsequence.push_back({j, w[j]});
            }

            std::sort(subsequence.begin(), subsequence.end(),
                      [](const std::pair<int, int> &a, const std::pair<int, int> &b) {
                          if (a.second != b.second) {
                              return a.second < b.second;
                          } else {
                              return a.first < b.first;
                          }
                      });

            std::string patternString = generatePatternString(subsequence, i);

//            cout<<patternString<<" "<<patternString.c_str()<<" "<<patternString.size()<<endl;

            uint64_t hashValue  = karp_rabin_hashing::hash_string(patternString.c_str(),patternString.size());


            H[k % 2][i] = hashValue;
            int x = ++HT[k % 2][H[k % 2][i]];
            if (x >= tau) {
                flag = true;

                HT[(k-1)%2][H[(k-1)%2][i]] =0;
                HT[(k-1)%2][H[(k-1)%2][i+1]] =0;
            }
        }




        for (auto it :HT[(k - 1) % 2]) {
            if (it.second >= tau) {

                cnt_maximal ++;
//                    continue;
            }

        }


        HT[(k - 1) % 2].clear();
        if (!flag){
//            cout<<"break"<<endl;
            cout<<"The max length of patterns: "<<k<<endl;

            break;
        }

    }
    return cnt_maximal;
}





int quadraticMethodMax(std::vector<int> &w, int &tau){

//    size_t memory_start = memory_usage();
//    cout<<"Memory 1: "<<memory_start*0.001<<endl;
    karp_rabin_hashing::init();

    int cnt_maximal = 0;
    int n = w.size();

    std::vector<std::vector<uint64_t>> H(2, std::vector<uint64_t>(n, 0));

    std::vector<std::unordered_map<uint64_t, int>> HT(2);
    std::set<std::pair<int, int>> S;

    for(int i = 0; i < n; ++i) {
        H[0][i] = 0;
    }
    HT[0][0] = n;

    uint64_t odd_hashValue  = 2 * n;

    bool flag;
    for(int k = 1; k < n; ++k) {
        flag = false;
        //initialization of Set S
        S.clear();
        for (int j = 0; j < k; ++j) {
            S.insert({w[j], j});
        }
        for (int i = 0; i < n - k; ++i) {

            std::pair<std::set<pair<int, int>>::iterator, bool> current = S.insert({w[i+k] , i+k});


            auto it = current.first;
            if (it != S.begin()) { // make it is not the first element
                --it; // the iterator points to the element before current

                uint64_t appendix = 2*(it->second - i) + (int)(it->first == w[i+k]);

                H[k % 2][i] = karp_rabin_hashing::concat(H[(k - 1) % 2][i], appendix, 1);

            } else {


                H[k % 2][i] = karp_rabin_hashing::concat(H[(k - 1) % 2][i], odd_hashValue, 1);
            }

            int x = ++HT[k % 2][H[k % 2][i]];
            if (x >= tau) {
//                std::cout<<"Killed"<<std::endl;
                flag = true;
                HT[(k-1)%2][H[(k-1)%2][i]] =0;
                HT[(k-1)%2][H[(k-1)%2][i+1]] =0;

            }

            // window sliding
            if (i + k + 1 < n) {
                S.erase({w[i], i});

            }
        }

        for (auto it :HT[(k - 1) % 2]) {
            if (it.second >= tau) {

                cnt_maximal ++;

            }
        }


        HT[(k - 1) % 2].clear();//        std::vector<int> vec = {1,2,4,4,2,5,5,1};
        if (!flag){
            cout<<"The max length of patterns: "<<k<<endl;
//            cout<<"Memory 2: "<<memory_usage()*0.001<<endl;
//            cout<<"Memory difference: "<<(memory_usage()- memory_start)*0.001<<endl;

//            cout<<"break"<<endl;
            break;
        }
    }

//    size_t memory_end = memory_usage();
//    memory = memory_end-memory_start;
    return cnt_maximal;
}



int cubicMethodClosed(std::vector<int> &w, int &tau){

    karp_rabin_hashing::init();

//    std::vector<int> w = {1,2,4,1,2,4,1,2,4};
    int cnt_closed = 0;
    int n = w.size();


    std::vector<std::vector<uint64_t>> H(2, std::vector<uint64_t>(n, 0));

    std::vector<std::unordered_map<uint64_t, int>> HT(2);
//
    for(int i = 0; i < n; ++i) {
        H[0][i] = 0;
    }
    HT[0][0] = n;
    bool flag;

    for(int k = 1; k < n; ++k) {
        flag = false;
        for (int i = 0; i < n - k; ++i) {


//            std::cout << "the range of w " << "(" << i << "," << k + i << ")" << std::endl;
            std::vector<std::pair<int, int>> subsequence;
            for (int j = i; j <= i + k; ++j) {
                subsequence.push_back({j, w[j]});
            }

            std::sort(subsequence.begin(), subsequence.end(),
                      [](const std::pair<int, int> &a, const std::pair<int, int> &b) {
                          if (a.second != b.second) {
                              return a.second < b.second;
                          } else {
                              return a.first < b.first;
                          }
                      });

            std::string patternString = generatePatternString(subsequence, i);


            uint64_t hashValue  = karp_rabin_hashing::hash_string(patternString.c_str(),patternString.size());

//            cout<<"k = "<<k <<"; hashvalue: "<<hashValue<<endl;
            H[k % 2][i] = hashValue;

            int x = ++HT[k % 2][H[k % 2][i]];


            if (x >= tau) {
//                std::cout<<"Killed"<<std::endl;
                flag = true;

            }


            if (HT[(k-1)%2][H[(k-1)%2][i]] == HT[k%2][H[k%2][i]]) {



                HT[(k-1)%2][H[(k-1)%2][i]] =0;

            }



            if (HT[(k-1)%2][H[(k-1)%2][i+1]] == HT[k%2][H[k%2][i]]){


                HT[(k-1)%2][H[(k-1)%2][i+1]] =0;

            }



        }




        for (auto it :HT[(k - 1) % 2]) {
            if (it.second >= tau) {
//                cout<<it.first<<" pattern happened "<< it.second<<"times"<<endl;
                cnt_closed ++;

            }

        }


        HT[(k - 1) % 2].clear();


        if (!flag){
//            cout<<"break"<<endl;
            cout<<"The max length of patterns: "<<k<<endl;

            break;
        }
    }
    return cnt_closed;
}


int quadraticMethodClosed(std::vector<int> &w, int &tau){
    karp_rabin_hashing::init();


    int cnt_closed = 0;
    int n = w.size();

    std::vector<std::vector<uint64_t>> H(2, std::vector<uint64_t>(n, 0));

    std::vector<std::unordered_map<uint64_t, int>> HT(2);

    std::set<std::pair<int, int>> S;

    for(int i = 0; i < n; ++i) {
        H[0][i] = 0;
    }
    HT[0][0] = n;
    uint64_t odd_hashValue = 2*n;

    bool flag;

    for(int k = 1; k < n; ++k) {
        flag = false;

        //initialization of Set S
        S.clear();
        for (int j = 0; j < k; ++j) {
            S.insert({w[j], j});
        }

        for (int i = 0; i < n - k; ++i) {

            std::pair<std::set<pair<int, int>>::iterator, bool> current = S.insert({w[i+k] , i+k});

            auto it = current.first;
            if (it != S.begin()) { // make it is not the first element
                --it; // the iterator points to the element before current

                // the position of the element before current
                //whether its first coordinate is equal to w[i+k].
                uint64_t appendix = 2*(it->second - i) + (int)(it->first == w[i+k]);

                H[k % 2][i] = karp_rabin_hashing::concat(H[(k - 1) % 2][i], appendix, 1);


            } else {


                H[k % 2][i] = karp_rabin_hashing::concat(H[(k - 1) % 2][i], odd_hashValue, 1);

            }

            int x = ++HT[k % 2][H[k % 2][i]];

            if (x >= tau) {
//                std::cout<<"Killed"<<std::endl;
                flag = true;

            }


            if (HT[(k-1)%2][H[(k-1)%2][i]] == HT[k%2][H[k%2][i]]) {

//                std::cout<<"Killed"<<std::endl;

                HT[(k-1)%2][H[(k-1)%2][i]] =0;

            }



            if (HT[(k-1)%2][H[(k-1)%2][i+1]] == HT[k%2][H[k%2][i]]){

                HT[(k-1)%2][H[(k-1)%2][i+1]] =0;

            }
            // window sliding
            if (i + k + 1 < n) {
                S.erase({w[i], i});

            }

        }



        for (auto it :HT[(k - 1) % 2]) {
            if (it.second >= tau) {


//                    cout<<"times" <<it.second<<
                cnt_closed ++;
//                cout<<it.first<<" pattern happened "<< it.second<<"times"<<endl;



            }
        }






        HT[(k - 1) % 2].clear();


        if (!flag){
//            cout<<"break"<<endl;
            cout<<"The max length of patterns: "<<k<<endl;

            break;
        }
    }
    return cnt_closed;
}




