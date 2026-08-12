import pytest

from transaction import Account, InsufficientFunds, transfer


def test_transfer_updates_both_sides() -> None:
    accounts = {"a": Account(100), "b": Account(10)}
    transfer(accounts, "a", "b", 30)
    assert accounts["a"].balance == 70
    assert accounts["b"].balance == 40


def test_failed_transfer_preserves_both_sides() -> None:
    accounts = {"a": Account(20), "b": Account(10)}
    with pytest.raises(InsufficientFunds):
        transfer(accounts, "a", "b", 30)
    assert accounts["a"].balance == 20
    assert accounts["b"].balance == 10
