/**
 * @file    karp_rabin_hashing.hpp
 * @section LICENCE
 *
 * This file is part of Lazy-AVLG v0.1.0
 * See: https://github.com/dominikkempa/lz77-to-slp
 *
 * Copyright (C) 2021
 *   Dominik Kempa <dominik.kempa (at) gmail.com>
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use,
 * copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following
 * conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 * WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
 * OTHER DEALINGS IN THE SOFTWARE.
 **/

#ifndef __KARP_RABIN_HASHING_HPP_INCLUDED
#define __KARP_RABIN_HASHING_HPP_INCLUDED

#include <cstdint>


namespace karp_rabin_hashing {

//=============================================================================
// Base and exponent used in Karp-Rabin hashing.
//=============================================================================
extern std::uint64_t hash_variable;
extern std::uint64_t mersenne_prime_exponent;

std::uint64_t mul_mod_mersenne(const std::uint64_t a,
    const std::uint64_t b, const std::uint64_t k);
std::uint64_t mod_mersenne(std::uint64_t a, const std::uint64_t k);
std::uint64_t rand_mod_mersenne(const std::uint64_t k);
std::uint64_t pow_mod_mersenne(const std::uint64_t a,
    std::uint64_t n, const std::uint64_t k);
std::uint64_t concat(const std::uint64_t lhash,
    const std::uint64_t rhash, const std::uint64_t rlen);
void init();

//=============================================================================
// Compute Karp-Rabin hash of a given string.
//=============================================================================
template<typename char_type>
std::uint64_t hash_string(
    const char_type * const str,
    const std::uint64_t length) {
  std::uint64_t h = 0;
  for (std::uint64_t i = 0; i < length; ++i) {
    h = mul_mod_mersenne(h, hash_variable, mersenne_prime_exponent);
    h = mod_mersenne(h + (std::uint64_t)str[i], mersenne_prime_exponent);
  }
  return h;
}

//=============================================================================
// Return the Karp-Rabin hash of the single symbol c.
//=============================================================================
template<typename char_type>
std::uint64_t hash_char(const char_type c) {
  return mod_mersenne((std::uint64_t)c, mersenne_prime_exponent);
}

}  // namespace karp_rabin_hashing

#endif  // __KARP_RABIN_HASHING_HPP_INCLUDED
