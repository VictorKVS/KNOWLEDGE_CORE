import pytest

from retry import IdempotentStore, PermanentError, TransientError, call_with_retry


def test_transient_failure_can_recover_within_bound() -> None:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TransientError("temporary")
        return "ok"

    assert call_with_retry(operation, max_attempts=3) == "ok"
    assert attempts == 3


def test_permanent_failure_is_not_retried() -> None:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        raise PermanentError("bad request")

    with pytest.raises(PermanentError):
        call_with_retry(operation, max_attempts=5)
    assert attempts == 1


def test_retry_is_bounded() -> None:
    attempts = 0

    def operation() -> str:
        nonlocal attempts
        attempts += 1
        raise TransientError("still down")

    with pytest.raises(TransientError):
        call_with_retry(operation, max_attempts=3)
    assert attempts == 3


def test_idempotency_key_prevents_duplicate_side_effect() -> None:
    store = IdempotentStore()
    assert store.create_once("request-1", "created") == "created"
    assert store.create_once("request-1", "created") == "created"
    assert store.side_effects == 1
