#include <iostream>
#include <string>
#include <sdsl/wavelet_trees.hpp>
#include <fstream>


//#include "Successor.h"
//#include "Predecessor.h"
//
#include "OPST.h"
//#include "baseline.h"
using namespace std;
using namespace sdsl;

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
    parser.add<bool>("printPattern", 'p', "Print out the pattern or not", false, false);
    parser.parse_check(argc, argv);

    string filename = parser.get<string>("filepath");

    cout<<"--------------------------------------------Information Board--------------------------------------------------------"<<endl;
    cout<<"Enabling OPST construction"<<endl;

    cout<< "Processing "<<filename<<endl;

    // read file to input_vec
    vector<int> input_vec;
    readfile(filename, input_vec);

//    cout<<"Memory outside2: "<<memory_usage()*0.001<<endl;

//    size_t memory;
    int rangeThreshold = parser.get<int>("rangeThreshold");

    // OPST construction
    auto Construction_start = std::chrono::high_resolution_clock::now();

    OPST OP(input_vec, rangeThreshold);

    auto Construction_end = std::chrono::high_resolution_clock::now();
    double time_Construction = std::chrono::duration_cast < std::chrono::microseconds > (Construction_end - Construction_start).count()*0.000001;

//    cout<<"Memory outside3: "<<memory_usage()*0.001<<endl;
//    cout<<"Memory difference: "<<memory_usage()*0.001<<endl;

    cout<<"The input size: "<<OP.n<<endl;

    cout<<"Terminate_label (2 * n + 1) $ = " << OP.terminate_label<<endl;

    cout<<"Runtime only for OPST construction  = "<<time_Construction<<" s."<<endl;

    cout<<"---------------------------------------------------------------------------------------------------------------------"<<endl;






    return 0;
}
