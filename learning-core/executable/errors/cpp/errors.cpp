#include <stdexcept>
#include <string>
#include <unordered_map>

struct Account {
    int balance;
};

class account_not_found : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class insufficient_funds : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

int withdraw(std::unordered_map<std::string, Account>& accounts,
             const std::string& account_id,
             int amount) {
    if (amount <= 0) {
        throw std::invalid_argument("amount must be positive");
    }
    auto it = accounts.find(account_id);
    if (it == accounts.end()) {
        throw account_not_found(account_id);
    }
    if (it->second.balance < amount) {
        throw insufficient_funds(account_id);
    }
    it->second.balance -= amount;
    return it->second.balance;
}
