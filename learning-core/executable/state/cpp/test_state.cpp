#include <cassert>

#include "state.cpp"

int main() {
    Document doc;
    doc = transition(doc, Status::approved);
    doc = transition(doc, Status::published);
    doc = transition(doc, Status::archived);
    assert(doc.status == Status::archived);

    const Document original;
    try {
        (void)transition(original, Status::published);
        assert(false);
    } catch (const invalid_transition&) {
        assert(original.status == Status::draft);
    }
}
