import pytest

from errors import Account, AccountNotFound, InsufficientFunds, withdraw


def test_withdraw_returns_new_balance() -> None:
    accounts = {"a": Account(100)}
    assert withdraw(accounts, "a", 30) == 70


def test_unknown_account_is_domain_error() -> None:
    with pytest.raises(AccountNotFound):
        withdraw({}, "missing", 10)


def test_insufficient_funds_is_domain_error_and_state_is_unchanged() -> None:
    accounts = {"a": Account(20)}
    with pytest.raises(InsufficientFunds):
        withdraw(accounts, "a", 30)
    assert accounts["a"].balance == 20


def test_invalid_amount_is_programming_contract_error() -> None:
    with pytest.raises(ValueError):
        withdraw({"a": Account(20)}, "a", 0)
