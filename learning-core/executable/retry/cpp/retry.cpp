#include <functional>
#include <stdexcept>
#include <string>
#include <unordered_map>

class transient_error : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class permanent_error : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

std::string call_with_retry(const std::function<std::string()>& operation, int max_attempts) {
    if (max_attempts < 1) {
        throw std::invalid_argument("max_attempts must be >= 1");
    }

    for (int attempt = 1; attempt <= max_attempts; ++attempt) {
        try {
            return operation();
        } catch (const permanent_error&) {
            throw;
        } catch (const transient_error&) {
            if (attempt == max_attempts) {
                throw;
            }
        }
    }

    throw std::logic_error("unreachable");
}

class IdempotentStore {
public:
    std::string create_once(const std::string& key, const std::string& value) {
        if (const auto it = results_.find(key); it != results_.end()) {
            return it->second;
        }
        ++side_effects;
        results_[key] = value;
        return value;
    }

    int side_effects{0};

private:
    std::unordered_map<std::string, std::string> results_;
};
