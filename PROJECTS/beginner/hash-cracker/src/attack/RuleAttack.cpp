// ©AngelaMos | 2026
// RuleAttack.cpp

#include "src/attack/RuleAttack.hpp"
#include "src/rules/RuleSet.hpp"

RuleAttack::RuleAttack(DictionaryAttack dict, bool chain_rules)
    : dict_(std::move(dict)), chain_rules_(chain_rules) {}

std::expected<RuleAttack, CrackError> RuleAttack::create(
    std::string_view path, bool chain_rules,
    unsigned thread_index, unsigned total_threads) {
    auto dict = DictionaryAttack::create(path, thread_index, total_threads);
    if (!dict.has_value()) {
        return std::unexpected(dict.error());
    }
    return RuleAttack(std::move(*dict), chain_rules);
}

bool RuleAttack::load_next_word() {
    auto word = dict_.next();
    if (!word.has_value()) {
        return false;
    }

    mutations_.clear();
    mutations_.push_back(*word);

    for (auto&& m : RuleSet::apply_all(*word)) {
        mutations_.push_back(std::move(m));
    }

    if (chain_rules_) {
        std::vector<std::string> base(mutations_.begin() + 1, mutations_.end());
        for (const auto& b : base) {
            for (auto&& m : RuleSet::apply_all(b)) {
                mutations_.push_back(std::move(m));
            }
        }
    }

    mutation_index_ = 0;
    return true;
}

std::expected<std::string, AttackComplete> RuleAttack::next() {
    while (mutation_index_ >= mutations_.size()) {
        if (!load_next_word()) {
            return std::unexpected(AttackComplete{});
        }
    }

    ++candidates_yielded_;
    return std::move(mutations_[mutation_index_++]);
}

std::size_t RuleAttack::total() const { return dict_.total(); }
std::size_t RuleAttack::progress() const { return candidates_yielded_; }
