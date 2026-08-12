#include <cassert>
#include <stdexcept>
#include <string>

#include "validation.cpp"

static bool rejects(const std::string& name, int age) {
    try {
        (void)parse_registration(name, age);
        return false;
    } catch (const std::invalid_argument&) {
        return true;
    }
}

int main() {
    const auto valid = parse_registration("  Ada  ", 36);
    assert(valid.username == "Ada");
    assert(valid.age == 36);

    assert(rejects("", 36));
    assert(rejects("Ada", -1));
    assert(rejects("Ada", 131));
}
