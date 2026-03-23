// ©AngelaMos | 2026
// RuleSet.cpp

#include "src/rules/RuleSet.hpp"
#include "src/config/Config.hpp"
#include <algorithm>
#include <array>
#include <cctype>
#include <ranges>
#include <utility>

static constexpr std::array<std::pair<char, char>, 6> LEET_MAP = {{
    {'a', '@'}, {'e', '3'}, {'i', '1'},
    {'o', '0'}, {'s', '$'}, {'t', '7'}
}};

std::generator<std::string> RuleSet::capitalize_first(std::string_view word) {
    if (word.empty()) { co_return; }
    std::string result(word);
    result[0] = static_cast<char>(std::toupper(static_cast<unsigned char>(result[0])));
    co_yield std::move(result);
}

std::generator<std::string> RuleSet::uppercase_all(std::string_view word) {
    std::string result(word);
    std::ranges::transform(result, result.begin(), [](unsigned char c) {
        return static_cast<char>(std::toupper(c));
    });
    co_yield std::move(result);
}

std::generator<std::string> RuleSet::leet_speak(std::string_view word) {
    std::string result(word);
    for (auto& c : result) {
        auto lower = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        for (auto [from, to] : LEET_MAP) {
            if (lower == from) { c = to; break; }
        }
    }
    co_yield std::move(result);
}

std::generator<std::string> RuleSet::append_digits(std::string_view word) {
    std::string base(word);
    for (std::size_t i = 0; i <= config::MAX_APPEND_DIGIT; ++i) {
        co_yield base + std::to_string(i);
    }
}

std::generator<std::string> RuleSet::prepend_digits(std::string_view word) {
    std::string base(word);
    for (std::size_t i = 0; i <= config::MAX_PREPEND_DIGIT; ++i) {
        co_yield std::to_string(i) + base;
    }
}

std::generator<std::string> RuleSet::reverse(std::string_view word) {
    std::string result(word.rbegin(), word.rend());
    co_yield std::move(result);
}

std::generator<std::string> RuleSet::toggle_case(std::string_view word) {
    std::string result(word);
    std::ranges::transform(result, result.begin(), [](unsigned char c) {
        if (std::islower(c)) { return static_cast<char>(std::toupper(c)); }
        return static_cast<char>(std::tolower(c));
    });
    co_yield std::move(result);
}

std::generator<std::string> RuleSet::apply_all(std::string_view word) {
    co_yield std::ranges::elements_of(capitalize_first(word));
    co_yield std::ranges::elements_of(uppercase_all(word));
    co_yield std::ranges::elements_of(leet_speak(word));
    co_yield std::ranges::elements_of(append_digits(word));
    co_yield std::ranges::elements_of(prepend_digits(word));
    co_yield std::ranges::elements_of(reverse(word));
    co_yield std::ranges::elements_of(toggle_case(word));
}
