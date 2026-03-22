// ©AngelaMos | 2026
// DictionaryAttack.hpp

#pragma once

#include <cstddef>
#include <expected>
#include <string>
#include <string_view>
#include <vector>
#include "src/core/Concepts.hpp"

class DictionaryAttack {
public:
    static std::expected<DictionaryAttack, CrackError> create(
        std::string_view path, unsigned thread_index, unsigned total_threads);

    ~DictionaryAttack();
    DictionaryAttack(DictionaryAttack&& other) noexcept;
    DictionaryAttack& operator=(DictionaryAttack&& other) noexcept;

    std::expected<std::string, AttackComplete> next();
    std::size_t total() const;
    std::size_t progress() const;

private:
    DictionaryAttack() = default;

    const char* mapped_data_ = nullptr;
    std::size_t file_size_ = 0;
    int fd_ = -1;

    std::size_t start_offset_ = 0;
    std::size_t end_offset_ = 0;
    std::size_t current_offset_ = 0;

    std::size_t total_words_ = 0;
    std::size_t words_read_ = 0;
};
