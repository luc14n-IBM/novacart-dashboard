"""
conftest.py — Shared pytest fixtures for the NovaCart Dashboard backend tests.

Provides:
  - `client`        : a TestClient backed by an in-memory SQLite database (no file I/O)
  - `db_conn`       : the raw in-memory SQLite connection for direct query tests
  - `empty_client`  : a TestClient whose database has tables but zero rows
  - `null_client`   : a TestClient whose database has rows with NULL-able fields set to NULL
"""

import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

# ── Force SQLite backend before the app module is imported ────────────────────
os.environ["DATA_BACKEND"] = "sqlite"
os.environ["CLIENT_VALIDATION"] = "Dev"

# ── Minimal seed data ─────────────────────────────────────────────────────────
_DDL = """
CREATE TABLE dim_date (
    date_key    INTEGER PRIMARY KEY,
    year        INTEGER,
    quarter     INTEGER,
    month       INTEGER,
    month_name  TEXT,
    day_of_week TEXT
);

CREATE TABLE dim_product (
    product_id  TEXT PRIMARY KEY,
    name        TEXT,
    category    TEXT,
    price       REAL
);

CREATE TABLE dim_customer (
    customer_id TEXT PRIMARY KEY,
    name        TEXT,
    email       TEXT,
    addr_city   TEXT,
    addr_state  TEXT,
    valid_from  TEXT,
    valid_to    TEXT,
    is_current  INTEGER DEFAULT 1
);

CREATE TABLE fact_orders (
    order_id    TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id  TEXT,
    order_date  TEXT,
    amount      REAL,
    currency    TEXT,
    status      TEXT,
    quantity    INTEGER,
    date_key    INTEGER
);
"""

_SEED_DATE_ROWS = [
    (20220101, 2022, 1, 1,  "January",  "Saturday"),
    (20220201, 2022, 1, 2,  "February", "Tuesday"),
    (20220301, 2022, 1, 3,  "March",    "Tuesday"),
    (20221201, 2022, 4, 12, "December", "Thursday"),
]

_SEED_PRODUCTS = [
    ("P001", "Wireless Headphones", "Electronics", 89.99),
    ("P002", "Coffee Maker",        "Appliances",  49.99),
]

_SEED_CUSTOMERS = [
    ("C001", "Alice Johnson", "alice@example.com", "Austin",  "TX", "2021-01-01", None, 1),
    ("C002", "Bob Smith",     "bob@example.com",   "Houston", "TX", "2021-01-01", None, 1),
    ("C003", "Past Customer", "past@example.com",  "Dallas",  "TX", "2020-01-01", "2021-12-31", 0),
]

_SEED_ORDERS = [
    ("O001", "C001", "P001", "2022-01-15", 179.98, "USD", "delivered", 2, 20220101),
    ("O002", "C001", "P002", "2022-02-20", 49.99,  "USD", "shipped",   1, 20220201),
    ("O003", "C002", "P001", "2022-03-10", 89.99,  "USD", "delivered", 1, 20220301),
    ("O004", "C002", "P002", "2022-01-05", 99.98,  "USD", "cancelled", 2, 20220101),  # excluded by status filter
    ("O005", "C001", "P001", "2022-12-01", 89.99,  "USD", "delivered", 1, 20221201),
]


def _build_db(seed_orders=True, null_nullable=False):
    """Create an in-memory SQLite DB with optional seeding."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(_DDL)
    conn.executemany("INSERT INTO dim_date VALUES (?,?,?,?,?,?)", _SEED_DATE_ROWS)
    conn.executemany("INSERT INTO dim_product VALUES (?,?,?,?)", _SEED_PRODUCTS)
    if null_nullable:
        conn.execute(
            "INSERT INTO dim_customer VALUES (?,?,?,?,?,?,?,?)",
            ("C001", None, None, None, None, "2021-01-01", None, 1),
        )
        conn.execute(
            "INSERT INTO fact_orders VALUES (?,?,?,?,?,?,?,?,?)",
            ("O001", "C001", "P001", "2022-01-15", None, None, "delivered", None, 20220101),
        )
    else:
        conn.executemany(
            "INSERT INTO dim_customer VALUES (?,?,?,?,?,?,?,?)", _SEED_CUSTOMERS
        )
        if seed_orders:
            conn.executemany(
                "INSERT INTO fact_orders VALUES (?,?,?,?,?,?,?,?,?)", _SEED_ORDERS
            )
    conn.commit()
    return conn


def _make_client(conn):
    """Patch connection.py so the app uses the given in-memory connection."""
    import connection
    import main

    connection.DATA_BACKEND = "sqlite"

    def _patched_get_connection():
        return conn

    original = connection.get_connection
    connection.get_connection = _patched_get_connection
    client = TestClient(main.app, raise_server_exceptions=False)
    connection.get_connection = original  # restore after client is built
    # Keep the patch active for the lifetime of the client by storing it
    client._nc_conn = conn
    client._nc_orig = original
    client._nc_module = connection
    return client


@pytest.fixture(scope="session")
def db_conn():
    return _build_db()


@pytest.fixture(scope="session")
def client(db_conn):
    import connection
    import main
    connection.DATA_BACKEND = "sqlite"
    orig = connection.get_connection
    connection.get_connection = lambda: db_conn
    c = TestClient(main.app, raise_server_exceptions=False)
    yield c
    connection.get_connection = orig


@pytest.fixture(scope="session")
def empty_client():
    conn = _build_db(seed_orders=False)
    import connection
    import main
    connection.DATA_BACKEND = "sqlite"
    orig = connection.get_connection
    connection.get_connection = lambda: conn
    c = TestClient(main.app, raise_server_exceptions=False)
    yield c
    connection.get_connection = orig


@pytest.fixture(scope="session")
def null_client():
    conn = _build_db(seed_orders=False, null_nullable=True)
    import connection
    import main
    connection.DATA_BACKEND = "sqlite"
    orig = connection.get_connection
    connection.get_connection = lambda: conn
    c = TestClient(main.app, raise_server_exceptions=False)
    yield c
    connection.get_connection = orig
