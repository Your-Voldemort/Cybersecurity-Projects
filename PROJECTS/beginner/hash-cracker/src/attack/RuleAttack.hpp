// ©AngelaMos | 2026
// RuleAttack.hpp

#pragma once

#include <cstddef>
#include <expected>
#include <string>
#include <string_view>
#include <vector>
#include "src/attack/DictionaryAttack.hpp"
#include "src/core/Concepts.hpp"

class RuleAttack {
public:
    static std::expected<RuleAttack, CrackError> create(
        std::string_view path, bool chain_rules,
        unsigned thread_index, unsigned total_threads);

    std::expected<std::string, AttackComplete> next();
    std::size_t total() const;
    std::size_t progress() const;

private:
    RuleAttack(DictionaryAttack dict, bool chain_rules);

    DictionaryAttack dict_;
    bool chain_rules_;
    std::vector<std::string> mutations_;
    std::size_t mutation_index_ = 0;
    std::size_t candidates_yielded_ = 0;

    bool load_next_word();
};
