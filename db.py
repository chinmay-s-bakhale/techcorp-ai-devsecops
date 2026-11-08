"""SQLite storage for support tickets."""
import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "techcorp.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, role TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS tickets "
                  "(id INTEGER PRIMARY KEY AUTOINCREMENT, owner TEXT, title TEXT, status TEXT DEFAULT 'open')")
        if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            c.executemany("INSERT INTO users VALUES (?, ?)",
                          [("alice", "employee"), ("bob", "employee"), ("admin", "administrator")])
            c.executemany("INSERT INTO tickets (owner, title) VALUES (?, ?)",
                          [("alice", "Laptop will not boot"), ("bob", "VPN access request"),
                           ("admin", "Rotate production credentials")])


def create_ticket(owner, title):
    # VULNERABLE: SQL built with string formatting (SQL injection)
    with _conn() as c:
        c.execute(f"INSERT INTO tickets (owner, title) VALUES ('{owner}', '{title}')")


def list_tickets(owner):
    # VULNERABLE: SQL built with string formatting (SQL injection)
    query = f"SELECT id, owner, title, status FROM tickets WHERE owner = '{owner}'"
    with _conn() as c:
        return c.execute(query).fetchall()
