#include <cassert>
#include <string>

#include "retry.cpp"

int main() {
    int attempts = 0;
    const auto result = call_with_retry([&attempts]() -> std::string {
        ++attempts;
        if (attempts < 3) throw transient_error("temporary");
        return "ok";
    }, 3);
    assert(result == "ok");
    assert(attempts == 3);

    attempts = 0;
    try {
        (void)call_with_retry([&attempts]() -> std::string {
            ++attempts;
            throw permanent_error("bad request");
        }, 5);
        assert(false);
    } catch (const permanent_error&) {
        assert(attempts == 1);
    }

    attempts = 0;
    try {
        (void)call_with_retry([&attempts]() -> std::string {
            ++attempts;
            throw transient_error("still down");
        }, 3);
        assert(false);
    } catch (const transient_error&) {
        assert(attempts == 3);
    }

    IdempotentStore store;
    assert(store.create_once("request-1", "created") == "created");
    assert(store.create_once("request-1", "created") == "created");
    assert(store.side_effects == 1);
}
