// ©AngelaMos | 2026
// BruteForceAttack.cpp

#include "src/attack/BruteForceAttack.hpp"
#include <algorithm>

std::size_t BruteForceAttack::compute_keyspace(std::size_t charset_size,
                                               std::size_t max_length) {
    std::size_t total = 0;
    std::size_t power = 1;
    for (std::size_t len = 1; len <= max_length; ++len) {
        power *= charset_size;
        total += power;
    }
    return total;
}

BruteForceAttack::BruteForceAttack(std::string_view charset,
                                   std::size_t max_length,
                                   unsigned thread_index,
                                   unsigned total_threads)
    : charset_(charset), max_length_(max_length),
      total_keyspace_(compute_keyspace(charset.size(), max_length)) {
    std::size_t per_thread = total_keyspace_ / total_threads;
    std::size_t remainder = total_keyspace_ % total_threads;

    start_index_ = thread_index * per_thread
        + std::min(static_cast<std::size_t>(thread_index), remainder);
    std::size_t my_count = per_thread + (thread_index < remainder ? 1 : 0);
    end_index_ = start_index_ + my_count;
    current_index_ = start_index_;
}

std::string BruteForceAttack::index_to_candidate(std::size_t index) const {
    std::size_t base = charset_.size();
    std::size_t cumulative = 0;
    std::size_t power = base;

    std::size_t length = 1;
    while (cumulative + power <= index && length < max_length_) {
        cumulative += power;
        ++length;
        power *= base;
    }

    std::size_t offset = index - cumulative;
    std::string result(length, charset_[0]);

    for (std::size_t i = length; i > 0; --i) {
        result[i - 1] = charset_[offset % base];
        offset /= base;
    }

    return result;
}

std::expected<std::string, AttackComplete> BruteForceAttack::next() {
    if (current_index_ >= end_index_) {
        return std::unexpected(AttackComplete{});
    }
    return index_to_candidate(current_index_++);
}

std::size_t BruteForceAttack::total() const { return total_keyspace_; }
std::size_t BruteForceAttack::progress() const { return current_index_ - start_index_; }
