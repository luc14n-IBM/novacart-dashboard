# Testing Guide — NovaCart Dashboard

## Overview

This guide covers the comprehensive edge case and input validation testing framework for the NovaCart Dashboard. The testing strategy ensures robustness across backend APIs, database queries, and frontend response handling.

---

## Backend Testing (Python / pytest)

### Test Suites

#### 1. **Input Validation Tests** (`backend/tests/test_input_validation.py`)

Tests that all parametrised endpoints accept valid inputs and reject/handle invalid inputs gracefully.

**Coverage:**
- ✓ Valid ISO 8601 date formats (YYYY-MM-DD)
- ✓ Single-day ranges (start == end)
- ✓ Default parameter values
- ✓ Full year boundaries (Jan 1 - Dec 31)
- ✓ Leap year dates (Feb 29)
- ✓ Non-leap year invalid dates (2022-02-29)
- ✓ Malformed dates (wrong separators, out-of-range months/days)
- ✓ SQL injection attempts in date parameters
- ✓ Inverted date ranges (start > end)
- ✓ Unknown/extra query parameters
- ✓ Very long string values (10,000+ chars)
- ✓ HTTP method enforcement (GET-only)

**Key Test Classes:**
- `TestValidDateFormats` — ensures valid dates are accepted
- `TestMalformedDates` — validates handling of bad date formats
- `TestInjectionAttempts` — security: parameterised queries prevent injection
- `TestInvertedDateRange` — returns empty list, not error
- `TestExtraParameters` — unknown params silently ignored
- `TestLongStringValues` — long strings handled safely
- `TestHTTPMethods` — POST/DELETE/PUT return 405

**Running:**
```bash
cd backend
python -m pytest tests/test_input_validation.py -v
```

---

#### 2. **Edge Case Tests** (`backend/tests/test_edge_cases.py`)

Tests each endpoint's behaviour under edge case conditions.

**Coverage by Endpoint:**

**Health Endpoint:**
- ✓ Healthy response structure
- ✓ Uptime field is numeric and >= 0
- ✓ Database connection block present
- ✓ Backend field reported
- ✓ Degraded state on DB failure (503)

**Authorize Endpoint:**
- ✓ Dev mode returns mock user
- ✓ SPCS mode reads sf-context-current-user header
- ✓ Missing header in SPCS mode returns 422
- ✓ Header case-insensitivity

**Summary Endpoint:**
- ✓ Response contains all required fields
- ✓ Revenue is numeric (not string)
- ✓ Order/customer counts are integers
- ✓ Cancelled orders excluded
- ✓ Empty database returns zeros (not nulls for numeric fields)
- ✓ Null date_range when no data

**Orders/Products/Customers/Cities Endpoints:**
- ✓ Response shape (all required fields present)
- ✓ Numeric fields are actually numeric
- ✓ Sorting by revenue/spent (descending)
- ✓ LIMIT clauses respected (10/20 rows)
- ✓ Empty date ranges return empty list
- ✓ Empty database returns empty list
- ✓ Month format validation (YYYY-MM)
- ✓ Cancelled orders excluded
- ✓ Non-current customers excluded

**NULL Field Edge Cases:**
- ✓ SUM(NULL) coalesced to 0
- ✓ NULL amounts handled

**Unknown Routes:**
- ✓ 404 for unknown paths
- ✓ 404 for deprecated /franchise/{id}/* pattern

**Running:**
```bash
cd backend
python -m pytest tests/test_edge_cases.py -v
```

---

#### 3. **Database Query Tests** (`backend/tests/test_database_queries.py`)

Direct unit tests of SQL queries and the `connection.execute_query()` abstraction.

**Coverage:**

**execute_query Abstraction:**
- ✓ Returns list of dicts
- ✓ Parameterised queries work
- ✓ Empty results return []
- ✓ Multiple rows returned
- ✓ Column names lowercase (Snowflake parity)

**Status Filter (delivered + shipped):**
- ✓ Cancelled orders excluded
- ✓ All statuses present in seed data
- ✓ Revenue calculation excludes cancelled

**BETWEEN Semantics:**
- ✓ Start date boundary included
- ✓ End date boundary included
- ✓ Inverted range returns 0 rows
- ✓ Full year queries work
- ✓ Single-day exact match

**is_current Filter:**
- ✓ Non-current customers (is_current=0) excluded
- ✓ COUNT of current customers correct
- ✓ JOIN excludes non-current rows

**Aggregate Functions:**
- ✓ SUM revenue calculation correct
- ✓ COUNT DISTINCT customers
- ✓ COUNT DISTINCT orders
- ✓ MIN/MAX order dates
- ✓ ROUND to 2 decimal places

**JOIN Correctness:**
- ✓ date_key JOIN populates month_name
- ✓ product_id JOIN populates name
- ✓ customer_id JOIN populates city
- ✓ Orphan rows (no matching date_key) excluded by INNER JOIN

**LIMIT Clauses:**
- ✓ Products limited to 10
- ✓ Customers limited to 20

**Monthly Grouping:**
- ✓ Month key format (YYYY-MM)
- ✓ Single-month ranges
- ✓ Months in chronological order

**Empty Tables:**
- ✓ COUNT on empty table returns 0
- ✓ SUM on empty table returns NULL

**Running:**
```bash
cd backend
python -m pytest tests/test_database_queries.py -v
```

---

### Test Fixtures (`conftest.py`)

The test suite uses in-memory SQLite fixtures to avoid file I/O and database dependencies.

**Fixtures:**

1. **`db_conn`** — Session-scoped in-memory DB with seed data
   - 4 qualifying orders (delivered/shipped)
   - 1 cancelled order
   - 2 current customers + 1 non-current
   - 2 products
   - Seed date rows for month grouping

2. **`client`** — TestClient bound to `db_conn`
   - Use for integration tests
   - All endpoints callable

3. **`empty_client`** — TestClient with empty tables (schema only)
   - Tests empty result handling
   - Numeric fields should be 0, not null

4. **`null_client`** — TestClient with NULL-able fields set to NULL
   - Tests aggregate function handling of NULL values

**Seed Data:**

Orders:
```
O001: C001, 2022-01-15, $179.98, delivered ✓
O002: C001, 2022-02-20, $49.99,  shipped ✓
O003: C002, 2022-03-10, $89.99,  delivered ✓
O004: C002, 2022-01-05, $99.98,  cancelled ✗
O005: C001, 2022-12-01, $89.99,  delivered ✓
```

Qualifying totals: 4 orders, $409.95 revenue, 2 customers

---

### Running Tests

**All tests:**
```bash
cd backend
python -m pytest tests/ -v
```

**Specific test file:**
```bash
python -m pytest tests/test_input_validation.py -v
```

**Specific test class:**
```bash
python -m pytest tests/test_input_validation.py::TestValidDateFormats -v
```

**Specific test:**
```bash
python -m pytest tests/test_input_validation.py::TestValidDateFormats::test_iso_date_range_returns_200 -v
```

**With coverage report:**
```bash
python -m pytest tests/ -v --cov=. --cov-report=html
# Opens htmlcov/index.html in browser
```

**Run only fast tests (skip integration):**
```bash
python -m pytest tests/ -v -m "not integration"
```

---

## Frontend Testing (JavaScript / Vitest)

### Test Suite: `frontend/tests/api.test.js`

Tests the frontend's ability to handle API responses, including edge cases and error conditions.

**Coverage:**

**Health Endpoint:**
- ✓ Valid healthy response
- ✓ Degraded response with error message
- ✓ Null uptime coercion to 0

**Summary Endpoint:**
- ✓ Valid response shape
- ✓ Zero values
- ✓ String numbers coerced to actual numbers
- ✓ Missing fields with defaults
- ✓ Null date_range handling

**Orders Endpoint:**
- ✓ Valid list of monthly summaries
- ✓ Empty list
- ✓ Null revenue values
- ✓ Invalid month format (13, etc.)
- ✓ Missing month_name field
- ✓ Negative revenue (refunds)

**Products Endpoint:**
- ✓ Valid list (max 10 rows)
- ✓ Empty list
- ✓ Missing category
- ✓ Null numeric fields
- ✓ Not sorted by revenue (should be sorted)

**Customers Endpoint:**
- ✓ Valid list (max 20 rows)
- ✓ Empty list
- ✓ Null city/state
- ✓ Unusual state codes
- ✓ Not sorted by spend
- ✓ Zero total_orders

**Cities Endpoint:**
- ✓ Valid list with all fields
- ✓ Empty list
- ✓ Null city names
- ✓ Unusual state codes
- ✓ Not sorted by revenue
- ✓ Negative order counts

**Network Error Handling:**
- ✓ 500 errors
- ✓ 404 errors
- ✓ 422 validation errors
- ✓ Network timeouts
- ✓ Malformed JSON
- ✓ Empty response body

**Type Validation:**
- ✓ Object vs. array detection
- ✓ String vs. number detection
- ✓ Missing fields
- ✓ Unexpected extra fields

**Running:**
```bash
cd frontend
npm test
```

---

## Test Configuration

### Backend: `pytest.ini`

```ini
[pytest]
testpaths = tests .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --tb=short --cov=. --cov-report=term-missing --cov-fail-under=95
markers =
    integration: marks tests as integration tests (require real database)
    unit: marks tests as unit tests (fast, no I/O)
    edge_case: marks tests that validate edge cases
    validation: marks tests that validate input handling
```

Coverage is also enforced via `.coveragerc` (omits `setup_tests.py` and `venv/`).

### Frontend: `vite.config.js`

Coverage is configured under the `test.coverage` block using `@vitest/coverage-v8`:

```js
coverage: {
  provider: 'v8',
  reporter: ['text', 'lcov'],
  include: ['src/**/*.{js,jsx}'],
}
```

---

## Key Test Principles

### 1. **Parameterised Queries**

All date parameters are passed as parameterised query arguments, preventing SQL injection:

```python
# ✓ SAFE — parameter substitution
execute_query(conn, "WHERE order_date BETWEEN ? AND ?", (start, end))

# ✗ UNSAFE — string concatenation
execute_query(conn, f"WHERE order_date BETWEEN {start} AND {end}")
```

Tests verify parameterised queries reject injection attempts without crashing.

### 2. **Status Filter**

Only `delivered` and `shipped` orders count toward revenue. `cancelled` and other statuses are excluded.

```python
WHERE status IN ('delivered', 'shipped')
```

Tests seed a `cancelled` order and verify it's excluded from all counts.

### 3. **is_current Filter**

Customer dimension has a `is_current` flag. Only current customers (is_current=1) appear in results.

```python
WHERE c.is_current = 1
```

Seed includes a non-current customer (C003) and verifies it's excluded.

### 4. **BETWEEN Inclusive**

SQLite BETWEEN is inclusive on both boundaries:

```python
WHERE order_date BETWEEN '2022-01-15' AND '2022-01-15'  -- includes exactly one day
```

### 5. **Empty Result Handling**

- Empty date ranges return `[]`, not errors
- Empty database returns `[]` for list endpoints
- Empty database returns `0` (not null) for numeric fields in summary
- SUM() on empty table returns NULL — code coalesces to 0

### 6. **Type Safety**

- Numeric fields (revenue, orders) are always numbers, not strings
- Month format must be YYYY-MM
- Dates must parse sensibly
- Frontend coerces types if needed

---

## CI/CD Integration

### GitHub Actions (`.github/workflows/test.yml`)

```yaml
name: Test

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python -m pytest tests/ -v --tb=short

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm test
```

---

## Best Practices

### ✓ DO

- **Write parametrised tests** — use pytest's `@pytest.mark.parametrize` to test multiple endpoints/conditions with one test
- **Test boundaries** — first day, last day, leap years, inverted ranges
- **Seed realistic data** — include edge cases (cancelled orders, non-current customers)
- **Mock external deps** — use in-memory SQLite, not real databases
- **Test error paths** — 400s, 422s, 503s, etc.
- **Assert specific errors** — "must not crash" isn't enough; assert the right status code
- **Document assumptions** — why does this test expect an empty list vs. a 422?

### ✗ DON'T

- **Skip edge cases** — "nobody will send that" is how bugs happen
- **Test implementation details** — test the contract (what you get), not how it works
- **Ignore NULL values** — aggregates can return NULL; code must coalesce
- **Assume sorting** — always verify ORDER BY is respected
- **Hardcode values** — use fixtures; don't copy-paste test data

---

## Troubleshooting

### Backend Tests Fail with "ModuleNotFoundError"

Install dependencies:
```bash
cd backend
python -m pip install -r requirements.txt
```

### Tests Pass Locally but Fail in CI

- Check Python version (tests assume 3.9+)
- Ensure environment variables are set (`DATA_BACKEND=sqlite`, `CLIENT_VALIDATION=Dev`)
- Verify database seed is created (conftest.py should create in-memory DB)

### Edge Case Test Fails with "AssertionError"

- Check the assertion message — which field/value doesn't match?
- Look at the seed data in `conftest.py` — maybe the expected value is wrong
- Re-run single test with `-vv` for more detail:
  ```bash
  python -m pytest tests/test_edge_cases.py::TestSummaryEndpoint::test_summary_excludes_cancelled_orders -vv
  ```

### Frontend Tests Not Running

- Install Vitest: `npm install --save-dev vitest`
- Check `vite.config.js` includes Vitest config
- Run: `npm test` or `npx vitest`

---

## Future Improvements

1. **Snowflake Integration Tests** — Currently tests use SQLite. Add Snowflake tests using real credentials.
2. **Performance Tests** — Add benchmarks for query execution time with large datasets.
3. **Frontend Component Tests** — Test React components with Vitest + React Testing Library.
4. **Integration Tests** — End-to-end tests with a real frontend + backend.
5. **Load Tests** — Verify API handles concurrent requests.
6. **Security Tests** — Add OWASP Top 10 coverage (CSRF, rate limiting, etc.).

---

## Reference

**Pytest:**
- https://docs.pytest.org/
- https://docs.pytest.org/parametrize
- https://docs.pytest.org/fixtures

**FastAPI Testing:**
- https://fastapi.tiangolo.com/advanced/testing-dependencies/
- https://fastapi.tiangolo.com/tutorial/testing/

**Vitest:**
- https://vitest.dev/
- https://vitest.dev/guide/

**SQL Injection Prevention:**
- https://owasp.org/www-community/attacks/SQL_Injection
- https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html
