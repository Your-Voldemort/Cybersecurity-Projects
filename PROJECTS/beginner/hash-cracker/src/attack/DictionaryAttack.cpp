// ©AngelaMos | 2026
// DictionaryAttack.cpp

#include "src/attack/DictionaryAttack.hpp"
#include <algorithm>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

static std::size_t count_lines_in_range(const char* data,
                                        std::size_t start,
                                        std::size_t end) {
    std::size_t count = 0;
    for (std::size_t i = start; i < end; ++i) {
        if (data[i] == '\n') {
            ++count;
        }
    }
    return count;
}

static std::size_t find_next_newline(const char* data,
                                     std::size_t pos,
                                     std::size_t size) {
    while (pos < size && data[pos] != '\n') {
        ++pos;
    }
    return pos < size ? pos + 1 : size;
}

std::expected<DictionaryAttack, CrackError> DictionaryAttack::create(
    std::string_view path, unsigned thread_index, unsigned total_threads) {
    std::string path_str(path);
    int fd = open(path_str.c_str(), O_RDONLY);
    if (fd < 0) {
        return std::unexpected(CrackError::FileNotFound);
    }

    struct stat sb{};
    if (fstat(fd, &sb) < 0) {
        close(fd);
        return std::unexpected(CrackError::FileNotFound);
    }

    auto file_size = static_cast<std::size_t>(sb.st_size);
    if (file_size == 0) {
        close(fd);
        return std::unexpected(CrackError::InvalidConfig);
    }

    auto* mapped = static_cast<const char*>(
        mmap(nullptr, file_size, PROT_READ, MAP_PRIVATE, fd, 0));

    if (mapped == MAP_FAILED) {
        close(fd);
        return std::unexpected(CrackError::FileNotFound);
    }

    madvise(const_cast<char*>(mapped), file_size, MADV_SEQUENTIAL);

    std::size_t total_lines = count_lines_in_range(mapped, 0, file_size);
    if (file_size > 0 && mapped[file_size - 1] != '\n') {
        ++total_lines;
    }

    std::size_t lines_per_thread = total_lines / total_threads;
    std::size_t remainder = total_lines % total_threads;

    std::size_t my_start_line = thread_index * lines_per_thread
        + std::min(static_cast<std::size_t>(thread_index), remainder);
    std::size_t my_line_count = lines_per_thread
        + (thread_index < remainder ? 1 : 0);

    std::size_t start_offset = 0;
    for (std::size_t i = 0; i < my_start_line; ++i) {
        start_offset = find_next_newline(mapped, start_offset, file_size);
    }

    std::size_t end_offset = start_offset;
    for (std::size_t i = 0; i < my_line_count; ++i) {
        end_offset = find_next_newline(mapped, end_offset, file_size);
    }

    DictionaryAttack attack;
    attack.mapped_data_ = mapped;
    attack.file_size_ = file_size;
    attack.fd_ = fd;
    attack.start_offset_ = start_offset;
    attack.end_offset_ = end_offset;
    attack.current_offset_ = start_offset;
    attack.total_words_ = my_line_count;
    attack.words_read_ = 0;

    return attack;
}

DictionaryAttack::~DictionaryAttack() {
    if (mapped_data_ && mapped_data_ != MAP_FAILED) {
        munmap(const_cast<char*>(mapped_data_), file_size_);
    }
    if (fd_ >= 0) {
        close(fd_);
    }
}

DictionaryAttack::DictionaryAttack(DictionaryAttack&& other) noexcept
    : mapped_data_(other.mapped_data_), file_size_(other.file_size_),
      fd_(other.fd_), start_offset_(other.start_offset_),
      end_offset_(other.end_offset_), current_offset_(other.current_offset_),
      total_words_(other.total_words_), words_read_(other.words_read_) {
    other.mapped_data_ = nullptr;
    other.fd_ = -1;
}

DictionaryAttack& DictionaryAttack::operator=(DictionaryAttack&& other) noexcept {
    if (this != &other) {
        if (mapped_data_ && mapped_data_ != MAP_FAILED) {
            munmap(const_cast<char*>(mapped_data_), file_size_);
        }
        if (fd_ >= 0) {
            close(fd_);
        }

        mapped_data_ = other.mapped_data_;
        file_size_ = other.file_size_;
        fd_ = other.fd_;
        start_offset_ = other.start_offset_;
        end_offset_ = other.end_offset_;
        current_offset_ = other.current_offset_;
        total_words_ = other.total_words_;
        words_read_ = other.words_read_;

        other.mapped_data_ = nullptr;
        other.fd_ = -1;
    }
    return *this;
}

std::expected<std::string, AttackComplete> DictionaryAttack::next() {
    if (current_offset_ >= end_offset_) {
        return std::unexpected(AttackComplete{});
    }

    std::size_t line_start = current_offset_;
    std::size_t line_end = line_start;

    while (line_end < end_offset_ && mapped_data_[line_end] != '\n') {
        ++line_end;
    }

    std::size_t word_end = line_end;
    if (word_end > line_start && mapped_data_[word_end - 1] == '\r') {
        --word_end;
    }

    current_offset_ = (line_end < end_offset_) ? line_end + 1 : end_offset_;
    ++words_read_;

    if (word_end <= line_start) {
        return next();
    }

    return std::string(mapped_data_ + line_start, word_end - line_start);
}

std::size_t DictionaryAttack::total() const { return total_words_; }
std::size_t DictionaryAttack::progress() const { return words_read_; }
