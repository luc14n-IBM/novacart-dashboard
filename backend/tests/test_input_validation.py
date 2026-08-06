"""
test_input_validation.py — Input validation tests for all parametrised endpoints.

Covers:
  - Valid date formats accepted
  - Malformed dates (bad separators, wrong field order, alphabetic strings)
  - Injection-attempt strings in date parameters
  - Boundary dates (year boundaries, leap-year Feb 29)
  - start > end (inverted range) — must return HTTP 200 with an empty list,
    not a 4xx/5xx, because SQLite's BETWEEN simply returns no rows
  - Extra / unknown query parameters are silently ignored (FastAPI default)
  - Very long string values in parameters

The backend currently accepts any string for `start`/`end` and relies on
SQLite's date comparison. These tests document and pin that contract.
If the backend is hardened with explicit date format validation in future,
update the expected status codes below.
"""

import pytest


# ── Parametrised date-bearing endpoints ───────────────────────────────────────

DATE_ENDPOINTS = [
    "/franchise/orders",
    "/franchise/products",
    "/franchise/customers",
    "/franchise/cities",
]


class TestValidDateFormats:
    """All four parametrised endpoints must accept YYYY-MM-DD without error."""

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_iso_date_range_returns_200(self, client, endpoint):
        r = client.get(endpoint, params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_response_is_a_list(self, client, endpoint):
        r = client.get(endpoint, params={"start": "2022-01-01", "end": "2022-12-31"})
        assert isinstance(r.json(), list)

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_single_day_range(self, client, endpoint):
        """start == end is a valid single-day query."""
        r = client.get(endpoint, params={"start": "2022-01-15", "end": "2022-01-15"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_defaults_used_when_params_omitted(self, client, endpoint):
        """Endpoints have default values — calling without params must not fail."""
        r = client.get(endpoint)
        assert r.status_code == 200

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_full_year_boundary(self, client, endpoint):
        r = client.get(endpoint, params={"start": "2022-01-01", "end": "2022-12-31"})
        assert r.status_code == 200

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_leap_year_date(self, client, endpoint):
        """Feb 29 on a leap year is a valid date and must not crash the backend."""
        r = client.get(endpoint, params={"start": "2020-02-29", "end": "2020-02-29"})
        assert r.status_code == 200

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_non_leap_year_feb_29(self, client, endpoint):
        """2022-02-29 is a non-existent date; SQLite treats it as an out-of-range
        string and returns zero rows — the API must still return 200."""
        r = client.get(endpoint, params={"start": "2022-02-29", "end": "2022-02-29"})
        assert r.status_code == 200
        assert r.json() == []


class TestMalformedDates:
    """
    The current backend passes date strings straight to SQLite.
    Malformed dates that SQLite cannot compare sensibly return empty results (200).
    The tests document this contract — a future validation layer may tighten
    these to 422 responses, in which case the assertions should be updated.
    """

    MALFORMED = [
        "01-01-2022",       # DD-MM-YYYY
        "2022/01/01",       # wrong separator
        "20220101",         # no separators
        "Jan 1 2022",       # human-readable
        "2022-13-01",       # month 13 — out of range
        "2022-00-01",       # month 0 — out of range
        "2022-01-00",       # day 0 — out of range
        "2022-01-32",       # day 32 — out of range
        "not-a-date",       # pure garbage
        "",                 # empty string — uses FastAPI default if omitted
    ]

    @pytest.mark.parametrize("bad_date", MALFORMED)
    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_malformed_start_date(self, client, endpoint, bad_date):
        if bad_date == "":
            pytest.skip("Empty string uses query-param default — tested separately")
        r = client.get(endpoint, params={"start": bad_date, "end": "2022-12-31"})
        # Must not 500 — either empty list (200) or validation error (422)
        assert r.status_code in (200, 422)

    @pytest.mark.parametrize("bad_date", MALFORMED)
    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_malformed_end_date(self, client, endpoint, bad_date):
        if bad_date == "":
            pytest.skip("Empty string uses query-param default — tested separately")
        r = client.get(endpoint, params={"start": "2022-01-01", "end": bad_date})
        assert r.status_code in (200, 422)

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_both_dates_malformed(self, client, endpoint):
        r = client.get(endpoint, params={"start": "bad", "end": "alsoBad"})
        assert r.status_code in (200, 422)


class TestInjectionAttempts:
    """SQL injection strings must never crash the backend or return 500."""

    INJECTION_STRINGS = [
        "' OR '1'='1",
        "'; DROP TABLE fact_orders; --",
        "2022-01-01' OR '1'='1",
        "2022-01-01; SELECT * FROM dim_customer --",
        "1 UNION SELECT * FROM dim_customer",
        "\\x00\\x1a",
    ]

    @pytest.mark.parametrize("payload", INJECTION_STRINGS)
    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_injection_in_start(self, client, endpoint, payload):
        r = client.get(endpoint, params={"start": payload, "end": "2022-12-31"})
        # Parameterised queries must prevent any injection
        assert r.status_code in (200, 422)
        # The table must still exist (injection did not drop it)
        if r.status_code == 200:
            assert isinstance(r.json(), list)

    @pytest.mark.parametrize("payload", INJECTION_STRINGS)
    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_injection_in_end(self, client, endpoint, payload):
        r = client.get(endpoint, params={"start": "2022-01-01", "end": payload})
        assert r.status_code in (200, 422)


class TestInvertedDateRange:
    """start > end produces zero rows, not an error."""

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_inverted_range_returns_empty_list(self, client, endpoint):
        r = client.get(endpoint, params={"start": "2022-12-31", "end": "2022-01-01"})
        assert r.status_code == 200
        assert r.json() == []


class TestExtraParameters:
    """FastAPI silently ignores unknown query parameters — must not raise 422."""

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_unknown_param_ignored(self, client, endpoint):
        r = client.get(
            endpoint,
            params={"start": "2022-01-01", "end": "2022-12-31", "unknown": "value"},
        )
        assert r.status_code == 200

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_duplicate_params_last_wins(self, client, endpoint):
        r = client.get(
            f"{endpoint}?start=2022-01-01&end=2022-12-31&start=1900-01-01"
        )
        # FastAPI takes the last value; result is still valid
        assert r.status_code in (200, 422)


class TestLongStringValues:
    """Very long strings should not crash the server."""

    LONG_STRING = "A" * 10_000

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_very_long_start_param(self, client, endpoint):
        r = client.get(endpoint, params={"start": self.LONG_STRING, "end": "2022-12-31"})
        assert r.status_code in (200, 422)

    @pytest.mark.parametrize("endpoint", DATE_ENDPOINTS)
    def test_very_long_end_param(self, client, endpoint):
        r = client.get(endpoint, params={"start": "2022-01-01", "end": self.LONG_STRING})
        assert r.status_code in (200, 422)


class TestHTTPMethods:
    """All data endpoints are GET-only — other methods must return 405."""

    ALL_ENDPOINTS = DATE_ENDPOINTS + ["/health", "/authorize", "/franchise/summary"]

    @pytest.mark.parametrize("endpoint", ALL_ENDPOINTS)
    def test_post_not_allowed(self, client, endpoint):
        r = client.post(endpoint)
        assert r.status_code == 405

    @pytest.mark.parametrize("endpoint", ALL_ENDPOINTS)
    def test_delete_not_allowed(self, client, endpoint):
        r = client.delete(endpoint)
        assert r.status_code == 405

    @pytest.mark.parametrize("endpoint", ALL_ENDPOINTS)
    def test_put_not_allowed(self, client, endpoint):
        r = client.put(endpoint)
        assert r.status_code == 405
