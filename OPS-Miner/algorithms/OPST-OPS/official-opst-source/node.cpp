//
// Created by ling on 12/03/24.
//
#include <iostream>
#include <string>
#include <unordered_map>
#include "node.h"

using namespace std;


stNode::stNode()
{
    this->start = 0;
    this->depth = 0;
    this->label = 0;
    this->parent = NULL;
    this->slink = NULL;

    this->visited = false;
    this->isCandidate = false;
    this->leftMax = true;
    this->leafCount = 0;
    this-> leftDiverse = false;

}



stNode::stNode(int terminate_label)
{
    this->start = 0;
    this->depth = 0;
    this->label = terminate_label;
    this->parent = NULL;

    this->slink = NULL;
    this->visited = false;
    this->isCandidate = false;
    this->leftMax = true;
    this->leafCount = 0;
    this-> leftDiverse = false;



}

stNode::stNode( int i, int d, int l)
{
    this->start = i;
    this->depth = d;
    this->label = l;
    this->parent = NULL;

    this->slink = NULL;
    this->visited = false;
    this->isCandidate = false;
    this->leftMax = true;
    this->leafCount = 0;
    this-> leftDiverse = false;



}


void stNode::setDepth( int d){

    this->depth = d;
}



stNode * stNode::getChild( int l )
{

    unordered_map<int, stNode*>::iterator it;



    it = this->child.find(l);
    if ( it == this->child.end() )
        return NULL;
    else
        return it->second;
}


void stNode::setSLink( stNode * slinkNode )
{
    this->slink = slinkNode;
}

void stNode::addChild( stNode * childNode, int l)
{
    auto it = this->child.find( l );
    if ( it == this->child.end() )
    {
        pair <int, stNode*> insertChild( l, childNode );
        this->child.insert( insertChild);
    }
    else
    {
        it->second = childNode;
    }
    childNode->label = l;
    childNode->parent = this;
}

void stNode::setParent( stNode * parentNode )
{
    this->parent = parentNode;
}


int stNode::numChild()
{
    if (this->child.empty()){
        return 0;
    }
    return this->child.size();
}




std::vector<stNode*> stNode::allChild() {
    std::vector<stNode*> allChildren;
    for (auto& pair : this->child) {
        allChildren.push_back(pair.second);
    }
    return allChildren;
}



stNode::~stNode()
{

/*
// recursion
    // Delete all child nodes
    for (auto it = this->child.begin(); it != this->child.end(); )
    {

        delete it->second; // Delete child node
        it = this->child.erase(it); // Erase from map and move to next

    }

    // Check if this node is not the root (has a parent)
//    cout<<"Delete the node"<<endl;
    if (this->parent != nullptr)
    {
        // If parent's child map is empty after erasing, delete the parent; otherwise deleting this child from its parent's children map
        if (this->parent->child.empty())
        {
            delete this->parent;
        }
    }

*/

}

