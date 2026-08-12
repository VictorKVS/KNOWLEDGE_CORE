#include <stdexcept>
#include <string>
#include <unordered_map>

struct Account {
    int balance;
};

class insufficient_funds : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

void transfer(std::unordered_map<std::string, Account>& accounts,
              const std::string& source,
              const std::string& target,
              int amount) {
    if (amount <= 0) {
        throw std::invalid_argument("amount must be positive");
    }
    auto& src = accounts.at(source);
    auto& dst = accounts.at(target);
    if (src.balance < amount) {
        throw insufficient_funds(source);
    }
    // Commit boundary: validate first, then apply both mutations.
    src.balance -= amount;
    dst.balance += amount;
}
