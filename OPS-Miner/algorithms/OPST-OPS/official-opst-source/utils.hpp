/**
 * @file    utils.h
 * @section LICENCE
 *
 * This file is part of Lazy-AVLG v0.1.0
 * See: https://github.com/dominikkempa/lz77-to-slp
 *
 * Copyright (C) 2012-2021
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

#ifndef __UTILS_HPP_INCLUDED
#define __UTILS_HPP_INCLUDED

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <string>
#include <mutex>
#include <sstream>


namespace utils {

    extern std::uint64_t current_ram_allocation;
    extern std::uint64_t current_io_volume;
    extern std::uint64_t current_disk_allocation;
    extern std::uint64_t peak_ram_allocation;
    extern std::uint64_t peak_disk_allocation;
    extern std::mutex io_mutex;

    long double wclock();
    void sleep(const long double);

    void *allocate(const std::uint64_t);
    void *aligned_allocate(const std::uint64_t, const std::uint64_t);
    void deallocate(const void * const);
    void aligned_deallocate(const void * const);

    void initialize_stats();
    std::uint64_t get_current_ram_allocation();
    std::uint64_t get_peak_ram_allocation();
    std::uint64_t get_current_io_volume();
    std::uint64_t get_current_disk_allocation();
    std::uint64_t get_peak_disk_allocation();

    template<typename value_type>
    value_type *allocate_array(const std::uint64_t size) {
        return (value_type *)allocate(size * sizeof(value_type));
    }

    template<typename value_type>
    value_type *aligned_allocate_array(
            const std::uint64_t size,
            const std::uint64_t align) {
        return (value_type *)aligned_allocate(size * sizeof(value_type), align);
    }

    std::FILE *file_open(const std::string, const std::string);
    std::FILE *file_open_nobuf(const std::string, const std::string);
    std::uint64_t file_size(const std::string);
    bool file_exists(const std::string);
    void file_delete(const std::string);
    std::string absolute_path(const std::string);
    void empty_page_cache(const std::string);
    std::string get_timestamp();

    template<typename value_type>
    void write_to_file(
            const value_type * const src,
            const std::uint64_t length,
            std::FILE * const f) {

#ifdef MONITOR_DISK_USAGE
        std::lock_guard<std::mutex> lk(io_mutex);
#endif

        const std::uint64_t fwrite_ret =
                std::fwrite(src, sizeof(value_type), length, f);

#ifdef MONITOR_DISK_USAGE
        current_io_volume += sizeof(value_type) * length;
  current_disk_allocation += sizeof(value_type) * length;
  peak_disk_allocation =
    std::max(peak_disk_allocation, current_disk_allocation);
#endif

        if (fwrite_ret != length) {
            fprintf(stderr, "\nError: fwrite failed.\n");
            std::exit(EXIT_FAILURE);
        }
    }

    template<typename value_type>
    void write_to_file_inplace(
            const value_type * const src,
            const std::uint64_t length,
            std::FILE * const f) {

#ifdef MONITOR_DISK_USAGE
        std::lock_guard<std::mutex> lk(io_mutex);
#endif

        const std::uint64_t fwrite_ret =
                std::fwrite(src, sizeof(value_type), length, f);

#ifdef MONITOR_DISK_USAGE
        current_io_volume += sizeof(value_type) * length;
#endif

        if (fwrite_ret != length) {
            fprintf(stderr, "\nError: fwrite failed.\n");
            std::exit(EXIT_FAILURE);
        }
    }

    template<typename value_type>
    void write_to_file(
            const value_type * const src,
            const std::uint64_t length,
            const std::string filename) {
        std::FILE * const f = file_open_nobuf(filename, "w");
        write_to_file(src, length, f);
        std::fclose(f);
    }

    template<typename value_type>
    void overwrite_at_offset(
            const value_type * const src,
            const std::uint64_t offset,
            const std::uint64_t length,
            std::FILE * const f) {
        std::fseek(f, sizeof(value_type) * offset, SEEK_SET);
        write_to_file_inplace(src, length, f);
    }

    template<typename value_type>
    void read_from_file(
            value_type * const dest,
            const std::uint64_t length,
            std::FILE * const f) {

#ifdef MONITOR_DISK_USAGE
        std::lock_guard<std::mutex> lk(io_mutex);
#endif

        const std::uint64_t fread_ret =
                std::fread(dest, sizeof(value_type), length, f);

#ifdef MONITOR_DISK_USAGE
        current_io_volume += sizeof(value_type) * length;
#endif

        if (fread_ret != length) {
            fprintf(stderr, "\nError: fread failed.\n");
            std::exit(EXIT_FAILURE);
        }
    }

    template<typename value_type>
    void read_from_file(
            value_type * const dest,
            const std::uint64_t length,
            const std::string filename) {
        std::FILE * const f = file_open_nobuf(filename, "r");
        read_from_file<value_type>(dest, length, f);
        std::fclose(f);
    }

    template<typename value_type>
    void read_from_file(
            value_type * const dest,
            const std::uint64_t max_items,
            std::uint64_t &items_read,
            std::FILE * const f) {

#ifdef MONITOR_DISK_USAGE
        std::lock_guard<std::mutex> lk(io_mutex);
#endif

        items_read = std::fread(dest, sizeof(value_type), max_items, f);

#ifdef MONITOR_DISK_USAGE
        current_io_volume += sizeof(value_type) * items_read;
#endif

        if (std::ferror(f)) {
            fprintf(stderr, "\nError: fread failed.\n");
            std::exit(EXIT_FAILURE);
        }
    }

    template<typename value_type>
    void read_at_offset(
            value_type * const dest,
            const std::uint64_t offset,
            const std::uint64_t length,
            std::FILE * const f) {
        std::fseek(f, offset, SEEK_SET);
        read_from_file(dest, length, f);
    }

    template<typename value_type>
    void read_at_offset(
            value_type * const dest,
            const std::uint64_t offset,
            const std::uint64_t length,
            const std::string filename) {
        std::FILE * const f = file_open_nobuf(filename, "r");
        read_at_offset(dest, offset, length, f);
        std::fclose(f);
    }

    template<typename int_type>
    int_type random_int(
            const int_type,
            const int_type) {
        fprintf(stderr, "\nError: random_int: unsupported type!\n");
        fprintf(stderr, "sizeof(int_type) = %lu\n",
                (std::uint64_t)sizeof(int_type));
        std::exit(EXIT_FAILURE);
    }


    template<>
    std::uint32_t random_int(const std::uint32_t, const std::uint32_t);
    template<>
    std::uint64_t random_int(const std::uint64_t, const std::uint64_t);


    void fill_random_string(std::uint8_t * const &,
                            const std::uint64_t, const std::uint64_t);
    void fill_random_letters(std::uint8_t * const &,
                             const std::uint64_t, const std::uint64_t);
    std::string random_string_hash();

    template<typename real_type = long double>
    real_type random_real() {
        const std::uint64_t mx = std::numeric_limits<std::uint64_t>::max() - 1;
        return (real_type)utils::random_int<std::uint64_t>(0, mx) / mx;
    }

    std::uint64_t log2ceil(const std::uint64_t);
    std::uint64_t log2floor(const std::uint64_t);

    template<typename int_type>
    std::string intToStr(const int_type x) {
        std::stringstream ss;
        ss << x;
        return ss.str();
    }

    template<typename int_type>
    int_type gcd(
            const int_type a,
            const int_type b) {
        if (b == (int_type)0) return a;
        else return gcd(b, a % b);
    }

    template<typename int_type>
    int_type lcm(
            const int_type a,
            const int_type b) {
        return (a / gcd(a, b)) * b;
    }

    template<typename value_type>
    std::uint64_t disk_block_size(const std::uint64_t ram_budget) {
        const std::uint64_t opt_block_size
                = lcm((std::uint64_t)BUFSIZ, (std::uint64_t)sizeof(value_type));

        std::uint64_t result = 0;
        if (ram_budget < opt_block_size) {
            result = std::max((std::uint64_t)1,
                              (std::uint64_t)(ram_budget / sizeof(value_type)));
        } else {
            const std::uint64_t opt_block_count = ram_budget / opt_block_size;
            const std::uint64_t opt_blocks_bytes = opt_block_count * opt_block_size;
            result = opt_blocks_bytes / sizeof(value_type);
        }

        return result;
    }

}  // namespace utils

#endif  // __UTILS_HPP_INCLUDED
