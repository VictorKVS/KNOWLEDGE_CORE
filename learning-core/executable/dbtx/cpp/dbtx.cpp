#include <stdexcept>
#include <string>
#include <unordered_map>

struct Store {
    std::unordered_map<std::string, int> balances;
};

struct Tx {
    std::unordered_map<std::string, int> working;
};

Tx begin(const Store& store) {
    return Tx{store.balances};
}

void transfer(Tx& tx, const std::string& source, const std::string& target, int amount) {
    if (amount <= 0) throw std::invalid_argument("amount must be positive");
    if (!tx.working.contains(source) || !tx.working.contains(target)) {
        throw std::out_of_range("account not found");
    }
    if (tx.working.at(source) < amount) {
        throw std::runtime_error("insufficient funds");
    }
    tx.working.at(source) -= amount;
    tx.working.at(target) += amount;
}

void commit(Store& store, Tx tx) {
    store.balances = std::move(tx.working);
}
