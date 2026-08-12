#include <cassert>
#include <stdexcept>
#include <string>
#include <unordered_map>

#include "errors.cpp"

int main() {
    std::unordered_map<std::string, Account> accounts{{"a", {100}}};
    assert(withdraw(accounts, "a", 30) == 70);

    accounts["a"].balance = 20;
    try {
        (void)withdraw(accounts, "a", 30);
        assert(false);
    } catch (const insufficient_funds&) {
        assert(accounts["a"].balance == 20);
    }

    try {
        (void)withdraw(accounts, "missing", 1);
        assert(false);
    } catch (const account_not_found&) {
    }

    try {
        (void)withdraw(accounts, "a", 0);
        assert(false);
    } catch (const std::invalid_argument&) {
    }
}
