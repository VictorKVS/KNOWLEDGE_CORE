import sqlite3
import pytest

from dbtx import init_db, transfer


def balances(conn):
    return dict(conn.execute("select id,balance from accounts"))


def test_transfer_commits_both_changes() -> None:
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    transfer(conn, "a", "b", 30)
    assert balances(conn) == {"a": 70, "b": 80}


def test_failure_rolls_back_transaction() -> None:
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    before = balances(conn)
    with pytest.raises(KeyError):
        transfer(conn, "a", "missing", 30)
    assert balances(conn) == before
