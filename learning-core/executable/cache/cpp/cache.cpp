#include <string>
#include <unordered_map>

struct Repository {
    std::unordered_map<std::string, std::string> data;
    int reads{0};

    std::string get(const std::string& key) {
        ++reads;
        return data.at(key);
    }
};

class CacheAside {
public:
    explicit CacheAside(Repository& repository) : repository_(repository) {}

    std::string get(const std::string& key) {
        const auto it = cache_.find(key);
        if (it != cache_.end()) {
            return it->second;
        }
        auto value = repository_.get(key);
        cache_[key] = value;
        return value;
    }

    void invalidate(const std::string& key) {
        cache_.erase(key);
    }

private:
    Repository& repository_;
    std::unordered_map<std::string, std::string> cache_;
};
