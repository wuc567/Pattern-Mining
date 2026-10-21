
#include <iostream>
#include <string>

#include <fstream>
#include "cmdline.h"


#include "baseline.h"
using namespace std;


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

    parser.add<int>("tau", 't', "the value of minimal support, tau > 1", false, 2);

    parser.parse_check(argc, argv);

    string filename = parser.get<string>("filepath");
    int tau = parser.get<int>("tau");

    cout<<"--------------------------------------------Information Board--------------------------------------------------------"<<endl;

    cout<<"Enabling O(n^2*log(n)) baseline - Maximal patterns mining: "<<endl;

    cout<< "Processing "<<filename<<endl;
    cout<<"Tau is set as "<< tau<<"."<<endl;

    // read file to input_vec
//    cout<<"Memory outside1: "<<memory_usage()*0.001<<endl;

    vector<int> input_vec;
    readfile(filename, input_vec);
//    cout<<"Memory outside2: "<<memory_usage()*0.001<<endl;


//    size_t memory =0;
    auto quadratic_start = std::chrono::high_resolution_clock::now();

    int numQuadratic= quadraticMethodMax(input_vec,tau);
    auto quadratic_end = std::chrono::high_resolution_clock::now();
    double time_quadratic = std::chrono::duration_cast < std::chrono::microseconds > (quadratic_end - quadratic_start).count() * 0.000001;
//    cout<<"Memory outside3: "<<memory_usage()*0.001<<endl;

    cout<<"The input size: "<<input_vec.size()<<endl;
    cout<<"Runtime used for mining "<<tau<<"-maximal order-preserving "<<tau<<"-frequent patterns: "<<time_quadratic<<" s."<<endl;
    cout<<"The number of found maximal patterns is "<<numQuadratic<<endl;
    cout<<"---------------------------------------------------------------------------------------------------------------------"<<endl;


    return 0;
}
