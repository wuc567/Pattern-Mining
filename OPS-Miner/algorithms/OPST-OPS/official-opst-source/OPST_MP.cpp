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
#include <filesystem>
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
std::string get_filename(const std::string& path) {

    size_t last_slash_idx = path.find_last_of("/\\");
    if (last_slash_idx == std::string::npos) {
        return path;
    }
    return path.substr(last_slash_idx + 1);
}

std::string get_grandparent_directory(const std::string& path) {

    size_t last_slash_idx = path.find_last_of("/\\");
    if (last_slash_idx == std::string::npos) {
        return ""; 
    }
    
    size_t second_last_slash_idx = path.substr(0, last_slash_idx).find_last_of("/\\");
    if (second_last_slash_idx == std::string::npos) {
        return "";  
    }
    return path.substr(0, second_last_slash_idx); 
}



int main(int argc, char *argv[])
{


    cmdline::parser parser;
    parser.add<string>("filepath", 'f', "the path to input file", false, "sample.txt");


    parser.add<int>("rangeThreshold", 'r', "the range of (a,b) determines call the naive or wavelet tree method", false, 512);
    parser.add<int>("tau", 't', "the value of minimal support, tau > 1", false, 2);


    parser.parse_check(argc, argv);

    string filename = parser.get<string>("filepath");
    string path = get_grandparent_directory(filename);
    string name = get_filename(filename);

    int tau = parser.get<int>("tau");

    cout<<"--------------------------------------------Information Board--------------------------------------------------------"<<endl;

    cout<<"Enabling OPST maximal method"<<endl;

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


    //Maximal patterns mining

//    std::vector<stNode*> MaxTauNodes;

    std::unordered_map<stNode*, int> MaxTauNodes;
    auto Maximal_start = std::chrono::high_resolution_clock::now();


    OP.MaxTauDFS(tau);
    OP.MaxFindNodes(MaxTauNodes);


    auto Maximal_end = std::chrono::high_resolution_clock::now();
    double time_Maximal = std::chrono::duration_cast < std::chrono::microseconds > (Maximal_end - Maximal_start).count()*0.000001;

//    string outputpath = parser.get<string>("output");

//    std::filesystem::create_directory(path+"/result_"+to_string(tau)+"/");
//    ofstream output(path+"/result_"+to_string(tau)+"/"+name);
//    for (auto &i: MaxTauNodes){
//        vector<int> PreCodeint;
//        stNode * node = i.first;
//        output<< node->start<<":";
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
//        reverse(PreCodeint.begin(),PreCodeint.end());
//        for (int j=0; j<PreCodeint.size();j++){
//            if (j == PreCodeint.size()-1){
//                output<<PreCodeint[j]<<":";
//                output<< i.second;
//
//            } else
//            {
//                output<<PreCodeint[j]<<",";
//
//            }
//
//        }
//
//        output<<"\n";
//        PreCodeint.clear();
//    }
//




    cout<<"The input size: "<<OP.n<<endl;

    cout<<"Terminate_label (2 * n + 1) $ = " << OP.terminate_label<<endl;

    cout<<"Runtime only for OPST construction  = "<<time_Construction<<" s."<<endl;

    cout<<"Runtime only used for mining "<<tau<<"-maximal order-preserving "<<tau<<"-frequent patterns: "<<time_Maximal<<" s."<<endl;
    cout<<"The number of found maximal patterns is "<<MaxTauNodes.size()<<endl;
    cout<<"Total runtime for OPST construction and Maximal patterns mining : "<<time_Construction+time_Maximal<<" s."<<endl;

    int max_length_k= 0;
//    set<int> ks;
    for (auto i: MaxTauNodes){
//        ks.insert(i.first->depth);
        if (max_length_k<i.first->depth){
            max_length_k = i.first->depth;
        }

//        cout<<i.first->start<<" depth:"<<i.first->depth<<endl;
//                cout<<"Pattern length: "<<i.first->depth<<endl;
//        for(auto j: i.first->LeafNodes){
//            cout<<"start from "<<j->start<<endl;
//        }
//        cout<<"------------------------------------------------------------------------"<<endl;


    }

//
//    for (auto i : ks){
//        cout<<i<<" ";
//    }
//    cout<<endl;
    cout<< "The max length of patterns:" <<max_length_k<<endl;
    cout<<"---------------------------------------------------------------------------------------------------------------------"<<endl;






    return 0;
}
