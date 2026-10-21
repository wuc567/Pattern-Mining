//
// Created by ling on 12/03/24.
//

#ifndef NODE_H
#define NODE_H


#include <string>
#include <unordered_map>
#include <vector>
#include <iostream>
using namespace std;
//#define UNORDERED_DENSE

class stNode
{
public:
    int start;
    int depth;
    int label; // label is the label of edge which links its parent and itself


    stNode * parent;
    stNode * slink;

    stNode();
    explicit stNode(int terminate_label);
    stNode( int i, int d, int l );

    void setDepth( int d);


//DFS
    bool isCandidate;
    bool leftMax;
    bool visited;
    int leafCount;
    bool leftDiverse;
    stNode* LCA;





    unordered_map<int, stNode*> child;


    stNode * getChild( int l );

    void setSLink( stNode * slinkNode );
    void addChild( stNode * childNode,  int l );

    void setParent ( stNode * parentNode );
    int numChild();

    std::vector<stNode*> allChild();


    ~stNode();
};

#endif


