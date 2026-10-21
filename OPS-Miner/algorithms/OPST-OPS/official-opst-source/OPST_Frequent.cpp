#include <chrono>
#include <fstream>
#include <iostream>
#include <stack>
#include <string>
#include <vector>

#include "OPST.h"

using namespace std;

static void readfile(const string &filename, vector<int> &values) {
    ifstream input(filename);
    if (!input) {
        throw runtime_error("Unable to open file: " + filename);
    }
    int value;
    while (input >> value) {
        values.push_back(value);
    }
}

// Every locus on a compressed OPST edge represents one distinct OPP.  All
// loci on an edge have the same occurrence count as the edge's child node.
// OPS/WOPP start at pattern length two, so the length-one locus is excluded.
static long long count_frequent_opps(OPST &tree, int tau) {
    tree.MaxTauDFS(tau);  // computes exact leafCount (support) for every node
    long long count = 0;
    stack<stNode *> pending;
    pending.push(tree.root);
    while (!pending.empty()) {
        stNode *node = pending.top();
        pending.pop();
        for (const auto &entry : node->child) {
            stNode *child = entry.second;
            if (child->leafCount >= tau) {
                const int first_depth = max(node->depth + 1, 2);
                if (child->depth >= first_depth) {
                    count += static_cast<long long>(child->depth - first_depth + 1);
                }
            }
            pending.push(child);
        }
    }
    return count;
}

int main(int argc, char *argv[]) {
    cmdline::parser parser;
    parser.add<string>("filepath", 'f', "input file", true);
    parser.add<int>("rangeThreshold", 'r', "naive/wavelet threshold", false, 512);
    parser.add<int>("tau", 't', "minimum support", true);
    parser.parse_check(argc, argv);

    vector<int> values;
    readfile(parser.get<string>("filepath"), values);
    int range_threshold = parser.get<int>("rangeThreshold");
    int tau = parser.get<int>("tau");

    const auto construction_start = chrono::high_resolution_clock::now();
    OPST tree(values, range_threshold);
    const auto construction_end = chrono::high_resolution_clock::now();

    const auto mining_start = chrono::high_resolution_clock::now();
    const long long frequent_count = count_frequent_opps(tree, tau);
    const auto mining_end = chrono::high_resolution_clock::now();

    const double construction_seconds = chrono::duration_cast<chrono::microseconds>(
        construction_end - construction_start).count() * 0.000001;
    const double mining_seconds = chrono::duration_cast<chrono::microseconds>(
        mining_end - mining_start).count() * 0.000001;

    cout << "Runtime only for OPST construction  = " << construction_seconds << " s.\n";
    cout << "Runtime only used for mining all frequent OPPs: " << mining_seconds << " s.\n";
    cout << "The number of found frequent patterns is " << frequent_count << "\n";
    cout << "Total runtime for OPST construction and frequent patterns mining : "
         << construction_seconds + mining_seconds << " s.\n";
    return 0;
}
