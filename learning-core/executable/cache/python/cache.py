from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Repository:
    data: dict[str, str]
    reads: int = 0

    def get(self, key: str) -> str:
        self.reads += 1
        return self.data[key]


class CacheAside:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.cache: dict[str, str] = {}

    def get(self, key: str) -> str:
        if key in self.cache:
            return self.cache[key]
        value = self.repository.get(key)
        self.cache[key] = value
        return value

    def invalidate(self, key: str) -> None:
        self.cache.pop(key, None)
