"""
main.py — NovaCart Account Dashboard API

Built with FastAPI.
  Local dev docs:  http://127.0.0.1:8000/docs   (Swagger UI)
  Local dev docs:  http://127.0.0.1:8000/redoc  (ReDoc)

Endpoints:
  GET /health                   — service health check and DB connectivity
  GET /authorize                — SPCS OAuth: reads Sf-Context-Current-User header
  GET /franchise/summary        — overview stats (revenue, orders, customers, date range)
  GET /franchise/orders         — monthly order volume and revenue
  GET /franchise/products       — top 10 products by revenue
  GET /franchise/customers      — top 20 customers by revenue
  GET /franchise/cities         — revenue by city/state

All franchise endpoints accept optional ?start=YYYY-MM-DD&end=YYYY-MM-DD query params.
Default date range when omitted: 2022-01-01 – 2022-12-31.
Revenue counts only status IN ('delivered', 'shipped'); 'cancelled' is excluded.

Data schema (from the DE capstone Gold layer):
  fact_orders:   order_id, customer_id, product_id, order_date, amount, currency, status, quantity, date_key
  dim_customer:  customer_id, name, email, addr_city, addr_state, valid_from, valid_to, is_current
  dim_product:   product_id, name, category, price
  dim_date:      date_key, year, quarter, month, month_name, day_of_week

The connection and query helpers are in connection.py.

Notes:
  - Franchise ID scoping was removed from all endpoints. The original design
    specified /franchise/{id}/* routes, but the current implementation returns
    data across the full dataset with no per-franchise filtering. If multi-
    franchise scoping is required in future, a franchise_id path parameter and
    corresponding fact_orders filter will need to be added.
  - All customer geography (addr_city, addr_state) is assumed to be United States
    data. City/state labels are displayed without country context and the /cities
    endpoint groups by city and state accordingly.
  - CLIENT_VALIDATION env var controls auth and CORS behaviour:
      'Dev'       — mock auth (returns dev_user), CORS enabled for localhost:3000
      'Snowflake' — real SPCS OAuth header auth, no CORS middleware (NGINX handles routing)
"""

import os
import time
from datetime import date as _date
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

import connection as _conn_module

load_dotenv()


def _validate_date(value: str) -> _date:
    """
    Parse and validate a YYYY-MM-DD date string.
    Raises HTTPException(422) for any value that is not a valid ISO date.
    """
    try:
        return _date.fromisoformat(value)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format '{value}'. Expected YYYY-MM-DD.",
        )


# ── App setup ─────────────────────────────────────────────────────────────────

PORT              = int(os.getenv("PORT", 8000))
CLIENT_VALIDATION = os.getenv("CLIENT_VALIDATION", "Dev")
START_TIME        = time.time()


# Replaces the deprecated @app.on_event("startup") pattern
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\nStarting NovaCart Dashboard API")
    print(f"Port:            {PORT}")
    print(f"Data backend:    {os.getenv('DATA_BACKEND', 'sqlite')}")
    print(f"Validation mode: {CLIENT_VALIDATION}")
    print(f"Docs:            http://localhost:{PORT}/docs\n")
    yield  # application runs here


_TAG_METADATA = [
    {
        "name": "System",
        "description": "Health check and uptime. Used by the frontend service status indicator.",
    },
    {
        "name": "Auth",
        "description": (
            "SPCS OAuth authorization. In Dev mode returns a mock user; "
            "in Snowflake mode reads the `Sf-Context-Current-User` header injected by SPCS."
        ),
    },
    {
        "name": "Franchise",
        "description": (
            "Sales analytics endpoints. All accept optional `start`/`end` date filters "
            "(YYYY-MM-DD). Default range: 2022-01-01 – 2022-12-31. "
            "Revenue figures include only `delivered` and `shipped` orders."
        ),
    },
]

app = FastAPI(
    title="NovaCart Account Dashboard API",
    description=(
        "REST API for the NovaCart account manager dashboard. "
        "Built on top of the Gold data layer produced by the Data Engineering team.\n\n"
        "**Authentication:** In local dev (`CLIENT_VALIDATION=Dev`) all endpoints are open. "
        "In SPCS (`CLIENT_VALIDATION=Snowflake`) the platform injects the authenticated "
        "Snowflake username via the `Sf-Context-Current-User` header.\n\n"
        "**Data backend:** `DATA_BACKEND=sqlite` for local development; "
        "`DATA_BACKEND=snowflake` for SPCS deployment."
    ),
    version="1.0.0",
    openapi_tags=_TAG_METADATA,
    lifespan=lifespan,
)

# CORS — only needed for local development
# In SPCS, the NGINX router handles routing so CORS is not required
if CLIENT_VALIDATION == "Dev":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )


# ── Health ────────────────────────────────────────────────────────────────────

@app.get(
    "/health",
    tags=["System"],
    summary="Service health check",
    responses={
        200: {"description": "Service is healthy and database is reachable."},
        503: {"description": "Database connection failed — service is degraded."},
    },
)
def health():
    """
    Returns service health and confirms the database connection is working.
    Used by the frontend `ServiceStatus` component.

    **Response (healthy):**
    ```json
    {
        "status":   "healthy",
        "uptime_s": 142,
        "backend":  "sqlite",
        "database": { "status": "connected" }
    }
    ```

    **Response (degraded — HTTP 503):**
    ```json
    {
        "status":   "degraded",
        "uptime_s": 5,
        "database": { "status": "error", "message": "Database connection failed" }
    }
    ```
    """
    uptime = round(time.time() - START_TIME)
    try:
        conn    = _conn_module.get_connection()
        results = _conn_module.execute_query(conn, "SELECT 1 AS ping")
        assert len(results) > 0
    except Exception:
        return JSONResponse(status_code=503, content={
            "status":   "degraded",
            "uptime_s": uptime,
            "database": {"status": "error", "message": "Database connection failed"},
        })
    return {
        "status":   "healthy",
        "uptime_s": uptime,
        "backend":  os.getenv("DATA_BACKEND", "sqlite"),
        "database": {"status": "connected"},
    }


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.get(
    "/authorize",
    tags=["Auth"],
    summary="Authenticate the current user",
    responses={
        200: {"description": "User identity returned successfully."},
        401: {"description": "SPCS mode only — `Sf-Context-Current-User` header missing."},
    },
)
def authorize(request: Request):
    """
    Returns the authenticated user's identity.

    **Dev mode** (`CLIENT_VALIDATION=Dev`): returns a mock user without
    inspecting any headers — no authentication required.

    **Snowflake / SPCS mode** (`CLIENT_VALIDATION=Snowflake`): the SPCS platform
    injects the Snowflake username in the `Sf-Context-Current-User` request header.
    This endpoint reads that header and returns it. If the header is absent the
    request is rejected with HTTP 401.

    **Response:**
    ```json
    { "user": "ALICE.SMITH", "status": "authorized" }
    ```

    **Error (HTTP 401 — SPCS mode, header missing):**
    ```json
    { "detail": "Missing Sf-Context-Current-User header" }
    ```
    """
    if CLIENT_VALIDATION == "Dev":
        return {"user": "dev_user", "status": "authorized"}

    username = request.headers.get("sf-context-current-user")
    if not username:
        raise HTTPException(status_code=401, detail="Missing Sf-Context-Current-User header")

    return {"user": username, "status": "authorized"}


# ── Franchise endpoints ───────────────────────────────────────────────────────

@app.get(
    "/franchise/summary",
    tags=["Franchise"],
    summary="Overview stats — revenue, orders, customers",
    responses={
        200: {"description": "Aggregated totals for the requested period."},
        404: {"description": "No delivered/shipped orders found for the given date range."},
        422: {"description": "One or more date parameters are not valid ISO 8601 dates."},
        503: {"description": "Database error."},
    },
)
def get_summary(start: str | None = None, end: str | None = None):
    """
    Returns aggregated totals across all delivered and shipped orders.

    **Query parameters (all optional):**

    | Parameter | Type   | Default | Description                    |
    |-----------|--------|---------|--------------------------------|
    | `start`   | string | —       | Start date, inclusive (YYYY-MM-DD) |
    | `end`     | string | —       | End date, inclusive (YYYY-MM-DD)   |

    When neither `start` nor `end` is supplied the query runs across the full
    dataset. When only one is supplied it is ignored and the unfiltered query
    is used.

    **Response (HTTP 200):**
    ```json
    {
        "total_revenue":    1284750.00,
        "total_orders":     8432,
        "unique_customers": 380,
        "date_range": { "start": "2022-01-01", "end": "2022-12-31" }
    }
    ```

    **Error (HTTP 404):** No qualifying orders found for the given range.

    **Error (HTTP 422):** Invalid date format — `{ "detail": "Invalid date format '...' . Expected YYYY-MM-DD." }`

    **Error (HTTP 503):** Database unreachable or query failed.
    """
    try:
        conn = _conn_module.get_connection()

        if start and end:
            results = _conn_module.execute_query(conn, """
                SELECT
                    COUNT(DISTINCT order_id)    AS total_orders,
                    SUM(amount)                 AS total_revenue,
                    COUNT(DISTINCT customer_id) AS unique_customers,
                    MIN(order_date)             AS start_date,
                    MAX(order_date)             AS end_date
                FROM fact_orders
                WHERE status IN ('delivered', 'shipped')
                  AND order_date BETWEEN ? AND ?
            """, (start, end))
        else:
            results = _conn_module.execute_query(conn, """
                SELECT
                    COUNT(DISTINCT order_id)    AS total_orders,
                    SUM(amount)                 AS total_revenue,
                    COUNT(DISTINCT customer_id) AS unique_customers,
                    MIN(order_date)             AS start_date,
                    MAX(order_date)             AS end_date
                FROM fact_orders
                WHERE status IN ('delivered', 'shipped')
            """)

        row = results[0]
        if row["total_orders"] is None or row["total_orders"] == 0:
            raise HTTPException(status_code=404, detail="No data found for the given date range")
        return {
            "total_revenue":    round(row["total_revenue"] or 0, 2),
            "total_orders":     row["total_orders"],
            "unique_customers": row["unique_customers"],
            "date_range": {"start": row["start_date"], "end": row["end_date"]},
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Internal server error")


@app.get(
    "/franchise/orders",
    tags=["Franchise"],
    summary="Monthly order volume and revenue",
    responses={
        200: {"description": "List of monthly order aggregates, sorted chronologically."},
        422: {"description": "One or more date parameters are not valid ISO 8601 dates."},
        503: {"description": "Database error."},
    },
)
def get_orders(start: str = "2022-01-01", end: str = "2022-12-31"):
    """
    Returns monthly order volume and revenue for the given date range.
    Used to power the monthly revenue chart in the Orders view.

    **Query parameters:**

    | Parameter | Type   | Default      | Description                    |
    |-----------|--------|--------------|--------------------------------|
    | `start`   | string | `2022-01-01` | Start date, inclusive (YYYY-MM-DD) |
    | `end`     | string | `2022-12-31` | End date, inclusive (YYYY-MM-DD)   |

    **Response (HTTP 200):** Array sorted chronologically by year and month.
    Returns `[]` when no qualifying orders exist in the range.
    ```json
    [
        { "month": "2022-01", "month_name": "January",  "order_count": 842, "revenue": 128450.00 },
        { "month": "2022-02", "month_name": "February", "order_count": 910, "revenue": 141230.00 }
    ]
    ```

    **Error (HTTP 422):** Invalid date — `{ "detail": "Invalid date format '...'. Expected YYYY-MM-DD." }`

    **Error (HTTP 503):** Database unreachable or query failed.
    """
    try:
        _validate_date(start)
        _validate_date(end)
        conn = _conn_module.get_connection()

        results = _conn_module.execute_query(conn, """
        SELECT
            d.year || '-' || SUBSTR('0' || CAST(d.month AS TEXT), -2) AS month,
            d.month_name,
            COUNT(DISTINCT o.order_id)               AS order_count,
            ROUND(SUM(o.amount), 2)                  AS revenue
        FROM fact_orders o
        JOIN dim_date d ON o.date_key = d.date_key
        WHERE o.order_date BETWEEN ? AND ?
          AND o.status IN ('delivered', 'shipped')
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month
        """, (start, end))

        return results or []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Internal server error")


@app.get(
    "/franchise/products",
    tags=["Franchise"],
    summary="Top 10 products by revenue",
    responses={
        200: {"description": "Up to 10 products ranked by revenue descending."},
        422: {"description": "One or more date parameters are not valid ISO 8601 dates."},
        503: {"description": "Database error."},
    },
)
def get_products(start: str = "2022-01-01", end: str = "2022-12-31"):
    """
    Returns the top 10 products by revenue for the given date range,
    ordered by revenue descending. Only `delivered` and `shipped` orders count.

    **Query parameters:**

    | Parameter | Type   | Default      | Description                    |
    |-----------|--------|--------------|--------------------------------|
    | `start`   | string | `2022-01-01` | Start date, inclusive (YYYY-MM-DD) |
    | `end`     | string | `2022-12-31` | End date, inclusive (YYYY-MM-DD)   |

    **Response (HTTP 200):** Array of up to 10 items, revenue descending.
    Returns `[]` when no qualifying orders exist in the range.
    ```json
    [
        {
            "product_id": "P001",
            "name":        "Wireless Headphones",
            "category":    "Electronics",
            "units_sold":  342,
            "revenue":     30578.58
        }
    ]
    ```

    **Error (HTTP 422):** Invalid date — `{ "detail": "Invalid date format '...'. Expected YYYY-MM-DD." }`

    **Error (HTTP 503):** Database unreachable or query failed.
    """
    try:
        _validate_date(start)
        _validate_date(end)
        conn = _conn_module.get_connection()

        results = _conn_module.execute_query(conn, """
        SELECT
            o.product_id,
            p.name,
            p.category,
            SUM(o.quantity)     AS units_sold,
            ROUND(SUM(o.amount), 2) AS revenue
        FROM fact_orders o
        JOIN dim_product p ON o.product_id = p.product_id
        WHERE o.order_date BETWEEN ? AND ?
          AND o.status IN ('delivered', 'shipped')
        GROUP BY o.product_id, p.name, p.category
        ORDER BY revenue DESC
        LIMIT 10
        """, (start, end))

        return results or []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Internal server error")


@app.get(
    "/franchise/customers",
    tags=["Franchise"],
    summary="Top 20 customers by total spend",
    responses={
        200: {"description": "Up to 20 current customers ranked by total spend descending."},
        422: {"description": "One or more date parameters are not valid ISO 8601 dates."},
        503: {"description": "Database error."},
    },
)
def get_customers(start: str = "2022-01-01", end: str = "2022-12-31"):
    """
    Returns the top 20 customers by total spend for the given date range,
    ordered by `total_spent` descending. Only current customers
    (`is_current = 1` in `dim_customer`) are included.

    **Query parameters:**

    | Parameter | Type   | Default      | Description                    |
    |-----------|--------|--------------|--------------------------------|
    | `start`   | string | `2022-01-01` | Start date, inclusive (YYYY-MM-DD) |
    | `end`     | string | `2022-12-31` | End date, inclusive (YYYY-MM-DD)   |

    **Response (HTTP 200):** Array of up to 20 items, `total_spent` descending.
    Returns `[]` when no qualifying orders exist in the range.
    ```json
    [
        {
            "customer_id":  "C001",
            "name":         "Alice Johnson",
            "city":         "Austin",
            "state":        "TX",
            "total_orders": 14,
            "total_spent":  1240.50
        }
    ]
    ```

    **Error (HTTP 422):** Invalid date — `{ "detail": "Invalid date format '...'. Expected YYYY-MM-DD." }`

    **Error (HTTP 503):** Database unreachable or query failed.
    """
    try:
        _validate_date(start)
        _validate_date(end)
        conn = _conn_module.get_connection()

        results = _conn_module.execute_query(conn, """
        SELECT
            o.customer_id,
            c.name,
            c.addr_city             AS city,
            c.addr_state            AS state,
            COUNT(DISTINCT o.order_id)  AS total_orders,
            ROUND(SUM(o.amount), 2)     AS total_spent
        FROM fact_orders o
        JOIN dim_customer c ON o.customer_id = c.customer_id
        WHERE c.is_current = 1
          AND o.order_date BETWEEN ? AND ?
          AND o.status IN ('delivered', 'shipped')
        GROUP BY o.customer_id, c.name, c.addr_city, c.addr_state
        ORDER BY total_spent DESC
        LIMIT 20
        """, (start, end))

        return results or []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Internal server error")


@app.get(
    "/franchise/cities",
    tags=["Franchise"],
    summary="Revenue by city and state",
    responses={
        200: {"description": "Cities ranked by revenue descending."},
        422: {"description": "One or more date parameters are not valid ISO 8601 dates."},
        503: {"description": "Database error."},
    },
)
def get_cities(start: str = "2022-01-01", end: str = "2022-12-31"):
    """
    Returns revenue grouped by city and state, ordered by revenue descending.
    Used to power the geographic breakdown chart in the Orders view.
    Only current customers (`is_current = 1`) are included.
    All geography is US-only (city + state, no country field).

    **Query parameters:**

    | Parameter | Type   | Default      | Description                    |
    |-----------|--------|--------------|--------------------------------|
    | `start`   | string | `2022-01-01` | Start date, inclusive (YYYY-MM-DD) |
    | `end`     | string | `2022-12-31` | End date, inclusive (YYYY-MM-DD)   |

    **Response (HTTP 200):** Array of all qualifying cities, revenue descending.
    Returns `[]` when no qualifying orders exist in the range.
    ```json
    [
        { "city": "Austin", "state": "TX", "order_count": 420, "revenue": 38430.00 }
    ]
    ```

    **Error (HTTP 422):** Invalid date — `{ "detail": "Invalid date format '...'. Expected YYYY-MM-DD." }`

    **Error (HTTP 503):** Database unreachable or query failed.
    """
    try:
        _validate_date(start)
        _validate_date(end)
        conn = _conn_module.get_connection()

        results = _conn_module.execute_query(conn, """
        SELECT
            c.addr_city                 AS city,
            c.addr_state                AS state,
            COUNT(DISTINCT o.order_id)  AS order_count,
            ROUND(SUM(o.amount), 2)     AS revenue
        FROM fact_orders o
        JOIN dim_customer c ON o.customer_id = c.customer_id
        WHERE c.is_current = 1
          AND o.order_date BETWEEN ? AND ?
          AND o.status IN ('delivered', 'shipped')
        GROUP BY c.addr_city, c.addr_state
        ORDER BY revenue DESC
        """, (start, end))

        return results or []
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail="Internal server error")
