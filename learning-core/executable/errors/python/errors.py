from __future__ import annotations

from dataclasses import dataclass


class AccountError(Exception):
    """Base domain error."""


class AccountNotFound(AccountError):
    pass


class InsufficientFunds(AccountError):
    pass


@dataclass
class Account:
    balance: int


def withdraw(accounts: dict[str, Account], account_id: str, amount: int) -> int:
    if amount <= 0:
        raise ValueError("amount must be positive")

    account = accounts.get(account_id)
    if account is None:
        raise AccountNotFound(account_id)
    if account.balance < amount:
        raise InsufficientFunds(account_id)

    account.balance -= amount
    return account.balance
