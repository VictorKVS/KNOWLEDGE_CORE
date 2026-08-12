from cache import CacheAside, Repository


def test_cache_miss_loads_source_and_hit_reuses_cached_value() -> None:
    repo = Repository({"user:1": "Ada"})
    cached = CacheAside(repo)

    assert cached.get("user:1") == "Ada"
    assert cached.get("user:1") == "Ada"
    assert repo.reads == 1


def test_source_change_is_not_visible_until_invalidation() -> None:
    repo = Repository({"user:1": "Ada"})
    cached = CacheAside(repo)
    assert cached.get("user:1") == "Ada"

    repo.data["user:1"] = "Grace"
    assert cached.get("user:1") == "Ada"

    cached.invalidate("user:1")
    assert cached.get("user:1") == "Grace"


def test_cache_is_not_source_of_truth() -> None:
    repo = Repository({"user:1": "Ada"})
    cached = CacheAside(repo)
    cached.cache["user:1"] = "corrupted"
    cached.invalidate("user:1")
    assert cached.get("user:1") == "Ada"
