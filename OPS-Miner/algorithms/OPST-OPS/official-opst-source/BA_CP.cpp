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

    cout<<"Enabling O(n^2*log(n)) baseline - Closed patterns mining: "<<endl;

    cout<< "Processing "<<filename<<endl;
    cout<<"Tau is set as "<< tau<<"."<<endl;

    // read file to input_vec
    vector<int> input_vec;
    readfile(filename, input_vec);



    auto quadratic_start = std::chrono::high_resolution_clock::now();

    int numQuadratic= quadraticMethodClosed(input_vec,tau);
    auto quadratic_end = std::chrono::high_resolution_clock::now();
    double time_quadratic = std::chrono::duration_cast < std::chrono::microseconds > (quadratic_end - quadratic_start).count() * 0.000001;
    cout<<"The input size: "<<input_vec.size()<<endl;

    cout<<"Runtime used for mining closed order-preserving "<<tau<<"-frequent patterns: "<<time_quadratic<<" s."<<endl;
    cout<<"The number of found closed patterns is "<<numQuadratic<<endl;
    cout<<"---------------------------------------------------------------------------------------------------------------------"<<endl;


    return 0;
}
