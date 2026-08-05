/**
 * api.js — NovaCart Dashboard API client
 *
 * All API calls go through this file.
 * In SPCS, REACT_APP_BACKEND_URL is set to /api and calls are
 * routed through the NGINX router to the backend container.
 * Locally, calls go directly to http://localhost:8000.
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
