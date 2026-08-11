#include <cassert>
#include <unordered_set>
#include <vector>

bool linear_contains(const std::vector<int>& values, int target);
bool binary_contains(const std::vector<int>& sorted_values, int target);
bool hash_contains(const std::unordered_set<int>& values, int target);

int main() {
    const std::vector<int> values{1, 3, 5, 7, 9};
    const std::unordered_set<int> set{1, 3, 5, 7, 9};

    assert(linear_contains(values, 7));
    assert(binary_contains(values, 7));
    assert(hash_contains(set, 7));

    assert(!linear_contains(values, 4));
    assert(!binary_contains(values, 4));
    assert(!hash_contains(set, 4));

    const std::vector<int> empty;
    const std::unordered_set<int> empty_set;
    assert(!linear_contains(empty, 1));
    assert(!binary_contains(empty, 1));
    assert(!hash_contains(empty_set, 1));

    const std::vector<int> one{42};
    const std::unordered_set<int> one_set{42};
    assert(linear_contains(one, 42));
    assert(binary_contains(one, 42));
    assert(hash_contains(one_set, 42));

    return 0;
}
