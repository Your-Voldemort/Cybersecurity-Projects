// ©AngelaMos | 2026
// HashDetector.cpp

#include "src/hash/HashDetector.hpp"
#include "src/config/Config.hpp"
#include <algorithm>
#include <cctype>

std::expected<HashType, CrackError> HashDetector::detect(std::string_view hash) {
    auto is_hex = [](char c) {
        return (c >= '0' && c <= '9') ||
               (c >= 'a' && c <= 'f') ||
               (c >= 'A' && c <= 'F');
    };

    if (!std::ranges::all_of(hash, is_hex)) {
        return std::unexpected(CrackError::InvalidHash);
    }

    switch (hash.size()) {
        case config::MD5_HEX_LENGTH: return HashType::MD5;
        case config::SHA1_HEX_LENGTH: return HashType::SHA1;
        case config::SHA256_HEX_LENGTH: return HashType::SHA256;
        case config::SHA512_HEX_LENGTH: return HashType::SHA512;
        default: return std::unexpected(CrackError::InvalidHash);
    }
}
