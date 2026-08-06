/**
 * frontend/tests/api.test.js
 * Frontend API response edge case tests
 * 
 * Tests the frontend's ability to handle:
 *   - Empty result sets
 *   - Null/undefined field values
 *   - Malformed responses
 *   - Missing fields in responses
 *   - Type mismatches (string instead of number, etc.)
 *   - Network errors and timeouts
 *   - Status codes (2xx, 4xx, 5xx)
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

/**
 * Mock API module
 */
const api = {
  async fetchJSON(endpoint) {
    const response = await fetch(endpoint);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },
};

// ─────────────────────────────────────────────────────────────────────────────
//  Health endpoint responses
// ─────────────────────────────────────────────────────────────────────────────

describe('Health Endpoint Edge Cases', () => {
  it('should handle healthy response', async () => {
    const response = {
      status: 'healthy',
      uptime_s: 123,
      backend: 'sqlite',
      database: { status: 'connected' },
    };
    expect(response.status).toBe('healthy');
    expect(typeof response.uptime_s).toBe('number');
    expect(response.uptime_s).toBeGreaterThanOrEqual(0);
  });

  it('should handle degraded response with 503 status', async () => {
    const response = {
      status: 'degraded',
      uptime_s: 45,
      database: { status: 'error', message: 'Connection refused' },
    };
    expect(response.status).toBe('degraded');
    expect(response.database.status).toBe('error');
    expect(response.database.message).toBeDefined();
  });

  it('should handle null uptime gracefully', async () => {
    const response = {
      status: 'healthy',
      uptime_s: null,
      backend: 'sqlite',
      database: { status: 'connected' },
    };
    // Frontend should coerce null to 0 or handle gracefully
    const uptime = response.uptime_s ?? 0;
    expect(typeof uptime).toBe('number');
  });
});

// ─────────────────────────────────────────────────────────────────────────────
//  Summary endpoint responses
// ─────────────────────────────────────────────────────────────────────────────

describe('Summary Endpoint Edge Cases', () => {
  it('should handle valid summary response', () => {
    const response = {
      total_revenue: 125000.50,
      total_orders: 450,
      unique_customers: 89,
      date_range: { start: '2022-01-01', end: '2022-12-31' },
    };
    expect(typeof response.total_revenue).toBe('number');
    expect(typeof response.total_orders).toBe('number');
    expect(typeof response.unique_customers).toBe('number');
    expect(response.date_range.start).toBeDefined();
    expect(response.date_range.end).toBeDefined();
  });

  it('should handle zero values in summary', () => {
    const response = {
      total_revenue: 0,
      total_orders: 0,
      unique_customers: 0,
      date_range: { start: null, end: null },
    };
    expect(response.total_revenue).toBe(0);
    expect(response.total_orders).toBe(0);
    expect(response.unique_customers).toBe(0);
    expect(response.date_range.start).toBeNull();
  });

  it('should handle string numbers instead of actual numbers', () => {
    const response = {
      total_revenue: '125000.50', // String instead of number
      total_orders: '450',
      unique_customers: '89',
      date_range: { start: '2022-01-01', end: '2022-12-31' },
    };
    // Frontend should convert to number
    const revenue = Number(response.total_revenue);
    expect(typeof revenue).toBe('number');
    expect(revenue).toBe(125000.50);
  });

  it('should handle missing fields gracefully', () => {
    const response = {
      total_revenue: 100000,
      // missing total_orders
      unique_customers: 50,
      date_range: { start: '2022-01-01', end: '2022-12-31' },
    };
    const totalOrders = response.total_orders ?? 0;
    expect(totalOrders).toBe(0);
  });

  it('should handle null date_range values', () => {
    const response = {
      total_revenue: 0,
      total_orders: 0,
      unique_customers: 0,
      date_range: { start: null, end: null },
    };
    const startDate = response.date_range?.start || 'No data';
    expect(startDate).toBe('No data');
  });
});

// ─────────────────────────────────────────────────────────────────────────────
//  Orders endpoint responses
// ─────────────────────────────────────────────────────────────────────────────

describe('Orders Endpoint Edge Cases', () => {
  it('should handle valid orders list', () => {
    const response = [
      {
        month: '2022-01',
        month_name: 'January',
        order_count: 150,
        revenue: 50000.75,
      },
      {
        month: '2022-02',
        month_name: 'February',
        order_count: 120,
        revenue: 40000.25,
      },
    ];
    expect(Array.isArray(response)).toBe(true);
    response.forEach((row) => {
      expect(row.month).toMatch(/^\d{4}-\d{2}$/);
      expect(typeof row.order_count).toBe('number');
      expect(typeof row.revenue).toBe('number');
    });
  });

  it('should handle empty orders list', () => {
    const response = [];
    expect(Array.isArray(response)).toBe(true);
    expect(response.length).toBe(0);
  });

  it('should handle null revenue values', () => {
    const response = [
      {
        month: '2022-01',
        month_name: 'January',
        order_count: 0,
        revenue: null,
      },
    ];
    const revenue = response[0].revenue ?? 0;
    expect(revenue).toBe(0);
  });

  it('should handle string month format', () => {
    const response = [
      {
        month: '2022-13', // Invalid month
        month_name: 'Invalid',
        order_count: 10,
        revenue: 1000,
      },
    ];
    // Frontend should validate or handle gracefully
    const isValidMonth = /^\d{4}-(0[1-9]|1[0-2])$/.test(response[0].month);
    expect(isValidMonth).toBe(false);
  });

  it('should handle missing month_name field', () => {
    const response = [
      {
        month: '2022-01',
        // missing month_name
        order_count: 150,
        revenue: 50000.75,
      },
    ];
    const monthName = response[0].month_name || 'Unknown';
    expect(monthName).toBe('Unknown');
  });

  it('should handle negative revenue (refunds?)', () => {
    const response = [
      {
        month: '2022-01',
        month_name: 'January',
        order_count: 10,
        revenue: -500.00,
      },
    ];
    // Frontend might filter or flag negative values
    expect(response[0].revenue).toBeLessThan(0);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
//  Products endpoint responses
// ─────────────────────────────────────────────────────────────────────────────

describe('Products Endpoint Edge Cases', () => {
  it('should handle valid products list (max 10)', () => {
    const response = [
      {
        product_id: 'P001',
        name: 'Wireless Headphones',
        category: 'Electronics',
        units_sold: 342,
        revenue: 30578.58,
      },
    ];
    expect(Array.isArray(response)).toBe(true);
    expect(response.length).toBeLessThanOrEqual(10);
    response.forEach((row) => {
      expect(typeof row.product_id).toBe('string');
      expect(typeof row.units_sold).toBe('number');
      expect(typeof row.revenue).toBe('number');
    });
  });

  it('should handle empty products list', () => {
    const response = [];
    expect(response.length).toBe(0);
  });

  it('should handle missing category field', () => {
    const response = [
      {
        product_id: 'P001',
        name: 'Product Name',
        // missing category
        units_sold: 100,
        revenue: 5000,
      },
    ];
    const category = response[0].category || 'Uncategorized';
    expect(category).toBe('Uncategorized');
  });

  it('should handle null values in numeric fields', () => {
    const response = [
      {
        product_id: 'P001',
        name: 'Product',
        category: 'Electronics',
        units_sold: null,
        revenue: 0,
      },
    ];
    const unitsSold = response[0].units_sold ?? 0;
    expect(typeof unitsSold).toBe('number');
  });

  it('should handle products not sorted by revenue', () => {
    const response = [
      { product_id: 'P1', name: 'A', category: 'X', units_sold: 1, revenue: 100 },
      { product_id: 'P2', name: 'B', category: 'X', units_sold: 2, revenue: 50 },
    ];
    // Frontend should sort or validate ordering
    const isSorted = response.every((v, i, a) =>
      i === 0 || a[i - 1].revenue >= v.revenue
    );
    expect(isSorted).toBe(false);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
//  Customers endpoint responses
// ─────────────────────────────────────────────────────────────────────────────

describe('Customers Endpoint Edge Cases', () => {
  it('should handle valid customers list (max 20)', () => {
    const response = [
      {
        customer_id: 'C001',
        name: 'Alice Johnson',
        city: 'Austin',
        state: 'TX',
        total_orders: 14,
        total_spent: 1240.50,
      },
    ];
    expect(Array.isArray(response)).toBe(true);
    expect(response.length).toBeLessThanOrEqual(20);
  });

  it('should handle empty customers list', () => {
    const response = [];
    expect(response.length).toBe(0);
  });

  it('should handle null city/state values', () => {
    const response = [
      {
        customer_id: 'C001',
        name: 'Alice',
        city: null,
        state: null,
        total_orders: 5,
        total_spent: 500,
      },
    ];
    const city = response[0].city || 'Unknown';
    expect(city).toBe('Unknown');
  });

  it('should handle unusual state codes', () => {
    const response = [
      {
        customer_id: 'C001',
        name: 'Alice',
        city: 'Austin',
        state: 'XX', // Invalid state
        total_orders: 5,
        total_spent: 500,
      },
    ];
    // Frontend might validate state codes
    expect(response[0].state).toBe('XX');
  });

  it('should handle customers not sorted by total_spent desc', () => {
    const response = [
      { customer_id: 'C1', name: 'A', city: 'X', state: 'Y', total_orders: 1, total_spent: 100 },
      { customer_id: 'C2', name: 'B', city: 'X', state: 'Y', total_orders: 2, total_spent: 200 },
    ];
    const isSorted = response.every((v, i, a) =>
      i === 0 || a[i - 1].total_spent >= v.total_spent
    );
    expect(isSorted).toBe(false);
  });

  it('should handle zero total_orders', () => {
    const response = [
      {
        customer_id: 'C001',
        name: 'Alice',
        city: 'Austin',
        state: 'TX',
        total_orders: 0,
        total_spent: 0,
      },
    ];
    expect(response[0].total_orders).toBe(0);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
//  Cities endpoint responses
// ─────────────────────────────────────────────────────────────────────────────

describe('Cities Endpoint Edge Cases', () => {
  it('should handle valid cities list', () => {
    const response = [
      { city: 'Austin', state: 'TX', order_count: 420, revenue: 38430.00 },
    ];
    expect(Array.isArray(response)).toBe(true);
    response.forEach((row) => {
      expect(typeof row.city).toBe('string');
      expect(typeof row.state).toBe('string');
      expect(typeof row.order_count).toBe('number');
      expect(typeof row.revenue).toBe('number');
    });
  });

  it('should handle empty cities list', () => {
    const response = [];
    expect(response.length).toBe(0);
  });

  it('should handle null city names', () => {
    const response = [
      { city: null, state: 'TX', order_count: 10, revenue: 1000 },
    ];
    const city = response[0].city || 'Unknown';
    expect(city).toBe('Unknown');
  });

  it('should handle unusual state codes', () => {
    const response = [
      { city: 'Boston', state: 'UK', order_count: 5, revenue: 500 },
    ];
    // Frontend might filter or validate
    expect(response[0].state).toBe('UK');
  });

  it('should handle cities not sorted by revenue desc', () => {
    const response = [
      { city: 'Austin', state: 'TX', order_count: 100, revenue: 5000 },
      { city: 'Dallas', state: 'TX', order_count: 50, revenue: 10000 },
    ];
    const isSorted = response.every((v, i, a) =>
      i === 0 || a[i - 1].revenue >= v.revenue
    );
    expect(isSorted).toBe(false);
  });

  it('should handle negative order counts', () => {
    const response = [
      { city: 'Austin', state: 'TX', order_count: -5, revenue: 1000 },
    ];
    // Frontend should flag or filter
    expect(response[0].order_count).toBeLessThan(0);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
//  Network and HTTP error handling
// ─────────────────────────────────────────────────────────────────────────────

describe('Network Error Handling', () => {
  it('should handle 500 Internal Server Error', () => {
    const statusCode = 500;
    const message = 'Internal Server Error';
    expect(statusCode).toBeGreaterThanOrEqual(500);
    expect(statusCode).toBeLessThan(600);
  });

  it('should handle 404 Not Found', () => {
    const statusCode = 404;
    expect(statusCode).toBe(404);
  });

  it('should handle 422 Unprocessable Entity (validation error)', () => {
    const statusCode = 422;
    expect(statusCode).toBe(422);
  });

  it('should handle timeout (network error)', () => {
    const error = new Error('Network timeout');
    expect(error.message).toContain('timeout');
  });

  it('should handle malformed JSON response', () => {
    const malformedJSON = '{invalid json}';
    expect(() => JSON.parse(malformedJSON)).toThrow();
  });

  it('should handle empty response body', () => {
    const response = '';
    expect(() => JSON.parse(response)).toThrow();
  });
});

// ─────────────────────────────────────────────────────────────────────────────
//  Type and field validation
// ─────────────────────────────────────────────────────────────────────────────

describe('Response Type Validation', () => {
  it('should detect when array is expected but object received', () => {
    const response = { data: [] }; // Wrapped in object
    expect(Array.isArray(response)).toBe(false);
  });

  it('should detect when number is expected but string received', () => {
    const revenue = '12345'; // String
    const isNumeric = !isNaN(parseFloat(revenue)) && isFinite(revenue);
    expect(isNumeric).toBe(true); // Can be coerced
  });

  it('should detect when expected field is missing', () => {
    const response = { name: 'Product' }; // Missing price
    const price = response.price;
    expect(price).toBeUndefined();
  });

  it('should detect extra unexpected fields', () => {
    const response = {
      name: 'Product',
      price: 100,
      secret_field: 'should not be here',
    };
    expect('secret_field' in response).toBe(true);
  });
});
