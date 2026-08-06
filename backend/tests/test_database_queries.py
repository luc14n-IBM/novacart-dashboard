"""
test_database_queries.py — Database query edge case tests.

Tests the connection.py execute_query abstraction and the SQL embedded in
main.py directly against an in-memory SQLite database, validating:
  - Correct row counts for various filter combinations
  - Aggregate function results (SUM, COUNT, MIN, MAX)
  - JOIN correctness (inner joins drop unmatched rows)
  - is_current filter removes historic customer records
  - Status filter allows only 'delivered' and 'shipped'
  - BETWEEN inclusive semantics on boundary dates
  - date_key JOIN produces correct month groupings
  - LIMIT clauses are respected
  - Round-trip numeric precision (ROUND to 2dp)
  - Empty-table queries return empty lists, not errors
"""

import sqlite3
import pytest


# ── In-process SQLite helper ──────────────────────────────────────────────────

def _execute(conn, sql, params=()):
    """Thin wrapper that mirrors execute_query behaviour for SQLite."""
    cur = conn.execute(sql, params)
    return [dict(row) for row in cur.fetchall()]


# ═══════════════════════════════════════════════════════════════════════════════
#  execute_query abstraction (connection.py)
# ═══════════════════════════════════════════════════════════════════════════════

class TestExecuteQuery:
    """Direct unit tests for connection.execute_query with SQLite."""

    def test_returns_list_of_dicts(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, "SELECT 1 AS value")
        assert isinstance(rows, list)
        assert len(rows) == 1
        assert rows[0]["value"] == 1

    def test_parameterised_query(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, "SELECT ? AS v", (42,))
        assert rows[0]["v"] == 42

    def test_empty_result_returns_empty_list(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, "SELECT 1 WHERE 1 = 0")
        assert rows == []

    def test_multiple_rows(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, "SELECT order_id FROM fact_orders ORDER BY order_id")
        # Seed has 5 orders
        assert len(rows) == 5

    def test_keys_are_lowercase(self, db_conn):
        """Column names must be returned in lowercase (matters for Snowflake parity)."""
        from connection import execute_query
        rows = execute_query(db_conn, "SELECT order_id FROM fact_orders LIMIT 1")
        assert "order_id" in rows[0]


# ═══════════════════════════════════════════════════════════════════════════════
#  Status filter — delivered + shipped only
# ═══════════════════════════════════════════════════════════════════════════════

class TestStatusFilter:
    """Only 'delivered' and 'shipped' orders should be counted."""

    def test_cancelled_orders_excluded(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(*) AS n FROM fact_orders
            WHERE status IN ('delivered', 'shipped')
        """)
        # Seed: O001 delivered, O002 shipped, O003 delivered, O005 delivered = 4
        assert rows[0]["n"] == 4

    def test_all_statuses_present_in_seed(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, "SELECT DISTINCT status FROM fact_orders")
        statuses = {r["status"] for r in rows}
        assert "cancelled" in statuses
        assert "delivered" in statuses
        assert "shipped" in statuses

    def test_revenue_excludes_cancelled(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT ROUND(SUM(amount), 2) AS rev
            FROM fact_orders
            WHERE status IN ('delivered', 'shipped')
        """)
        # O001=179.98, O002=49.99, O003=89.99, O005=89.99 => 409.95
        assert abs(rows[0]["rev"] - 409.95) < 0.01


# ═══════════════════════════════════════════════════════════════════════════════
#  BETWEEN inclusive semantics
# ═══════════════════════════════════════════════════════════════════════════════

class TestBetweenSemantics:

    def test_boundary_start_included(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(*) AS n FROM fact_orders
            WHERE order_date BETWEEN ? AND ?
        """, ("2022-01-15", "2022-01-15"))
        assert rows[0]["n"] == 1  # exactly O001

    def test_boundary_end_included(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(*) AS n FROM fact_orders
            WHERE order_date BETWEEN ? AND ?
        """, ("2022-12-01", "2022-12-01"))
        assert rows[0]["n"] == 1  # exactly O005

    def test_inverted_range_returns_zero(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(*) AS n FROM fact_orders
            WHERE order_date BETWEEN ? AND ?
        """, ("2022-12-31", "2022-01-01"))
        assert rows[0]["n"] == 0

    def test_full_year_all_orders(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(*) AS n FROM fact_orders
            WHERE order_date BETWEEN ? AND ?
        """, ("2022-01-01", "2022-12-31"))
        assert rows[0]["n"] == 5  # all seed orders

    def test_single_day_exact_match(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT order_id FROM fact_orders
            WHERE order_date BETWEEN ? AND ?
        """, ("2022-03-10", "2022-03-10"))
        assert len(rows) == 1
        assert rows[0]["order_id"] == "O003"


# ═══════════════════════════════════════════════════════════════════════════════
#  is_current customer filter
# ═══════════════════════════════════════════════════════════════════════════════

class TestIsCurrentFilter:

    def test_non_current_customer_excluded(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT customer_id FROM dim_customer WHERE is_current = 1
        """)
        ids = {r["customer_id"] for r in rows}
        assert "C003" not in ids

    def test_current_customers_count(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(*) AS n FROM dim_customer WHERE is_current = 1
        """)
        assert rows[0]["n"] == 2  # C001, C002 only

    def test_customer_join_excludes_non_current(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT o.order_id
            FROM fact_orders o
            JOIN dim_customer c ON o.customer_id = c.customer_id
            WHERE c.is_current = 1
        """)
        order_ids = {r["order_id"] for r in rows}
        # All seed orders belong to C001 or C002 (both is_current=1), so all appear
        assert len(order_ids) == 5


# ═══════════════════════════════════════════════════════════════════════════════
#  Aggregate correctness
# ═══════════════════════════════════════════════════════════════════════════════

class TestAggregateCorrectness:

    def test_total_revenue_calculation(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT ROUND(SUM(amount), 2) AS total
            FROM fact_orders
            WHERE status IN ('delivered', 'shipped')
              AND order_date BETWEEN ? AND ?
        """, ("2022-01-01", "2022-12-31"))
        # O001=179.98, O002=49.99, O003=89.99, O005=89.99 => 409.95
        assert abs(rows[0]["total"] - 409.95) < 0.01

    def test_unique_customers_count(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(DISTINCT customer_id) AS n
            FROM fact_orders
            WHERE status IN ('delivered', 'shipped')
        """)
        assert rows[0]["n"] == 2  # C001, C002

    def test_unique_orders_count(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(DISTINCT order_id) AS n
            FROM fact_orders
            WHERE status IN ('delivered', 'shipped')
        """)
        assert rows[0]["n"] == 4

    def test_min_max_order_dates(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT MIN(order_date) AS start_date, MAX(order_date) AS end_date
            FROM fact_orders
            WHERE status IN ('delivered', 'shipped')
        """)
        assert rows[0]["start_date"] == "2022-01-15"
        assert rows[0]["end_date"]   == "2022-12-01"

    def test_revenue_rounded_to_2dp(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT ROUND(SUM(amount), 2) AS rev
            FROM fact_orders WHERE order_id = ?
        """, ("O001",))
        # O001 amount is 179.98 — already 2dp, rounding should not change it
        val = rows[0]["rev"]
        assert val == round(val, 2)


# ═══════════════════════════════════════════════════════════════════════════════
#  JOIN correctness
# ═══════════════════════════════════════════════════════════════════════════════

class TestJoinCorrectness:

    def test_date_join_populates_month_name(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT d.month_name
            FROM fact_orders o
            JOIN dim_date d ON o.date_key = d.date_key
            WHERE o.order_id = ?
        """, ("O001",))
        assert rows[0]["month_name"] == "January"

    def test_product_join_populates_name(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT p.name
            FROM fact_orders o
            JOIN dim_product p ON o.product_id = p.product_id
            WHERE o.order_id = ?
        """, ("O001",))
        assert rows[0]["name"] == "Wireless Headphones"

    def test_customer_join_populates_city(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT c.addr_city
            FROM fact_orders o
            JOIN dim_customer c ON o.customer_id = c.customer_id
            WHERE o.order_id = ?
        """, ("O001",))
        assert rows[0]["addr_city"] == "Austin"

    def test_order_with_no_date_key_excluded_by_inner_join(self, db_conn):
        """An order whose date_key doesn't match dim_date is silently excluded by INNER JOIN."""
        from connection import execute_query
        # Insert an order with a date_key that has no corresponding dim_date row
        db_conn.execute(
            "INSERT INTO fact_orders VALUES (?,?,?,?,?,?,?,?,?)",
            ("O_ORPHAN", "C001", "P001", "2023-06-15", 50.00, "USD", "delivered", 1, 99999999),
        )
        db_conn.commit()
        rows = execute_query(db_conn, """
            SELECT o.order_id
            FROM fact_orders o
            JOIN dim_date d ON o.date_key = d.date_key
            WHERE o.order_id = ?
        """, ("O_ORPHAN",))
        assert rows == []
        # Clean up
        db_conn.execute("DELETE FROM fact_orders WHERE order_id = 'O_ORPHAN'")
        db_conn.commit()


# ═══════════════════════════════════════════════════════════════════════════════
#  LIMIT clause
# ═══════════════════════════════════════════════════════════════════════════════

class TestLimitClauses:

    def test_products_limited_to_10(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT o.product_id, SUM(o.amount) AS revenue
            FROM fact_orders o
            JOIN dim_product p ON o.product_id = p.product_id
            WHERE o.status IN ('delivered', 'shipped')
            GROUP BY o.product_id
            ORDER BY revenue DESC
            LIMIT 10
        """)
        assert len(rows) <= 10

    def test_customers_limited_to_20(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT o.customer_id, SUM(o.amount) AS total_spent
            FROM fact_orders o
            JOIN dim_customer c ON o.customer_id = c.customer_id
            WHERE c.is_current = 1 AND o.status IN ('delivered', 'shipped')
            GROUP BY o.customer_id
            ORDER BY total_spent DESC
            LIMIT 20
        """)
        assert len(rows) <= 20


# ═══════════════════════════════════════════════════════════════════════════════
#  Monthly grouping
# ═══════════════════════════════════════════════════════════════════════════════

class TestMonthlyGrouping:

    def test_month_key_format(self, db_conn):
        from connection import execute_query
        import re
        rows = execute_query(db_conn, """
            SELECT d.year || '-' || printf('%02d', d.month) AS month
            FROM fact_orders o
            JOIN dim_date d ON o.date_key = d.date_key
            WHERE o.status IN ('delivered', 'shipped')
            GROUP BY d.year, d.month
        """)
        pattern = re.compile(r"^\d{4}-\d{2}$")
        for row in rows:
            assert pattern.match(row["month"]), f"Bad month: {row['month']}"

    def test_single_month_range(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT COUNT(*) AS n
            FROM fact_orders o
            JOIN dim_date d ON o.date_key = d.date_key
            WHERE o.order_date BETWEEN ? AND ?
              AND o.status IN ('delivered', 'shipped')
            GROUP BY d.year, d.month
        """, ("2022-01-01", "2022-01-31"))
        # Only O001 in January (is_current join not required here)
        assert len(rows) == 1
        assert rows[0]["n"] == 1

    def test_months_in_order(self, db_conn):
        from connection import execute_query
        rows = execute_query(db_conn, """
            SELECT d.year || '-' || printf('%02d', d.month) AS month
            FROM fact_orders o
            JOIN dim_date d ON o.date_key = d.date_key
            WHERE o.status IN ('delivered', 'shipped')
            GROUP BY d.year, d.month
            ORDER BY d.year, d.month
        """)
        months = [r["month"] for r in rows]
        assert months == sorted(months)


# ═══════════════════════════════════════════════════════════════════════════════
#  Empty table queries
# ═══════════════════════════════════════════════════════════════════════════════

class TestEmptyTableQueries:

    def test_count_on_empty_table_returns_zero(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.executescript("""
            CREATE TABLE fact_orders (
                order_id TEXT, customer_id TEXT, product_id TEXT,
                order_date TEXT, amount REAL, currency TEXT, status TEXT,
                quantity INTEGER, date_key INTEGER
            );
        """)
        from connection import execute_query
        import os
        orig_backend = os.environ.get("DATA_BACKEND")
        os.environ["DATA_BACKEND"] = "sqlite"
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        rows = execute_query(conn, "SELECT COUNT(*) AS n FROM fact_orders")
        assert rows[0]["n"] == 0
        connection.DATA_BACKEND = orig
        if orig_backend:
            os.environ["DATA_BACKEND"] = orig_backend

    def test_sum_on_empty_table_returns_null(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("""
            CREATE TABLE fact_orders (
                order_id TEXT, amount REAL, status TEXT, order_date TEXT
            )
        """)
        from connection import execute_query
        import connection
        orig = connection.DATA_BACKEND
        connection.DATA_BACKEND = "sqlite"
        rows = execute_query(conn, "SELECT SUM(amount) AS total FROM fact_orders")
        assert rows[0]["total"] is None
        connection.DATA_BACKEND = orig
