// ©AngelaMos | 2026
// MappedFile.hpp

#pragma once

#include <cstddef>
#include <expected>
#include <string_view>
#include "src/core/Concepts.hpp"

class MappedFile {
public:
    MappedFile() = default;
    static std::expected<MappedFile, CrackError> open(std::string_view path);

    ~MappedFile();
    MappedFile(MappedFile&& other) noexcept;
    MappedFile& operator=(MappedFile&& other) noexcept;

    MappedFile(const MappedFile&) = delete;
    MappedFile& operator=(const MappedFile&) = delete;

    const char* data() const { return data_; }
    std::size_t size() const { return size_; }

private:
    const char* data_ = nullptr;
    std::size_t size_ = 0;
    int fd_ = -1;
};
