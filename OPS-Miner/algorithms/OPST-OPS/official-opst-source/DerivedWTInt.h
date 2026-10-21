#ifndef OPST_EXTENSION_DERIVEDWTINT_H
#define OPST_EXTENSION_DERIVEDWTINT_H

#include <sdsl/wavelet_trees.hpp>

class DerivedWTInt : public sdsl::wt_int<> {
public:

    using wt_int<>::wt_int;

    int rank_bit( value_type c, int i,size_type offset) const;

    int select_bit( value_type c, int i, const node_type& node) const;


};




#endif
