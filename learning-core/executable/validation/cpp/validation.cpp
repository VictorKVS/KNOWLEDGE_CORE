#include <stdexcept>
#include <string>

struct Registration {
    std::string username;
    int age;
};

static std::string trim_ascii(std::string value) {
    const auto first = value.find_first_not_of(" \t\n\r");
    if (first == std::string::npos) return {};
    const auto last = value.find_last_not_of(" \t\n\r");
    return value.substr(first, last - first + 1);
}

Registration parse_registration(std::string username, int age) {
    username = trim_ascii(std::move(username));
    if (username.empty() || username.size() > 64) {
        throw std::invalid_argument("username length must be 1..64");
    }
    if (age < 0 || age > 130) {
        throw std::invalid_argument("age must be in range 0..130");
    }
    return {std::move(username), age};
}
