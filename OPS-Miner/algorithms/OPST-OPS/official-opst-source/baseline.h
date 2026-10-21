//
// Created by ling on 28/03/24.
//

#ifndef OPST_BASELINE_H
#define OPST_BASELINE_H

#include <iostream>
#include <vector>

#include <utility> // for std::pair
#include <string> // for std::string
#include <sstream> // for std::stringstream
#include <functional>

#include <sdsl/wavelet_trees.hpp>
#include <stdlib.h>
//#include <stdio.h>
#include "karp_rabin_hashing.hpp"
#include "utils.hpp"

#include <cmath>

using namespace std;
using namespace sdsl;



// Function to measure memory allocation


std::string generatePatternString(const std::vector<std::pair<int, int>>& sortedArray, int x);


int cubicMethodMax(std::vector<int> &w, int &tau);


int quadraticMethodMax(std::vector<int> &w, int &tau);


int cubicMethodClosed(std::vector<int> &w, int &tau);

int quadraticMethodClosed(std::vector<int> &w, int &tau);


long long memory_usage();











#endif
