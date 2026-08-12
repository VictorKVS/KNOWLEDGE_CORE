#include <cassert>

#include "idempotent_message.cpp"

int main() {
    ConsumerState state;
    assert(handle(state, "m1", 10));
    assert(!handle(state, "m1", 10));
    assert(state.total == 10);

    assert(handle(state, "m2", 5));
    assert(state.total == 15);
}
