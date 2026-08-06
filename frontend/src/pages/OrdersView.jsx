/**
 * OrdersView.js — Orders Overview page
 *
 * Charts:
 *   - Monthly Revenue: Bar / Line / Area toggle
 *   - Revenue by City: Horizontal Bar / Vertical Bar toggle
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar,
  LineChart, Line,
  AreaChart, Area,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';
import Navbar from '../components/Navbar';
import { getSummary, getOrders, getCities } from '../utils/api';
import {
  DocumentChart, BarChartIcon, GlobePin, FlowNodes, Gear, Calendar,
  LineChartIcon, AreaChartIcon, HBarChartIcon,
} from '../components/Icons';

export default function OrdersView({ startDate, endDate, setStartDate, setEndDate }) {
  const [summary,         setSummary]         = useState(null);
  const [orders,          setOrders]          = useState([]);
  const [cities,          setCities]          = useState([]);
  const [loading,         setLoading]         = useState(true);
  const [error,           setError]           = useState(null);
  const [revenueView,     setRevenueView]     = useState('bar');   // 'bar' | 'line' | 'area'
  const [cityView,        setCityView]        = useState('hbar');  // 'hbar' | 'vbar'

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
        getSummary(startDate, endDate),
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

  const revenueTooltip = { formatter: v => [`$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Revenue'] };
  const yTickFmt = v => `$${(v / 1000).toFixed(0)}K`;
  const xTickProps = { fontSize: 12, fill: 'var(--text-muted)' };
  const gridStroke = 'var(--border)';

  const cityData = cities.slice(0, 10).map(c => ({ ...c, label: `${c.city}, ${c.state}` }));

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">

        {/* ── Filter bar ─────────────────────────────────────────────────── */}
        <div className="filter-bar">
          <FlowNodes size={14} style={{ color: 'var(--text-muted)' }} />
          <label htmlFor="orders-from">From</label>
          <input id="orders-from" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
          <label htmlFor="orders-to">To</label>
          <input id="orders-to" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
          <button className="btn-apply" onClick={loadData} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Gear size={13} />Apply
          </button>
        </div>

        {/* ── Error state ────────────────────────────────────────────────── */}
        {error && (
          <div role="alert" style={{ color: '#C62828', padding: 16, background: '#FFEBEE', borderRadius: 8, marginBottom: 16 }}>
            Error: {error}
          </div>
        )}

        {/* ── Loading state ──────────────────────────────────────────────── */}
        {loading && <div role="status" className="loading">Loading orders data…</div>}

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
                <div className="label" style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <Calendar size={12} />Date Range
                </div>
                <div className="value" style={{ fontSize: 14 }}>
                  {summary?.date_range?.start} – {summary?.date_range?.end}
                </div>
              </div>
            </div>

            {/* ── Monthly Revenue chart ───────────────────────────────────── */}
            <div className="card" style={{ marginBottom: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
                <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <BarChartIcon size={18} />Monthly Revenue
                </div>
                <div className="chart-toggle">
                  <button className={revenueView === 'bar'  ? 'active' : ''} onClick={() => setRevenueView('bar')}>
                    <BarChartIcon size={13} />Bar
                  </button>
                  <button className={revenueView === 'line' ? 'active' : ''} onClick={() => setRevenueView('line')}>
                    <LineChartIcon size={13} />Line
                  </button>
                  <button className={revenueView === 'area' ? 'active' : ''} onClick={() => setRevenueView('area')}>
                    <AreaChartIcon size={13} />Area
                  </button>
                </div>
              </div>

              <ResponsiveContainer width="100%" height={260}>
                {revenueView === 'bar' ? (
                  <BarChart data={orders} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                    <XAxis dataKey="month_name" tick={xTickProps} />
                    <YAxis tickFormatter={yTickFmt} tick={xTickProps} width={56} />
                    <Tooltip {...revenueTooltip} />
                    <Bar dataKey="revenue" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                ) : revenueView === 'line' ? (
                  <LineChart data={orders} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                    <XAxis dataKey="month_name" tick={xTickProps} />
                    <YAxis tickFormatter={yTickFmt} tick={xTickProps} width={56} />
                    <Tooltip {...revenueTooltip} />
                    <Line type="monotone" dataKey="revenue" stroke="var(--blue)" strokeWidth={2} dot={{ r: 4, fill: 'var(--blue)' }} activeDot={{ r: 5 }} />
                  </LineChart>
                ) : (
                  <AreaChart data={orders} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
                    <defs>
                      <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="var(--accent)" stopOpacity={0.35} />
                        <stop offset="95%" stopColor="var(--accent)" stopOpacity={0.03} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                    <XAxis dataKey="month_name" tick={xTickProps} />
                    <YAxis tickFormatter={yTickFmt} tick={xTickProps} width={56} />
                    <Tooltip {...revenueTooltip} />
                    <Area type="monotone" dataKey="revenue" stroke="var(--accent)" strokeWidth={2} fill="url(#revGrad)" />
                  </AreaChart>
                )}
              </ResponsiveContainer>
            </div>

            {/* ── Revenue by City chart ───────────────────────────────────── */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
                <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <GlobePin size={18} />Revenue by City (Top 10)
                </div>
                <div className="chart-toggle">
                  <button className={cityView === 'hbar' ? 'active' : ''} onClick={() => setCityView('hbar')}>
                    <HBarChartIcon size={13} />Horizontal
                  </button>
                  <button className={cityView === 'vbar' ? 'active' : ''} onClick={() => setCityView('vbar')}>
                    <BarChartIcon size={13} />Vertical
                  </button>
                </div>
              </div>

              <ResponsiveContainer width="100%" height={320}>
                {cityView === 'hbar' ? (
                  <BarChart
                    layout="vertical"
                    data={cityData}
                    margin={{ top: 4, right: 24, left: 8, bottom: 4 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
                    <XAxis type="number" tickFormatter={yTickFmt} tick={xTickProps} />
                    <YAxis type="category" dataKey="label" width={120} tick={xTickProps} />
                    <Tooltip formatter={v => [`$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Revenue']} />
                    <Bar dataKey="revenue" fill="var(--blue)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                ) : (
                  <BarChart
                    data={cityData}
                    margin={{ top: 4, right: 16, left: 0, bottom: 60 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                    <XAxis dataKey="label" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} angle={-40} textAnchor="end" interval={0} />
                    <YAxis tickFormatter={yTickFmt} tick={xTickProps} width={56} />
                    <Tooltip formatter={v => [`$${Number(v).toLocaleString('en-US', { minimumFractionDigits: 2 })}`, 'Revenue']} />
                    <Bar dataKey="revenue" fill="var(--blue)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
