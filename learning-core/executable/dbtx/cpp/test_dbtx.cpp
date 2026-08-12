#include <cassert>

#include "dbtx.cpp"

int main() {
    Store store{{{"a", 100}, {"b", 50}}};
    auto tx = begin(store);
    transfer(tx, "a", "b", 30);
    commit(store, std::move(tx));
    assert(store.balances.at("a") == 70);
    assert(store.balances.at("b") == 80);

    const auto before = store.balances;
    auto failed = begin(store);
    try {
        transfer(failed, "a", "missing", 10);
        assert(false);
    } catch (const std::out_of_range&) {
    }
    assert(store.balances == before);
}
