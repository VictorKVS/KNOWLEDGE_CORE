// PROB-SEARCH-001: repeated membership lookup.
// Reference variants for evidence-driven comparison.

#include <algorithm>
#include <stdexcept>
#include <unordered_set>
#include <vector>

bool linear_contains(const std::vector<int>& values, int target) {
    return std::find(values.begin(), values.end(), target) != values.end();
}

bool binary_contains(const std::vector<int>& sorted_values, int target) {
    return std::binary_search(sorted_values.begin(), sorted_values.end(), target);
}

std::unordered_set<int> build_hash_index(const std::vector<int>& values) {
    return std::unordered_set<int>(values.begin(), values.end());
}

bool hash_contains(const std::unordered_set<int>& index, int target) {
    return index.find(target) != index.end();
}

void validate_unique(const std::vector<int>& values) {
    std::unordered_set<int> seen;
    seen.reserve(values.size());
    for (const int value : values) {
        if (!seen.insert(value).second) {
            throw std::invalid_argument("PROB-SEARCH-001 requires unique identifiers");
        }
    }
}
