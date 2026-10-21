#include "DerivedWTInt.h"


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
        throw std::logic_error("select("+sdsl::util::to_string(c)+","+sdsl::util::to_string(i)+"): "+sdsl::util::to_string(c)+" does not occur "+ sdsl::util::to_string(i) +" times in the bit vector of this node");
    }

    if (c){
        // detect error
        if (ones_in_node < i) {
            throw std::logic_error("select("+sdsl::util::to_string(c)+","+sdsl::util::to_string(i)+"): "+sdsl::util::to_string(c)+" does not occur "+ sdsl::util::to_string(i) +" times in the bit vector of this node");
        }

        return  m_tree_select1(ones_before_o + i) - offset;
    }
    else{
        if (node_size - ones_in_node< i) {
            // detect error
            throw std::logic_error("select("+sdsl::util::to_string(c)+","+sdsl::util::to_string(i)+"): "+sdsl::util::to_string(c)+" does not occur "+ sdsl::util::to_string(i) +" times in the bit vector of this node");
        }
        return m_tree_select0(offset - ones_before_o + i) - offset ;
    }
}


