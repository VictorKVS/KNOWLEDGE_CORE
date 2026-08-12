#include <cassert>
#include <unordered_map>
#include <string>

#include "transaction.cpp"

int main() {
    std::unordered_map<std::string, Account> accounts{{"a", {100}}, {"b", {10}}};
    transfer(accounts, "a", "b", 30);
    assert(accounts["a"].balance == 70);
    assert(accounts["b"].balance == 40);

    accounts["a"].balance = 20;
    accounts["b"].balance = 10;
    try {
        transfer(accounts, "a", "b", 30);
        assert(false);
    } catch (const insufficient_funds&) {
        assert(accounts["a"].balance == 20);
        assert(accounts["b"].balance == 10);
    }
}
