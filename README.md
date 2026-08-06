# NovaCart Account Dashboard
### HC&D Associates Capstone — App Developer + App Consultant

React + FastAPI dashboard for the NovaCart account manager. Reads from the Gold data layer produced by the Data Engineering team and surfaces revenue, order, product, and customer insights.

---

## What's in this repo

```
backend/          Python + FastAPI API
  main.py         — 5 franchise endpoints + health + auth
  connection.py   — handles SQLite (local dev) and Snowflake (SPCS) automatically
  requirements.txt
  Dockerfile

frontend/         React 18 frontend
  src/pages/
    OrdersView.jsx    — stat cards + monthly revenue chart + cities chart
    ProductsView.jsx  — products bar chart + products table
    CustomersView.jsx — sortable customers table
    LoginView.jsx     — login + /authorize integration
  src/components/     — Navbar, ServiceStatus
  src/utils/          — api.js, ThemeContext.js
  Dockerfile

router/           NGINX reverse proxy — do not modify
data/
  novacart_gold.db  — SQLite database for local development
                      30,000 orders · 400 customers · 15 products

build-and-push.sh   — Run on Day 4 to deploy to SPCS
```

---

## Quick Start — Local Development

### 1. Backend

```bash
cd backend
cp .env.example .env
# No changes needed — DATA_BACKEND=sqlite works out of the box

pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs** — Swagger UI with all endpoints.

Test the health endpoint:
```bash
curl http://127.0.0.1:8000/health
```

### 2. Frontend

```bash
cd frontend
cp .env.example .env
# VITE_BACKEND_URL=/api  (uses Vite dev proxy — no CORS issues)

npm install
npm start
# Opens at http://127.0.0.1:3000
```

Or run both together from the repo root:
```bash
# macOS
bash startapp.sh

# Windows
startapp.bat
```

---

## API Endpoints

| Endpoint | Description | Params | Status codes |
|---|---|---|---|
| `GET /health` | Service health and DB connectivity | — | 200, 503 |
| `GET /authorize` | SPCS OAuth — returns authenticated username | — | 200, 401 |
| `GET /franchise/summary` | Total revenue, orders, unique customers, date range | `start`, `end` (optional) | 200, 404, 422, 503 |
| `GET /franchise/orders` | Monthly order volume and revenue | `start`, `end` | 200, 422, 503 |
| `GET /franchise/products` | Top 10 products by revenue | `start`, `end` | 200, 422, 503 |
| `GET /franchise/customers` | Top 20 customers by total spend | `start`, `end` | 200, 422, 503 |
| `GET /franchise/cities` | Revenue by city and state | `start`, `end` | 200, 422, 503 |

Date parameters use format `YYYY-MM-DD`. Default range for all franchise endpoints: `2022-01-01` – `2022-12-31`.
Revenue figures count only `status IN ('delivered', 'shipped')` — cancelled orders are excluded.

---

## Data Schema

The SQLite database has four tables matching the Gold layer from the Data Engineering capstone:

```
fact_orders    order_id, customer_id, product_id, order_date, amount,
               currency, status, quantity, date_key

dim_customer   customer_id, name, email, signup_date,
               addr_street, addr_city, addr_state, addr_zip,
               valid_from, valid_to, is_current

dim_product    product_id, name, category, price, updated_at

dim_date       date_key, full_date, year, quarter, month,
               month_name, day_of_week, is_weekend
```

Revenue calculations use `status IN ('delivered', 'shipped')`.
All customer geography is US-only (city + state, no country field).

---

## Deploying to SPCS

```bash
export REPO_URL=<provided by your facilitator>
export GROUP=<your team number>

bash build-and-push.sh
```

Then notify your facilitator — they will deploy your services and give you the public URL.

The Dockerfile defaults `CLIENT_VALIDATION=Prod`. The `auto-deploy.yml` workflow overrides this with `CLIENT_VALIDATION=Snowflake` in the service spec, which activates SPCS OAuth on deployment.

---

## Troubleshooting

**Backend can't find the database** — Run `uvicorn` from inside the `backend/` directory, or use `startapp.bat` / `startapp.sh`.

**CORS error in browser** — Make sure `CLIENT_VALIDATION=Dev` in your backend `.env` and `VITE_BACKEND_URL=/api` in your frontend `.env`.

**`snow` command not found** — Run:
```bash
pip3 install snowflake-cli-labs
```
Then open a new terminal (Snowflake CLI adds itself to PATH on first install).

**Docker build fails** — Run with `--no-cache`:
```bash
docker build --no-cache --platform linux/amd64 ...
```
