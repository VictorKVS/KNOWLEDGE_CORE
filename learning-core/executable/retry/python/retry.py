from __future__ import annotations

from collections.abc import Callable


class TransientError(RuntimeError):
    pass


class PermanentError(RuntimeError):
    pass


def call_with_retry(operation: Callable[[], str], *, max_attempts: int = 3) -> str:
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    last_error: TransientError | None = None
    for _ in range(max_attempts):
        try:
            return operation()
        except PermanentError:
            raise
        except TransientError as exc:
            last_error = exc

    assert last_error is not None
    raise last_error


class IdempotentStore:
    def __init__(self) -> None:
        self._results: dict[str, str] = {}
        self.side_effects = 0

    def create_once(self, key: str, value: str) -> str:
        if key in self._results:
            return self._results[key]
        self.side_effects += 1
        self._results[key] = value
        return value
