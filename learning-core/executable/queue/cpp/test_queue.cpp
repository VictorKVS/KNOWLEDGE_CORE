#include <cassert>

#include "queue.cpp"

int main() {
    BoundedQueue q(2);
    q.put("a");
    q.put("b");
    assert(q.get() == "a");
    assert(q.get() == "b");

    BoundedQueue bounded(1);
    bounded.put("a");
    try {
        bounded.put("b");
        assert(false);
    } catch (const queue_full&) {
        assert(bounded.size() == 1);
    }
}
