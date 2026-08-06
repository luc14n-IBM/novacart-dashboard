"""
test_api.py — Automated tests for the NovaCart Dashboard API.

Run with:  pytest test_api.py -v

All tests use the real novacart_gold.db SQLite database.
No mocking is required — the FastAPI TestClient handles everything in-process.
"""

import pytest


# ── /health ────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200

    def test_response_shape(self, client):
        data = client.get("/health").json()
        assert "status"   in data
        assert "uptime_s" in data
        assert "database" in data

    def test_database_connected(self, client):
        data = client.get("/health").json()
        assert data["database"]["status"] == "connected"

    def test_status_is_healthy(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_uptime_is_nonnegative(self, client):
        data = client.get("/health").json()
        assert data["uptime_s"] >= 0

    def test_backend_field_present(self, client):
        data = client.get("/health").json()
        assert "backend" in data


# ── /authorize ─────────────────────────────────────────────────────────────────

class TestAuthorize:
    # Dev mode
    def test_dev_mode_returns_200(self, client):
        res = client.get("/authorize")
        assert res.status_code == 200

    def test_dev_mode_user(self, client):
        data = client.get("/authorize").json()
        assert data["user"]   == "dev_user"
        assert data["status"] == "authorized"

    # SPCS mode — missing header
    def test_spcs_missing_header_returns_401(self, spcs_client):
        res = spcs_client.get("/authorize")
        assert res.status_code == 401

    # SPCS mode — header present
    def test_spcs_with_header_returns_user(self, spcs_client):
        res = spcs_client.get(
            "/authorize",
            headers={"sf-context-current-user": "alice@example.com"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["user"]   == "alice@example.com"
        assert data["status"] == "authorized"


# ── /franchise/summary ─────────────────────────────────────────────────────────

class TestSummary:
    def test_returns_200(self, client):
        res = client.get("/franchise/summary")
        assert res.status_code == 200

    def test_response_shape(self, client):
        data = client.get("/franchise/summary").json()
        assert "total_revenue"    in data
        assert "total_orders"     in data
        assert "unique_customers" in data
        assert "date_range"       in data

    def test_date_range_has_start_and_end(self, client):
        dr = client.get("/franchise/summary").json()["date_range"]
        assert "start" in dr
        assert "end"   in dr

    def test_total_revenue_is_float(self, client):
        data = client.get("/franchise/summary").json()
        assert isinstance(data["total_revenue"], (int, float))

    def test_total_orders_is_int(self, client):
        data = client.get("/franchise/summary").json()
        assert isinstance(data["total_orders"], int)

    def test_nonnegative_values(self, client):
        data = client.get("/franchise/summary").json()
        assert data["total_revenue"]    >= 0
        assert data["total_orders"]     >= 0
        assert data["unique_customers"] >= 0

    def test_revenue_rounded_to_two_decimals(self, client):
        revenue = client.get("/franchise/summary").json()["total_revenue"]
        assert round(revenue, 2) == revenue


# ── /franchise/orders ──────────────────────────────────────────────────────────

class TestOrders:
    def test_returns_200(self, client):
        res = client.get("/franchise/orders")
        assert res.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/franchise/orders").json()
        assert isinstance(data, list)

    def test_item_shape(self, client):
        data = client.get("/franchise/orders").json()
        assert len(data) > 0, "Expected at least one month of orders"
        item = data[0]
        assert "month"       in item
        assert "month_name"  in item
        assert "order_count" in item
        assert "revenue"     in item

    def test_date_filter_narrows_results(self, client):
        full  = client.get("/franchise/orders?start=2022-01-01&end=2022-12-31").json()
        short = client.get("/franchise/orders?start=2022-01-01&end=2022-03-31").json()
        assert len(short) <= len(full)

    def test_empty_date_range_returns_empty_list(self, client):
        data = client.get("/franchise/orders?start=2000-01-01&end=2000-01-31").json()
        assert data == []

    def test_revenue_values_are_numeric(self, client):
        data = client.get("/franchise/orders").json()
        for item in data:
            assert isinstance(item["revenue"], (int, float))

    def test_months_are_in_order(self, client):
        data = client.get("/franchise/orders").json()
        months = [item["month"] for item in data]
        assert months == sorted(months)


# ── /franchise/products ────────────────────────────────────────────────────────

class TestProducts:
    def test_returns_200(self, client):
        res = client.get("/franchise/products")
        assert res.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/franchise/products").json()
        assert isinstance(data, list)

    def test_max_ten_results(self, client):
        data = client.get("/franchise/products").json()
        assert len(data) <= 10

    def test_item_shape(self, client):
        data = client.get("/franchise/products").json()
        assert len(data) > 0, "Expected at least one product"
        item = data[0]
        assert "product_id" in item
        assert "name"       in item
        assert "category"   in item
        assert "units_sold" in item
        assert "revenue"    in item

    def test_sorted_by_revenue_descending(self, client):
        data = client.get("/franchise/products").json()
        revenues = [item["revenue"] for item in data]
        assert revenues == sorted(revenues, reverse=True)

    def test_date_filter_returns_at_most_ten(self, client):
        data = client.get("/franchise/products?start=2022-01-01&end=2022-01-31").json()
        assert len(data) <= 10

    def test_empty_date_range_returns_empty_list(self, client):
        data = client.get("/franchise/products?start=2000-01-01&end=2000-01-31").json()
        assert data == []


# ── /franchise/customers ───────────────────────────────────────────────────────

class TestCustomers:
    def test_returns_200(self, client):
        res = client.get("/franchise/customers")
        assert res.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/franchise/customers").json()
        assert isinstance(data, list)

    def test_max_twenty_results(self, client):
        data = client.get("/franchise/customers").json()
        assert len(data) <= 20

    def test_item_shape(self, client):
        data = client.get("/franchise/customers").json()
        assert len(data) > 0, "Expected at least one customer"
        item = data[0]
        assert "customer_id"  in item
        assert "name"         in item
        assert "city"         in item
        assert "state"        in item
        assert "total_orders" in item
        assert "total_spent"  in item

    def test_sorted_by_total_spent_descending(self, client):
        data = client.get("/franchise/customers").json()
        spent = [item["total_spent"] for item in data]
        assert spent == sorted(spent, reverse=True)

    def test_date_filter_narrows_results(self, client):
        full  = client.get("/franchise/customers?start=2022-01-01&end=2022-12-31").json()
        short = client.get("/franchise/customers?start=2022-06-01&end=2022-06-30").json()
        assert len(short) <= len(full)

    def test_empty_date_range_returns_empty_list(self, client):
        data = client.get("/franchise/customers?start=2000-01-01&end=2000-01-31").json()
        assert data == []


# ── /franchise/cities ──────────────────────────────────────────────────────────

class TestCities:
    def test_returns_200(self, client):
        res = client.get("/franchise/cities")
        assert res.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/franchise/cities").json()
        assert isinstance(data, list)

    def test_item_shape(self, client):
        data = client.get("/franchise/cities").json()
        assert len(data) > 0, "Expected at least one city"
        item = data[0]
        assert "city"        in item
        assert "state"       in item
        assert "order_count" in item
        assert "revenue"     in item

    def test_sorted_by_revenue_descending(self, client):
        data = client.get("/franchise/cities").json()
        revenues = [item["revenue"] for item in data]
        assert revenues == sorted(revenues, reverse=True)

    def test_date_filter_narrows_results(self, client):
        full  = client.get("/franchise/cities?start=2022-01-01&end=2022-12-31").json()
        short = client.get("/franchise/cities?start=2022-06-01&end=2022-06-30").json()
        assert len(short) <= len(full)

    def test_empty_date_range_returns_empty_list(self, client):
        data = client.get("/franchise/cities?start=2000-01-01&end=2000-01-31").json()
        assert data == []
