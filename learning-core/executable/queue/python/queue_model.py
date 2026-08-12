from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


class QueueFull(RuntimeError):
    pass


@dataclass
class BoundedQueue:
    capacity: int
    _items: deque[str] = field(default_factory=deque)

    def put(self, item: str) -> None:
        if len(self._items) >= self.capacity:
            raise QueueFull("queue capacity reached")
        self._items.append(item)

    def get(self) -> str:
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)
