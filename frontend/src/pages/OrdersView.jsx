/**
 * OrdersView.js — Orders Overview page
 *
 * This page shows:
 *   - Stat cards: total revenue, total orders, unique customers
 *   - A bar/line chart of monthly revenue over time
 *   - A bar chart of revenue by city/state
 *   - A date range filter
 *
 * The data fetching is already wired up.
 * Your job: implement the UI — charts, stat cards, and layout.
 *
 * Useful libraries already installed:
 *   - recharts: BarChart, LineChart, XAxis, YAxis, Tooltip, ResponsiveContainer
 */

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import Navbar from '../components/Navbar';
import { getSummary, getOrders, getCities } from '../utils/api';
import { DocumentChart, BarChartIcon, GlobePin, FlowNodes, Gear } from '../components/Icons';

export default function OrdersView() {
  const [startDate, setStartDate] = useState('2022-01-01');
  const [endDate,   setEndDate]   = useState('2022-12-31');
  const [summary,   setSummary]   = useState(null);
  const [orders,    setOrders]    = useState([]);
  const [cities,    setCities]    = useState([]);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState(null);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 300_000);
    return () => clearInterval(interval);
  }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [s, o, c] = await Promise.all([
        getSummary(),
        getOrders(startDate, endDate),
        getCities(startDate, endDate),
      ]);
      setSummary(s);
      setOrders(o);
      setCities(c);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">

        {/* ── Filter bar ─────────────────────────────────────────────────── */}
        <div className="filter-bar">
          <FlowNodes size={14} style={{ color: 'var(--text-muted)' }} />
          <label>From</label>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
          <label>To</label>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
          <button className="btn-apply" onClick={loadData} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Gear size={13} />Apply
          </button>
        </div>

        {/* ── Error state ────────────────────────────────────────────────── */}
        {error && (
          <div style={{ color: '#C62828', padding: 16, background: '#FFEBEE', borderRadius: 8, marginBottom: 16 }}>
            Error: {error}
          </div>
        )}

        {/* ── Loading state ──────────────────────────────────────────────── */}
        {loading && <div className="loading">Loading orders data…</div>}

        {!loading && !error && (
          <>
            {/* Stat cards */}
            <div className="stat-row">
              <div className="stat-box">
                <div className="label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <DocumentChart size={12} />Total Revenue
                </div>
                <div className="value">
                  ${summary?.total_revenue?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              </div>
              <div className="stat-box">
                <div className="label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <BarChartIcon size={12} />Total Orders
                </div>
                <div className="value">{summary?.total_orders?.toLocaleString()}</div>
              </div>
              <div className="stat-box">
                <div className="label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <GlobePin size={12} />Unique Customers
                </div>
                <div className="value">{summary?.unique_customers?.toLocaleString()}</div>
              </div>
              <div className="stat-box">
                <div className="label">Date Range</div>
                <div className="value" style={{ fontSize: 14 }}>
                  {summary?.date_range?.start} – {summary?.date_range?.end}
                </div>
              </div>
            </div>

            {/* Monthly revenue bar chart */}
            <div className="card" style={{ marginBottom: 20 }}>
              <div className="section-title" style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <BarChartIcon size={18} />Monthly Revenue
              </div>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={orders} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                  <XAxis dataKey="month_name" tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
                  <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}K`} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} width={56} />
                  <Tooltip formatter={v => [`$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Revenue']} />
                  <Bar dataKey="revenue" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Revenue by city horizontal bar chart — top 10 */}
            <div className="card">
              <div className="section-title" style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <GlobePin size={18} />Revenue by City (Top 10)
              </div>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart
                  layout="vertical"
                  data={cities.slice(0, 10).map(c => ({ ...c, label: `${c.city}, ${c.state}` }))}
                  margin={{ top: 4, right: 24, left: 8, bottom: 4 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
                  <XAxis type="number" tickFormatter={v => `$${(v / 1000).toFixed(0)}K`} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
                  <YAxis type="category" dataKey="label" width={120} tick={{ fontSize: 12, fill: 'var(--text-muted)' }} />
                  <Tooltip formatter={v => [`$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Revenue']} />
                  <Bar dataKey="revenue" fill="var(--blue)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
