#include <stdexcept>
#include <string>
#include <unordered_set>

struct ConsumerState {
    std::unordered_set<std::string> processed_ids;
    int total{0};
};

bool handle(ConsumerState& state, const std::string& message_id, int amount) {
    if (message_id.empty()) {
        throw std::invalid_argument("message id is required");
    }
    if (state.processed_ids.contains(message_id)) {
        return false;
    }
    state.total += amount;
    state.processed_ids.insert(message_id);
    return true;
}
