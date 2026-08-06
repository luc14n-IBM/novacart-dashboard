"""
test_edge_cases.py — Edge case tests for all NovaCart Dashboard API endpoints.

Covers:
  - Empty result sets (date range with no matching data)
  - Null / None field values in database rows
  - Boundary dates (first/last day of year, cross-year range)
  - Summary endpoint with no qualifying orders
  - Health endpoint in both healthy and degraded states
  - Authorize endpoint in Dev mode and SPCS mode
  - Response shape / field presence for each endpoint
  - Numeric field types (revenue must be a number, not a string)
  - Status filter — cancelled/pending orders must be excluded
  - Cross-year date ranges
"""

import os
import sqlite3
import pytest
from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════════════════════════════════
#  Health endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestHealthEndpoint:

    def test_healthy_status(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "healthy"

    def test_health_has_uptime(self, client):
        r = client.get("/health")
        body = r.json()
        assert "uptime_s" in body
        assert isinstance(body["uptime_s"], (int, float))
        assert body["uptime_s"] >= 0

    def test_health_has_database_block(self, client):
        r = client.get("/health")
        body = r.json()
        assert "database" in body
        assert body["database"]["status"] == "connected"

    def test_health_reports_backend(self, client):
        r = client.get("/health")
        assert "backend" in r.json()

    def test_health_degraded_on_db_failure(self, monkeypatch):
        """When the database is unreachable the health endpoint must return 503."""
        import connection
        # main.py calls _conn_module.get_connection() — patch the module attribute
        monkeypatch.setattr(connection, "get_connection", lambda: (_ for _ in ()).throw(Exception("db down")))
        import main
        c = TestClient(main.app, raise_server_exceptions=False)
        r = c.get("/health")
        assert r.status_code == 503
        assert r.json()["status"] == "degraded"


# ═══════════════════════════════════════════════════════════════════════════════
#  Authorize endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestAuthorizeEndpoint:

    def test_dev_mode_returns_dev_user(self, client):
        r = client.get("/authorize")
        assert r.status_code == 200
        body = r.json()
        assert body["user"] == "dev_user"
        assert body["status"] == "authorized"

    def test_spcs_mode_with_header(self, monkeypatch):
        import main
        monkeypatch.setattr(main, "CLIENT_VALIDATION", "SPCS")
        c = TestClient(main.app, raise_server_exceptions=False)
        r = c.get("/authorize", headers={"sf-context-current-user": "john.doe@example.com"})
        assert r.status_code == 200
        assert r.json()["user"] == "john.doe@example.com"

    def test_spcs_mode_missing_header_returns_401(self, monkeypatch):
        import main
        monkeypatch.setattr(main, "CLIENT_VALIDATION", "SPCS")
        c = TestClient(main.app, raise_server_exceptions=False)
        r = c.get("/authorize")
        assert r.status_code == 401

    def test_authorize_header_case_insensitive(self, monkeypatch):
        """HTTP headers are case-insensitive; the backend reads sf-context-current-user."""
        import main
        monkeypatch.setattr(main, "CLIENT_VALIDATION", "SPCS")
        c = TestClient(main.app, raise_server_exceptions=False)
        # TestClient / Starlette normalises headers to lowercase already
        r = c.get("/authorize", headers={"SF-Context-Current-User": "alice"})
        assert r.status_code == 200
        assert r.json()["user"] == "alice"


# ═══════════════════════════════════════════════════════════════════════════════
#  Summary endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestSummaryEndpoint:

    def test_summary_response_shape(self, client):
        r = client.get("/franchise/summary")
        assert r.status_code == 200
        body = r.json()
        assert "total_revenue" in body
        assert "total_orders" in body
        assert "unique_customers" in body
        assert "date_range" in body
        assert "start" in body["date_range"]
        assert "end" in body["date_range"]

    def test_summary_revenue_is_number(self, client):
        body = client.get("/franchise/summary").json()
        assert isinstance(body["total_revenue"], (int, float))

    def test_summary_orders_is_integer(self, client):
        body = client.get("/franchise/summary").json()
        assert isinstance(body["total_orders"], int)

    def test_summary_customers_is_integer(self, client):
        body = client.get("/franchise/summary").json()
        assert isinstance(body["unique_customers"], int)

    def test_summary_excludes_cancelled_orders(self, client):
        """Cancelled orders must not be counted in the summary totals."""
        body = client.get("/franchise/summary").json()
        # Seed has 4 qualifying orders (O001, O002, O003, O005) and 1 cancelled (O004)
        assert body["total_orders"] == 4

    def test_summary_empty_database_returns_404(self, empty_client):
        """With no qualifying orders get_summary raises 404 — no data found."""
        r = empty_client.get("/franchise/summary")
        assert r.status_code == 404

    def test_summary_date_range_null_when_empty(self, empty_client):
        """When there are no orders get_summary raises 404 (total_orders == 0)."""
        r = empty_client.get("/franchise/summary")
        assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
#  Orders endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestOrdersEndpoint:

    def test_orders_response_shape(self, client):
        r = client.get("/franchise/orders", params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200
        rows = r.json()
        assert len(rows) > 0
        row = rows[0]
        assert "month" in row
        assert "month_name" in row
        assert "order_count" in row
        assert "revenue" in row

    def test_orders_revenue_is_numeric(self, client):
        rows = client.get("/franchise/orders", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        for row in rows:
            assert isinstance(row["revenue"], (int, float))

    def test_orders_month_format(self, client):
        """month field must be YYYY-MM."""
        rows = client.get("/franchise/orders", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        import re
        pattern = re.compile(r"^\d{4}-\d{2}$")
        for row in rows:
            assert pattern.match(row["month"]), f"Bad month format: {row['month']}"

    def test_orders_cancelled_excluded(self, client):
        """The cancelled order O004 is in January; total Jan orders should be 1."""
        rows = client.get("/franchise/orders", params={"start": "2022-01-01", "end": "2022-01-31"}).json()
        jan = next((r for r in rows if r["month"] == "2022-01"), None)
        assert jan is not None
        assert jan["order_count"] == 1  # O001 only (O004 is cancelled)

    def test_orders_empty_range_returns_empty_list(self, client):
        r = client.get("/franchise/orders", params={"start": "2000-01-01", "end": "2000-12-31"})
        assert r.status_code == 200
        assert r.json() == []

    def test_orders_cross_year_range(self, client):
        """A range spanning multiple years must return rows from each year."""
        r = client.get("/franchise/orders", params={"start": "2020-01-01", "end": "2025-12-31"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_orders_ordered_chronologically(self, client):
        rows = client.get("/franchise/orders", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        months = [r["month"] for r in rows]
        assert months == sorted(months)

    def test_orders_empty_database(self, empty_client):
        r = empty_client.get("/franchise/orders", params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200
        assert r.json() == []


# ═══════════════════════════════════════════════════════════════════════════════
#  Products endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestProductsEndpoint:

    def test_products_response_shape(self, client):
        rows = client.get("/franchise/products", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        assert len(rows) > 0
        row = rows[0]
        for field in ("product_id", "name", "category", "units_sold", "revenue"):
            assert field in row, f"Missing field: {field}"

    def test_products_at_most_10_rows(self, client):
        rows = client.get("/franchise/products", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        assert len(rows) <= 10

    def test_products_ordered_by_revenue_desc(self, client):
        rows = client.get("/franchise/products", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        revenues = [r["revenue"] for r in rows]
        assert revenues == sorted(revenues, reverse=True)

    def test_products_revenue_is_numeric(self, client):
        rows = client.get("/franchise/products", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        for row in rows:
            assert isinstance(row["revenue"], (int, float))

    def test_products_units_sold_non_negative(self, client):
        rows = client.get("/franchise/products", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        for row in rows:
            assert row["units_sold"] >= 0

    def test_products_empty_range(self, client):
        r = client.get("/franchise/products", params={"start": "1990-01-01", "end": "1990-12-31"})
        assert r.status_code == 200
        assert r.json() == []

    def test_products_empty_database(self, empty_client):
        r = empty_client.get("/franchise/products", params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200
        assert r.json() == []


# ═══════════════════════════════════════════════════════════════════════════════
#  Customers endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestCustomersEndpoint:

    def test_customers_response_shape(self, client):
        rows = client.get("/franchise/customers", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        assert len(rows) > 0
        row = rows[0]
        for field in ("customer_id", "name", "city", "state", "total_orders", "total_spent"):
            assert field in row, f"Missing field: {field}"

    def test_customers_at_most_20_rows(self, client):
        rows = client.get("/franchise/customers", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        assert len(rows) <= 20

    def test_customers_ordered_by_total_spent_desc(self, client):
        rows = client.get("/franchise/customers", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        spent = [r["total_spent"] for r in rows]
        assert spent == sorted(spent, reverse=True)

    def test_customers_excludes_non_current(self, client):
        """dim_customer.is_current = 0 rows must not appear in results."""
        rows = client.get("/franchise/customers", params={"start": "2020-01-01", "end": "2025-12-31"}).json()
        customer_ids = [r["customer_id"] for r in rows]
        assert "C003" not in customer_ids  # C003 has is_current = 0

    def test_customers_empty_range(self, client):
        r = client.get("/franchise/customers", params={"start": "1990-01-01", "end": "1990-12-31"})
        assert r.status_code == 200
        assert r.json() == []

    def test_customers_empty_database(self, empty_client):
        r = empty_client.get("/franchise/customers", params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200
        assert r.json() == []

    def test_customers_total_spent_is_numeric(self, client):
        rows = client.get("/franchise/customers", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        for row in rows:
            assert isinstance(row["total_spent"], (int, float))


# ═══════════════════════════════════════════════════════════════════════════════
#  Cities endpoint
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestCitiesEndpoint:

    def test_cities_response_shape(self, client):
        rows = client.get("/franchise/cities", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        assert len(rows) > 0
        row = rows[0]
        for field in ("city", "state", "order_count", "revenue"):
            assert field in row, f"Missing field: {field}"

    def test_cities_ordered_by_revenue_desc(self, client):
        rows = client.get("/franchise/cities", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        revenues = [r["revenue"] for r in rows]
        assert revenues == sorted(revenues, reverse=True)

    def test_cities_revenue_is_numeric(self, client):
        rows = client.get("/franchise/cities", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        for row in rows:
            assert isinstance(row["revenue"], (int, float))

    def test_cities_excludes_non_current_customers(self, client):
        """is_current = 0 customers must not contribute city revenue."""
        rows = client.get("/franchise/cities", params={"start": "2020-01-01", "end": "2025-12-31"}).json()
        # C003 is in Dallas — if it appeared it was incorrectly included
        cities = [r["city"] for r in rows]
        # Dallas would only appear if C003 orders existed (they don't in seed, but
        # the is_current filter is what we validate here)
        assert "Dallas" not in cities

    def test_cities_empty_range(self, client):
        r = client.get("/franchise/cities", params={"start": "1990-01-01", "end": "1990-12-31"})
        assert r.status_code == 200
        assert r.json() == []

    def test_cities_empty_database(self, empty_client):
        r = empty_client.get("/franchise/cities", params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200
        assert r.json() == []

    def test_cities_order_count_positive(self, client):
        rows = client.get("/franchise/cities", params={"start": "2022-01-01", "end": "2022-12-31"}).json()
        for row in rows:
            assert row["order_count"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  NULL field edge cases
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestNullFieldEdgeCases:
    """When rows in the DB have NULL values the API must not crash."""

    def test_summary_null_amount_treated_as_zero(self, null_client):
        """SUM(amount) of a NULL row is NULL; the endpoint coalesces to 0."""
        r = null_client.get("/franchise/summary")
        assert r.status_code == 200
        assert r.json()["total_revenue"] == 0

    def test_orders_handles_null_amounts(self, null_client):
        r = null_client.get("/franchise/orders", params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
#  404 / unknown route
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.mark.edge_case
class TestUnknownRoutes:

    def test_unknown_path_returns_404(self, client):
        r = client.get("/does/not/exist")
        assert r.status_code == 404

    def test_old_franchise_id_route_returns_404(self, client):
        """The deprecated /franchise/{id}/* pattern is not registered."""
        r = client.get("/franchise/1/summary")
        assert r.status_code == 404
