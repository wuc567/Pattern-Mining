#include <iostream>
#include <string>
#include <stack>
#include <cstring>
#include <unordered_set>

#include "OPST.h"

using namespace std;
//using namespace sdsl;
//#include <malloc.h>


//size_t memory_usage() {
//    struct mallinfo2 mi = mallinfo2();
//    return mi.uordblks;
//}

int DerivedWTInt::rank_bit( value_type c, int i, size_type offset) const{

    size_type ones_before_i   = m_tree_rank(offset + i + 1) - m_tree_rank(offset);

    if (c){
        return  ones_before_i;
    }
    else{
//        size_type zero_before_i = i + 1 - ones_before_i;

        return i + 1 - ones_before_i;
    }
}


int DerivedWTInt::select_bit(value_type c, int i, const node_type& node) const{

    size_type offset = node.offset;
    size_type node_size = node.size;

    size_type ones_before_o   = m_tree_rank(offset);
    size_type ones_in_node = m_tree_rank(offset + node_size) - ones_before_o;


    if (0ULL == node_size or node_size < i) {
        throw std::logic_error("select("+util::to_string(c)+","+util::to_string(i)+"): "+util::to_string(c)+" does not occur "+ util::to_string(i) +" times in the bit vector of this node");
    }

    if (c){
        // detect error
        if (ones_in_node < i) {
            throw std::logic_error("select("+util::to_string(c)+","+util::to_string(i)+"): "+util::to_string(c)+" does not occur "+ util::to_string(i) +" times in the bit vector of this node");
        }

        return  m_tree_select1(ones_before_o + i) - offset;
    }
    else{
        if (node_size - ones_in_node< i) {
            // detect error
            throw std::logic_error("select("+util::to_string(c)+","+util::to_string(i)+"): "+util::to_string(c)+" does not occur "+ util::to_string(i) +" times in the bit vector of this node");
        }
        return m_tree_select0(offset - ones_before_o + i) - offset ;
    }
}




int OPST::Max(const sdsl::wt_int<>::node_type& u, int a, int b) {

    if (wt.is_leaf(u)){

        return b;
    }else if (wt.rank_bit(1, a, u.offset) == wt.rank_bit(1, b, u.offset)) {
#ifdef VERBOSE
        cout<<"Max: a: "<<(int )wt.rank_bit(0, a, u.offset)<<endl;
        cout<<"Max: b: "<<(int )wt.rank_bit(0, b, u.offset)<<endl;
        cout<<"Max: "<< Max(wt.expand(u)[0], wt.rank_bit(0, a, u.offset) - 1, wt.rank_bit(0, b, u.offset) - 1)<<endl;

#endif

        return wt.select_bit(0, Max( wt.expand(u)[0], wt.rank_bit(0, a, u.offset) - 1, wt.rank_bit(0, b, u.offset) - 1) + 1, u);
    } else {
#ifdef VERBOSE

        cout<<"Max: a: "<<(int )wt.rank_bit(1, a, u.offset)<<endl;
        cout<<"Max: b: "<<(int )wt.rank_bit(1, b, u.offset)<<endl;
        cout<<"Max: "<< Max(wt.expand(u)[1], wt.rank_bit(1, a, u.offset) - 1, wt.rank_bit(1, b, u.offset) - 1)<<endl;

#endif

        return wt.select_bit(1, Max(wt.expand(u)[1], wt.rank_bit(1, a, u.offset) - 1, wt.rank_bit(1, b, u.offset) - 1) + 1, u);
    }
}





int OPST::predecessorWT(const sdsl::wt_int<>::node_type& u, int a, int b) {


    if (a == b) return NA; // predecessor does not exist

    if (!wt.is_leaf(u)) {
        auto B_u = wt.bit_vec(u); // get the bit vector of u

        auto x = B_u[b + 1];

        int pos = predecessorWT(wt.expand(u)[x], wt.rank_bit(x, a, u.offset)-1, wt.rank_bit(x, b, u.offset)-1);// For counting 1s.


        if (pos != NA) {

            return wt.select_bit(x, pos + 1, u);
        } else if (x == 0 || wt.rank_bit(0, a, u.offset) == wt.rank_bit(0, b, u.offset)) {

            return NA;
        } else {

            return wt.select_bit(0, Max( wt.expand(u)[0], wt.rank_bit(0, a, u.offset)-1, wt.rank_bit(0, b, u.offset) - 1) + 1, u);
        }
    } else {
        return b;
    }
}


int OPST::predecessorNV(int a, int b) {
    if (w.empty()) return -1; // Handle empty vector case


    int aimElement = w[b];
    int predecessorIndex = NA; // Default to "not found"
    // Find the rightmost occurrence of the smallest element greater than or equal to the aimelement
    if (b < 0){
        return predecessorIndex;
    }
    if (a < 0){
        for (int j = 0; j < b ; ++j) {
            if (w[j] <= aimElement) {
                if (predecessorIndex == NA || w[j] >= w[predecessorIndex]) {
                    predecessorIndex = j;
                }
            }
        }

    } else{

        for (int j = a; j < b ; ++j) {
            if (w[j] <= aimElement) {
                if (predecessorIndex == NA || w[j] >= w[predecessorIndex]) {
                    predecessorIndex = j;
                }
            }
        }

    }

    return predecessorIndex;
}







pair<int, int> OPST:: LastCode(int a , int b){



    if ( b -a < rangeThreshold) {


        int predecessor_local = predecessorNV(a, b);


        int successor_local;

        //if predecessor_local is -1, successor is set to notEqual(0)
        if(predecessor_local<0){
            successor_local = 0;
        } else{

            successor_local = (int) (w[predecessor_local] == w[b]);

        }

        if (predecessor_local != NA) {
            predecessor_local = predecessor_local - a;
        }


        return make_pair(predecessor_local, successor_local);

    } else{

        // construct wavelet tree for LastCodeInt only when necessarily

        if (!waveletFlag){
            auto wavelet_start = std::chrono::high_resolution_clock::now();
            int_vector<> uint64_vec;
            uint64_vec.resize(w.size());
            for(size_t i = 0; i < w.size(); ++i) {
                uint64_vec[i] = (uint64_t)w[i];
            }
            construct_im(wt,uint64_vec);
            auto wavelet_end = std::chrono::high_resolution_clock::now();

            this->waveletTime = std::chrono::duration_cast < std::chrono::milliseconds > (wavelet_end - wavelet_start).count()*0.001;
            waveletFlag = true;
            cout<<"It is necessary to construct the wavelet tree for b-a > "<< rangeThreshold<<endl;
            cout<<"sigma of input = "<<wt.sigma<<endl;
            cout<< "Runtime for wavelet tree construction  = "<<waveletTime<<" s."<<endl;
        }


        int predecessor_local = predecessorWT(wt.root(), a-1, b-1);

        int successor_local;

        //if predecessor_local is -1, successor is set to notEqual(0)

        if(predecessor_local<0){
            successor_local = 0;
        } else{

            successor_local = (int) (w[predecessor_local] == w[b]);

        }

        if (predecessor_local != NA){
            predecessor_local = predecessor_local - a;
        }

        return make_pair(predecessor_local,successor_local);

    }

}



int OPST::LastCodeInt(int a, int b) {
    // call LastCode
    // b = n, returns terminate_label: 2 * n + 1
    if (b != n){
        pair<int, int> ab = this->LastCode(a, b);
        return (ab.first * 2 + ab.second);

    } else{
        return terminate_label;

    }

}




OPST::OPST(vector<int> & w, int &rangeThreshold)
{
//    size_t memory_start = memory_usage()*0.001;

    this->w = w;
    this->n = w.size();


    //set the value of terminate_label
    terminate_label = 2 * this->n + 1;
    waveletFlag = false;

    this->rangeThreshold = rangeThreshold;


    this->root = new stNode(terminate_label);
    this->root->setSLink( this->root );



    stNode * u = this->root;
    int d = 0;


    for ( int i = 0; i < this->n; i++ )
    {
        while (((i+d) < this -> n) && (d == u->depth) && (u->getChild(LastCodeInt(i, i + d)) != NULL)) {


            u = u->getChild(LastCodeInt(i, i + d));
            d = d + 1;
            while ((i + d < this->n) && (u->start +d < this->n) && (d < u->depth) && (LastCode(u->start, u->start + d) == LastCode(i , i + d))) {
                d = d + 1;
            }
        }

        if ( d < u->depth)
        {
            u= createNode (u, d );
        }
        createLeaf( i, u, d);

        if ( u->slink == NULL )
        {
            ComputeSuffixLink( u );
        }
        u = u->slink;

//        d = u->getDepth(); // same as d = max( d-1, 0 );
        d = max( d-1, 0 );


    }
    //the only child of root



//    memory = memory_usage()*0.001 - memory_start;

}



void OPST::ComputeSuffixLink( stNode * u )
{
    int d = u->depth;
    stNode * u_copy = u;

    //count the num of implicit node between two branching nodes
    while (!u_copy->parent->slink){
        u_copy = u_copy->parent;
//        explicit_k ++;

        // count the explicit nodes we traverse
    }

    stNode * v = u_copy->parent->slink;

    while ( v->depth < d-1 )
    {


        // go down
        v = v->getChild( LastCodeInt(u->start+1, u->start + v->depth + 1) );

//        explicit_k ++;
        // count the explicit nodes we traverse
    }
    if ( v->depth > d-1 )
    {
        //create a new node as a suffix link node
        v = createNode( v, d-1);
    }
    u->setSLink (v);
//    u-> slink->setDepth(d -1);
}

stNode * OPST::createNode(stNode * u, int d )
{

    // add a new node v between p and u
    int i = u->start;
    stNode * p = u->parent;


    // get the label of u and v
    int v_label = LastCodeInt(i, i+p->depth);
    int u_label = LastCodeInt(i, i+d);

    stNode * v = new stNode( i, d, v_label);
    v->addChild( u, u_label);
    p->addChild( v, v_label);

    return v;
}


void OPST::createLeaf( int i, stNode * u, int d )
{
    // create a leaf node connected to u
    // (n+2)(n+1)+1 represents $

    int leaf_label = LastCodeInt( i, i+d);
    int depth = this->n-i +1;
    stNode *leaf  = new stNode(i, depth, leaf_label) ;
    u->addChild( leaf, leaf_label);
    pos2leaf.insert({i, leaf});


}





void OPST::MaxTauDFS(int tau) {
    std::stack<stNode *> stack;
    stack.push(root);

    int tauminus1= tau - 1; //for saving time

    while (!stack.empty()) {
        stNode *top = stack.top();

        if (!top->visited) {
            // First visit to a node: add all its child nodes to the stack
            top->visited = true;
            for (auto &it: top->child) {
                stack.push(it.second);
            }
        } else {
            // Second visit to the node: The leafCount of all child nodes has been calculated. Now calculate the leafCount of the current node.
            stack.pop();

            if (top->child.empty()) {
                // if it is leaf
                top->leafCount = 1;
            } else {
                //Otherwise, accumulate leafCount of all child nodes
                if (top->child.size() > 1) {
                    bool childrenGetau = false; // if one of top's children is candidate, top can not be candidate
                    for (auto &it: top->child) {
                        top->leafCount += it.second->leafCount;
                        childrenGetau = childrenGetau || (it.second->leafCount > tauminus1);
                    }
                    if (top->leafCount > tauminus1 && !childrenGetau) { // it satisfies condition 1 and 2 at the same time
                        top->isCandidate = true;
                    }

                } else { // the size of children =1 indicating it is implicit node, let its leafCount = leafCount of first child


                    top->leafCount = top->child.begin()->second->leafCount;

                }



                if (top->isCandidate && top->slink!= NULL) {
                    stNode *ancestor = top->slink;

                    // Propagate the leftMax upward
                    while ((ancestor != nullptr) && (ancestor->leftMax)) {
                        if (ancestor->leftMax){
                            ancestor->leftMax = false;  // kill the node which has incoming suffix link
                            ancestor = ancestor->parent;
                        }
                    }
                }

            }
            top->visited = false; // After second visiting, reset visited status to default for future use

        }
    }
}






void OPST::MaxFindNodes(std::unordered_map<stNode*, int> &MaxTauNodes){
    std::stack<stNode*> stack;
    stack.push(root);
    while (!stack.empty()) {
        stNode* top = stack.top();

        if (!top->visited) {
            top->visited = true; // Mark as visited
            // Push the current node onto the stack again so that it can be accessed again after all child nodes have been processed
            for (auto &it: top->child) {
                stack.push(it.second);
            }
        } else {
            //When all child nodes have been processed, check whether the current node meets the conditions

            if (top->isCandidate && top->leftMax) {
                MaxTauNodes.insert({top,top->leafCount}); // Add to result vector

            }
            top->visited = false; // After second visiting, reset visited status to default for future use
            top->isCandidate = false; //reset
            top->leftMax = true; //reset
            top->leafCount =0; //reset
            stack.pop();

        }

    }
}




stNode* OPST::FindLCA(stNode* node){

    stNode* u = node->child.begin()->second->LCA;
    // start from the second child
    for (auto it = std::next(node->child.begin()); it != node->child.end(); it++ ) {
        stNode* v = it->second->LCA;
        if(u->parent==root && root->child.size() ==1){
            break;
        }
        while(u != v){
            if(u->depth < v->depth){
                v = v->parent;
            } else{
                u = u->parent;
            }
        }

    }
    return u;

}






void OPST::ClosedTauDFS(int tau) {

    std::stack<stNode *> stack;
    stack.push(root);

    // set the LCA stored in the leaves
    for (auto &i: pos2leaf){
        if (i.first!=0){
            i.second->LCA = pos2leaf[i.first -1];
        } else{
            i.second->LCA = root->allChild()[0];
        }
    }


    int tauminus1 = tau - 1; //for saving time
    while (!stack.empty()) {
        stNode *top = stack.top();

        if (!top->visited) {
            // First visit to a node: add all its child nodes to the stack
            top->visited = true;
            for (auto &it: top->child) {
                stack.push(it.second);
            }


        } else {
            // Second visit to the node: The leafCount of all child nodes has been calculated. Now calculate the leafCount of the current node.
            stack.pop();

            if (top->child.empty()) {
                // if it is leaf
                top->leafCount = 1;
                //if the leaf does not start from position 0


            } else {
                //Otherwise, accumulate leafCount of all child nodes
                if (top->child.size() > 1) {
//                    cout<<"2"<<endl;

                    for (auto &it: top->child) {
                        top->leafCount += it.second->leafCount;
                    }

                    if (top->leafCount > tauminus1 ) { // it satisfies tau frequent and right-closed
                        top->isCandidate = true;
                    }

//                    top->LCA_depth = top->child.begin()->second->LCA_depth;
                    top->LCA = FindLCA(top);


                } else {
//                    cout<<"3"<<endl;

                    // the size of children =1 indicating it is implicit node, let its leafCount = leafCount of first child; LCA depth is LCA depth of first child

                    top->leafCount = top->child.begin()->second->leafCount;
                    top->LCA = top->child.begin()->second->LCA;

//                    top->LCA_depth = top->child.begin()->second->LCA_depth;

                }


                if(top->LCA->depth < top->depth +1){
                    top->leftDiverse = true;
                }

            }
            top->visited = false; // After second visiting, reset visited status to default for future use
        }

    }
}




void OPST::ClosedFindNodes(std::unordered_map<stNode*, int> &ClosedTauNodes){
    std::stack<stNode*> stack;
    stack.push(root);
    while (!stack.empty()) {
        stNode* top = stack.top();

        if (!top->visited) {
            top->visited = true; // Mark as visited
            // Push the current node onto the stack again so that it can be accessed again after all child nodes have been processed
            for (auto &it: top->child) {
                stack.push(it.second);
            }
        } else {
            //When all child nodes have been processed, check whether the current node meets the conditions

            if (top->isCandidate && top->leftDiverse) {
//                ClosedTauNodes.push_back(top); // Add to result vector
                ClosedTauNodes.insert({top,top->leafCount}); // Add to result vector

            }
            top->visited = false; // After second visiting, reset visited status to default for future use
            top->isCandidate = false; //reset
            top->leftDiverse = false; //reset
            top->leafCount =0; //reset
            stack.pop();
        }

    }
}






void OPST::deleteTreeIteratively() {
    std::stack<stNode*> toDelete;
    toDelete.push(root);

    while (!toDelete.empty()) {
        stNode* current = toDelete.top();
        toDelete.pop();

        for (auto it = current->child.begin(); it != current->child.end();) {
            if (it->second != nullptr){
                toDelete.push(it->second);
                it->second = nullptr;

            }
            it = current->child.erase(it);
        }
        delete current;

    }
}

OPST::~OPST() {

//    delete this->root;
    deleteTreeIteratively();
}

