// ©AngelaMos | 2026
// test_rules.cpp

#include <gtest/gtest.h>
#include "src/attack/RuleAttack.hpp"
#include "src/rules/RuleSet.hpp"
#include <algorithm>
#include <vector>

static std::vector<std::string> collect(std::generator<std::string> gen) {
    std::vector<std::string> out;
    for (auto&& s : gen) {
        out.push_back(std::move(s));
    }
    return out;
}

TEST(RuleSetTest, CapitalizeFirst) {
    auto results = collect(RuleSet::capitalize_first("password"));
    ASSERT_EQ(results.size(), 1);
    EXPECT_EQ(results[0], "Password");
}

TEST(RuleSetTest, UppercaseAll) {
    auto results = collect(RuleSet::uppercase_all("password"));
    ASSERT_EQ(results.size(), 1);
    EXPECT_EQ(results[0], "PASSWORD");
}

TEST(RuleSetTest, LeetSpeak) {
    auto results = collect(RuleSet::leet_speak("password"));
    ASSERT_EQ(results.size(), 1);
    EXPECT_EQ(results[0], "p@$$w0rd");
}

TEST(RuleSetTest, AppendDigits) {
    auto results = collect(RuleSet::append_digits("pass"));
    EXPECT_EQ(results.size(), 1000);
    EXPECT_EQ(results[0], "pass0");
    EXPECT_EQ(results[999], "pass999");
}

TEST(RuleSetTest, PrependDigits) {
    auto results = collect(RuleSet::prepend_digits("pass"));
    EXPECT_EQ(results.size(), 1000);
    EXPECT_EQ(results[0], "0pass");
}

TEST(RuleSetTest, Reverse) {
    auto results = collect(RuleSet::reverse("password"));
    ASSERT_EQ(results.size(), 1);
    EXPECT_EQ(results[0], "drowssap");
}

TEST(RuleSetTest, ToggleCase) {
    auto results = collect(RuleSet::toggle_case("password"));
    ASSERT_EQ(results.size(), 1);
    EXPECT_EQ(results[0], "PASSWORD");
}

TEST(RuleSetTest, AllRulesProduceMutations) {
    auto all = collect(RuleSet::apply_all("password"));
    EXPECT_GT(all.size(), 2000);
    EXPECT_TRUE(std::ranges::find(all, "Password") != all.end());
    EXPECT_TRUE(std::ranges::find(all, "p@$$w0rd") != all.end());
    EXPECT_TRUE(std::ranges::find(all, "password0") != all.end());
}

TEST(RuleAttackTest, AppliesRulesToDictionaryWords) {
    auto attack = RuleAttack::create("tests/data/small_wordlist.txt", false, 0, 1);
    ASSERT_TRUE(attack.has_value());

    std::vector<std::string> candidates;
    while (auto c = attack->next()) {
        candidates.push_back(std::move(*c));
    }
    EXPECT_GT(candidates.size(), 10);
    EXPECT_TRUE(std::ranges::find(candidates, "Password") != candidates.end());
    EXPECT_TRUE(std::ranges::find(candidates, "p@$$w0rd") != candidates.end());
    EXPECT_TRUE(std::ranges::find(candidates, "password") != candidates.end());
}

TEST(RuleAttackTest, ChainRulesProducesMoreCandidates) {
    auto without = RuleAttack::create("tests/data/small_wordlist.txt", false, 0, 1);
    auto with_chain = RuleAttack::create("tests/data/small_wordlist.txt", true, 0, 1);
    ASSERT_TRUE(without.has_value());
    ASSERT_TRUE(with_chain.has_value());

    std::size_t count_without = 0;
    while (without->next()) { ++count_without; }

    std::size_t count_with = 0;
    while (with_chain->next()) { ++count_with; }

    EXPECT_GT(count_with, count_without);
}
