/**
 * api.test.js — Unit tests for the NovaCart API client (src/utils/api.jsx).
 *
 * Strategy: stub the global fetch with vi.stubGlobal so no real network
 * requests are made. Each test restores the stub after the assertion.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  authorize,
  getHealth,
  getSummary,
  getOrders,
  getProducts,
  getCustomers,
  getCities,
} from './api';

// ── helpers ──────────────────────────────────────────────────────────────────

/** Build a minimal Response-like object that fetch resolves with. */
function mockFetch(body, status = 200) {
  const jsonBody = JSON.stringify(body);
  vi.stubGlobal('fetch', vi.fn(() =>
    Promise.resolve({
      ok:     status >= 200 && status < 300,
      status,
      json:   () => Promise.resolve(body),
      statusText: 'Bad Request',
    })
  ));
}

function mockFetchError(status, detail) {
  vi.stubGlobal('fetch', vi.fn(() =>
    Promise.resolve({
      ok:     false,
      status,
      json:   () => Promise.resolve(detail ? { detail } : {}),
      statusText: 'Server Error',
    })
  ));
}

afterEach(() => {
  vi.unstubAllGlobals();
});

// ── URL routing ───────────────────────────────────────────────────────────────

describe('URL routing', () => {
  it('calls the correct URL for authorize', async () => {
    mockFetch({ user: 'dev_user', status: 'authorized' });
    await authorize();
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/authorize'),
      expect.any(Object)
    );
  });

  it('calls the correct URL for health', async () => {
    mockFetch({ status: 'healthy' });
    await getHealth();
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/health'),
      expect.any(Object)
    );
  });

  it('calls the correct URL for summary', async () => {
    mockFetch({ total_revenue: 0, total_orders: 0, unique_customers: 0, date_range: {} });
    await getSummary();
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/franchise/summary'),
      expect.any(Object)
    );
  });

  it('getOrders includes start and end query params', async () => {
    mockFetch([]);
    await getOrders('2022-01-01', '2022-12-31');
    const url = fetch.mock.calls[0][0];
    expect(url).toContain('start=2022-01-01');
    expect(url).toContain('end=2022-12-31');
  });

  it('getProducts includes start and end query params', async () => {
    mockFetch([]);
    await getProducts('2022-03-01', '2022-03-31');
    const url = fetch.mock.calls[0][0];
    expect(url).toContain('start=2022-03-01');
    expect(url).toContain('end=2022-03-31');
  });

  it('getCustomers includes start and end query params', async () => {
    mockFetch([]);
    await getCustomers('2022-06-01', '2022-06-30');
    const url = fetch.mock.calls[0][0];
    expect(url).toContain('start=2022-06-01');
    expect(url).toContain('end=2022-06-30');
  });

  it('getCities includes start and end query params', async () => {
    mockFetch([]);
    await getCities('2022-01-01', '2022-06-30');
    const url = fetch.mock.calls[0][0];
    expect(url).toContain('start=2022-01-01');
    expect(url).toContain('end=2022-06-30');
  });
});

// ── Response parsing ──────────────────────────────────────────────────────────

describe('Response parsing', () => {
  it('returns parsed JSON on a successful call', async () => {
    const payload = { total_revenue: 9999.99, total_orders: 100, unique_customers: 50, date_range: {} };
    mockFetch(payload);
    const result = await getSummary();
    expect(result).toEqual(payload);
  });

  it('throws with the detail string on a non-ok response', async () => {
    mockFetchError(422, 'Missing Sf-Context-Current-User header');
    await expect(authorize()).rejects.toThrow('Missing Sf-Context-Current-User header');
  });

  it('throws a fallback message when no detail is present', async () => {
    mockFetchError(500, null);
    await expect(getSummary()).rejects.toThrow('API error 500');
  });
});

// ── Cache modes ───────────────────────────────────────────────────────────────

describe('Cache modes', () => {
  it('uses no-cache for data endpoints (getSummary)', async () => {
    mockFetch({});
    await getSummary();
    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      { cache: 'no-cache' }
    );
  });

  it('uses default cache for static endpoints (getHealth)', async () => {
    mockFetch({ status: 'healthy' });
    await getHealth();
    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      { cache: 'default' }
    );
  });

  it('uses default cache for authorize', async () => {
    mockFetch({ user: 'dev_user', status: 'authorized' });
    await authorize();
    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      { cache: 'default' }
    );
  });
});

// ── Base URL ──────────────────────────────────────────────────────────────────

describe('Base URL', () => {
  it('falls back to /api when VITE_BACKEND_URL is not set', async () => {
    mockFetch({});
    await getSummary();
    const url = fetch.mock.calls[0][0];
    // In the test environment import.meta.env.VITE_BACKEND_URL is undefined
    expect(url).toMatch(/^\/api\//);
  });
});
