

#include <iostream>
#include <string>
#include <sdsl/wavelet_trees.hpp>
#include <fstream>


//#include "Successor.h"
//#include "Predecessor.h"
//
#include "OPST.h"
#include "baseline.h"
using namespace std;
using namespace sdsl;
#include <algorithm>
//#define terminate_label 0
//#include "cmdline.h"




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





int main(int argc, char *argv[])
{


    cmdline::parser parser;
    parser.add<string>("filepath", 'f', "the path to input file", false, "sample.txt");

    parser.add<int>("rangeThreshold", 'r', "the range of (a,b) determines call the naive or wavelet tree method", false, 512);
    parser.add<int>("tau", 't', "the value of minimal support, tau > 1", false, 2);


    parser.parse_check(argc, argv);

    string filename = parser.get<string>("filepath");
    int tau = parser.get<int>("tau");

    cout<<"--------------------------------------------Information Board--------------------------------------------------------"<<endl;

    cout<<"Enabling OPST closed method"<<endl;

    cout<< "Processing "<<filename<<endl;


    cout<<"Tau is set as "<< tau<<"."<<endl;

    // read file to input_vec
    vector<int> input_vec;
    readfile(filename, input_vec);




    int rangeThreshold = parser.get<int>("rangeThreshold");

    // OPST construction
    auto Construction_start = std::chrono::high_resolution_clock::now();

    OPST OP(input_vec, rangeThreshold);

    auto Construction_end = std::chrono::high_resolution_clock::now();
    double time_Construction = std::chrono::duration_cast < std::chrono::microseconds > (Construction_end - Construction_start).count()*0.000001;


    //Closed patterns mining
    std::unordered_map<stNode*, int> ClosedTauNodes;

    auto Closed_start = std::chrono::high_resolution_clock::now();

    OP.ClosedTauDFS(tau);
    auto Closed_start1 = std::chrono::high_resolution_clock::now();

    OP.ClosedFindNodes(ClosedTauNodes);


    auto Closed_end = std::chrono::high_resolution_clock::now();
    double time_Closed1 = std::chrono::duration_cast < std::chrono::microseconds > (Closed_start1 - Closed_start).count()*0.000001;

    double time_Closed = std::chrono::duration_cast < std::chrono::microseconds > (Closed_end - Closed_start).count()*0.000001;

//    ofstream output(filename+"_ClosedPattern_"+ to_string(tau));
//    for (auto &i: ClosedTauNodes){
//        vector<int> PreCodeint;
//        stNode * node = i.first;
//        while (1){
//
//            if (node == OP.root){
//                break;
//            }
//
//            PreCodeint.push_back(node->label);
//            node = node->parent;
//
//        }
//        if (PreCodeint.size()<200){
//
//            output<< node->start<<":";
//
//            reverse(PreCodeint.begin(),PreCodeint.end());
//            for (int j=0; j<PreCodeint.size();j++){
//                if (j == PreCodeint.size()-1){
//                    output<<PreCodeint[j]<<":";
//                    output<< i.second;
//
//                } else
//                {
//                    output<<PreCodeint[j]<<",";
//
//                }
//
//            }
//
//            output<<"\n";
//
//
//        }
//
//        PreCodeint.clear();
//    }
//
//
//







    cout<<"The input size: "<<OP.n<<endl;

    cout<<"Terminate_label (2 * n + 1) $ = " << OP.terminate_label<<endl;

    cout<<"Runtime only for OPST construction  = "<<time_Construction<<" s."<<endl;
 

    cout<<"Runtime only used for mining closed order-preserving "<<tau<<"-frequent patterns: "<<time_Closed<<" s."<<endl;
    cout<<"The number of found closed patterns is "<<ClosedTauNodes.size()<<endl;

    cout<<"Total runtime for OPST construction and Closed patterns mining : "<<time_Construction+time_Closed<<" s."<<endl;
    int max_length_k= 0;
    for (auto i: ClosedTauNodes){
        if (max_length_k<i.first->depth){
            max_length_k = i.first->depth;
        }

//        cout<<i.first->start<<" depth:"<<i.first->depth<<endl;
    }
    cout<< "The max length of patterns:" <<max_length_k<<endl;
    cout<<"---------------------------------------------------------------------------------------------------------------------"<<endl;











    return 0;
}
