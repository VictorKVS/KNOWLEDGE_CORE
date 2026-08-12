from __future__ import annotations

import sqlite3


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute("create table accounts(id text primary key, balance integer not null check(balance >= 0))")
    conn.executemany("insert into accounts(id,balance) values(?,?)", [("a", 100), ("b", 50)])
    conn.commit()


def transfer(conn: sqlite3.Connection, source: str, target: str, amount: int) -> None:
    if amount <= 0:
        raise ValueError("amount must be positive")
    with conn:
        row = conn.execute("select balance from accounts where id=?", (source,)).fetchone()
        if row is None:
            raise KeyError(source)
        if row[0] < amount:
            raise ValueError("insufficient funds")
        if conn.execute("select 1 from accounts where id=?", (target,)).fetchone() is None:
            raise KeyError(target)
        conn.execute("update accounts set balance=balance-? where id=?", (amount, source))
        conn.execute("update accounts set balance=balance+? where id=?", (amount, target))
