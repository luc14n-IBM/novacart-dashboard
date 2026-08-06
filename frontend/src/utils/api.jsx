/**
 * api.jsx — NovaCart Dashboard API client
 *
 * All API calls go through this module.
 *
 * Base URL resolution (VITE_BACKEND_URL env var):
 *   Local dev  — set to /api in .env; Vite dev-server proxies /api → http://127.0.0.1:8000
 *   SPCS       — set to /api at build time; NGINX router strips the prefix and
 *                forwards to the backend container on localhost:8000
 *
 * Cache strategy:
 *   Data endpoints (summary, orders, products, customers, cities) — 'no-cache':
 *     always revalidate so filter changes are reflected immediately.
 *   Static endpoints (health, authorize) — 'default':
 *     may be served from browser cache between navigations.
 *
 * Error handling:
 *   Non-2xx responses throw an Error whose message is the FastAPI `detail`
 *   string, or "API error <status>" when no detail is present.
 */

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || '/api';

// Default fetch — always revalidates with the server before using a cached response.
// Static endpoints (health, authorize) use the browser default and may be cached freely.
async function apiFetch(path, cache = 'no-cache') {
  const res = await fetch(`${BACKEND_URL}${path}`, { cache });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
}

export async function authorize()       { return apiFetch('/authorize', 'default'); }
export async function getHealth()       { return apiFetch('/health',    'default'); }
export async function getSummary(s, e)  { return apiFetch(`/franchise/summary?start=${s}&end=${e}`); }
export async function getOrders(s, e)   { return apiFetch(`/franchise/orders?start=${s}&end=${e}`); }
export async function getProducts(s, e) { return apiFetch(`/franchise/products?start=${s}&end=${e}`); }
export async function getCustomers(s,e) { return apiFetch(`/franchise/customers?start=${s}&end=${e}`); }
export async function getCities(s, e)   { return apiFetch(`/franchise/cities?start=${s}&end=${e}`); }
