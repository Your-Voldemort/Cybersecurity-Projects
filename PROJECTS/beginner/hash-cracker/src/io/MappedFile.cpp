// ©AngelaMos | 2026
// MappedFile.cpp

#include "src/io/MappedFile.hpp"
#include <fcntl.h>
#include <string>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

std::expected<MappedFile, CrackError> MappedFile::open(std::string_view path) {
    std::string path_str(path);
    int fd = ::open(path_str.c_str(), O_RDONLY);
    if (fd < 0) {
        return std::unexpected(CrackError::FileNotFound);
    }

    struct stat sb{};
    if (fstat(fd, &sb) < 0) {
        ::close(fd);
        return std::unexpected(CrackError::FileNotFound);
    }

    auto file_size = static_cast<std::size_t>(sb.st_size);
    if (file_size == 0) {
        ::close(fd);
        return std::unexpected(CrackError::InvalidConfig);
    }

    auto* mapped = static_cast<const char*>(
        mmap(nullptr, file_size, PROT_READ, MAP_PRIVATE, fd, 0));

    if (mapped == MAP_FAILED) {
        ::close(fd);
        return std::unexpected(CrackError::FileNotFound);
    }

    madvise(const_cast<char*>(mapped), file_size, MADV_SEQUENTIAL);

    MappedFile mf;
    mf.data_ = mapped;
    mf.size_ = file_size;
    mf.fd_ = fd;
    return mf;
}

MappedFile::~MappedFile() {
    if (data_ && data_ != MAP_FAILED) {
        munmap(const_cast<char*>(data_), size_);
    }
    if (fd_ >= 0) {
        ::close(fd_);
    }
}

MappedFile::MappedFile(MappedFile&& other) noexcept
    : data_(other.data_), size_(other.size_), fd_(other.fd_) {
    other.data_ = nullptr;
    other.fd_ = -1;
}

MappedFile& MappedFile::operator=(MappedFile&& other) noexcept {
    if (this != &other) {
        if (data_ && data_ != MAP_FAILED) {
            munmap(const_cast<char*>(data_), size_);
        }
        if (fd_ >= 0) {
            ::close(fd_);
        }
        data_ = other.data_;
        size_ = other.size_;
        fd_ = other.fd_;
        other.data_ = nullptr;
        other.fd_ = -1;
    }
    return *this;
}
