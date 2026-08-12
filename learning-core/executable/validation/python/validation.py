from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Registration:
    username: str
    age: int


def parse_registration(payload: object) -> Registration:
    """Validate an untrusted registration payload at the boundary."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be an object")

    allowed = {"username", "age"}
    unknown = set(payload) - allowed
    if unknown:
        raise ValueError(f"unknown fields: {sorted(unknown)}")

    username = payload.get("username")
    age = payload.get("age")

    if not isinstance(username, str):
        raise ValueError("username must be a string")
    username = username.strip()
    if not 1 <= len(username) <= 64:
        raise ValueError("username length must be 1..64")

    if isinstance(age, bool) or not isinstance(age, int):
        raise ValueError("age must be an integer")
    if not 0 <= age <= 130:
        raise ValueError("age must be in range 0..130")

    return Registration(username=username, age=age)
