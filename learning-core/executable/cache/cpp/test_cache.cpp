#include <cassert>
#include <string>

#include "cache.cpp"

int main() {
    Repository repo{{{"user:1", "Ada"}}};
    CacheAside cached(repo);

    assert(cached.get("user:1") == "Ada");
    assert(cached.get("user:1") == "Ada");
    assert(repo.reads == 1);

    repo.data["user:1"] = "Grace";
    assert(cached.get("user:1") == "Ada");

    cached.invalidate("user:1");
    assert(cached.get("user:1") == "Grace");
}
