from __future__ import annotations

from dataclasses import dataclass


class InsufficientFunds(ValueError):
    pass


@dataclass
class Account:
    balance: int


def transfer(accounts: dict[str, Account], source: str, target: str, amount: int) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")
    src = accounts[source]
    dst = accounts[target]
    if src.balance < amount:
        raise InsufficientFunds(source)

    # Commit boundary: validate everything first, then apply both mutations.
    src.balance -= amount
    dst.balance += amount
