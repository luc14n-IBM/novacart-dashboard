/**
 * ProductsView.js — Product Performance page
 *
 * Charts:
 *   - Top 10 Products: Horizontal Bar / Vertical Bar / Category Donut toggle
 *   - Product Details: table (unchanged)
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import Navbar from '../components/Navbar';
import { getProducts } from '../utils/api';
import { ProductGrid, SearchGraph, Gear, BarChartIcon, HBarChartIcon, PieChartIcon } from '../components/Icons';

// Brand palette — ordered for pie slice assignment
const BRAND_COLORS = [
  '#1C4EF5', // Vivid Blue
  '#00BFA5', // Teal
  '#FF6B6B', // Salmon
  '#BBDEFB', // Light Blue
  '#A8E6CF', // Mint
  '#051B3F', // Navy
];

function formatCurrency(value) {
  if (!value) return '$0';
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000)    return `$${(value / 1000).toFixed(0)}K`;
  return `$${value.toFixed(2)}`;
}

// Custom donut label — percentage only, suppressed on slices < 5% to avoid clutter
function renderDonutLabel({ cx, cy, midAngle, innerRadius, outerRadius, percent }) {
  if (percent < 0.05) return null;
  const RADIAN = Math.PI / 180;
  const r  = innerRadius + (outerRadius - innerRadius) * 0.55;
  const x  = cx + r * Math.cos(-midAngle * RADIAN);
  const y  = cy + r * Math.sin(-midAngle * RADIAN);
  return (
    <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central"
      style={{ fontSize: 11, fontWeight: 700, fontFamily: 'IBM Plex Sans, sans-serif' }}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
}

export default function ProductsView({ startDate, endDate, setStartDate, setEndDate }) {
  const [products,     setProducts]     = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState(null);
  const [productsView, setProductsView] = useState('hbar'); // 'hbar' | 'vbar' | 'donut'

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const data = await getProducts(startDate, endDate);
      setProducts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const xTickProps = { fontSize: 12, fill: 'var(--text-muted)' };
  const gridStroke = 'var(--border)';

  const chartData = products.map(p => ({
    ...p,
    shortName: p.name.length > 22 ? p.name.slice(0, 22) + '…' : p.name,
  }));

  // Roll products up into category totals for the donut
  const categoryData = Object.values(
    products.reduce((acc, p) => {
      const key = p.category || 'Other';
      if (!acc[key]) acc[key] = { category: key, revenue: 0 };
      acc[key].revenue = Math.round((acc[key].revenue + p.revenue) * 100) / 100;
      return acc;
    }, {})
  ).sort((a, b) => b.revenue - a.revenue);

  const chartTitle = productsView === 'donut'
    ? 'Revenue by Category'
    : 'Top 10 Products by Revenue';

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">

        <div className="filter-bar">
          <label>From</label>
          <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
          <label>To</label>
          <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
          <button className="btn-apply" onClick={loadData} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Gear size={13} />Apply
          </button>
        </div>

        {error && (
          <div style={{ color: '#C62828', padding: 16, background: '#FFEBEE', borderRadius: 8, marginBottom: 16 }}>
            Error: {error}
          </div>
        )}

        {loading && <div className="loading">Loading products data…</div>}

        {!loading && !error && (
          <div className="grid-2">

            {/* ── Left chart card ────────────────────────────────────────── */}
            <div className="card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
                <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <SearchGraph size={18} />{chartTitle}
                </div>
                <div className="chart-toggle">
                  <button className={productsView === 'hbar'  ? 'active' : ''} onClick={() => setProductsView('hbar')}>
                    <HBarChartIcon size={13} />Horizontal
                  </button>
                  <button className={productsView === 'vbar'  ? 'active' : ''} onClick={() => setProductsView('vbar')}>
                    <BarChartIcon size={13} />Vertical
                  </button>
                  <button className={productsView === 'donut' ? 'active' : ''} onClick={() => setProductsView('donut')}>
                    <PieChartIcon size={13} />Category
                  </button>
                </div>
              </div>

              {/* Horizontal bar */}
              {productsView === 'hbar' && (
                <ResponsiveContainer width="100%" height={340}>
                  <BarChart layout="vertical" data={chartData} margin={{ top: 4, right: 24, left: 8, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
                    <XAxis type="number" tickFormatter={v => `$${(v / 1000).toFixed(0)}K`} tick={xTickProps} />
                    <YAxis type="category" dataKey="shortName" width={140} tick={xTickProps} />
                    <Tooltip formatter={v => [formatCurrency(v), 'Revenue']} labelFormatter={(_, payload) => payload?.[0]?.payload?.name ?? ''} />
                    <Bar dataKey="revenue" fill="var(--accent)" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}

              {/* Vertical bar */}
              {productsView === 'vbar' && (
                <ResponsiveContainer width="100%" height={340}>
                  <BarChart data={chartData} margin={{ top: 4, right: 16, left: 0, bottom: 60 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                    <XAxis dataKey="shortName" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} angle={-40} textAnchor="end" interval={0} />
                    <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}K`} tick={xTickProps} width={56} />
                    <Tooltip formatter={v => [formatCurrency(v), 'Revenue']} labelFormatter={(_, payload) => payload?.[0]?.payload?.name ?? ''} />
                    <Bar dataKey="revenue" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}

              {/* Category donut */}
              {productsView === 'donut' && (
                <ResponsiveContainer width="100%" height={340}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      dataKey="revenue"
                      nameKey="category"
                      cx="50%"
                      cy="46%"
                      innerRadius="42%"
                      outerRadius="68%"
                      labelLine={false}
                      label={renderDonutLabel}
                    >
                      {categoryData.map((_, i) => (
                        <Cell key={i} fill={BRAND_COLORS[i % BRAND_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={v => [formatCurrency(v), 'Revenue']} />
                    <Legend
                      formatter={(value) => (
                        <span style={{ fontSize: 12, color: 'var(--text-primary)', fontFamily: 'IBM Plex Sans, sans-serif' }}>
                          {value}
                        </span>
                      )}
                    />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            {/* ── Products detail table ──────────────────────────────────── */}
            <div className="card">
              <div className="section-title" style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                <ProductGrid size={18} />Product Details
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)', textAlign: 'left', color: 'var(--text-muted)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    <th style={{ padding: '8px 10px' }}>Name</th>
                    <th style={{ padding: '8px 10px' }}>Category</th>
                    <th style={{ padding: '8px 10px', textAlign: 'right' }}>Units Sold</th>
                    <th style={{ padding: '8px 10px', textAlign: 'right' }}>Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map((p, i) => (
                    <tr key={p.product_id} style={{ background: i % 2 === 0 ? 'transparent' : 'var(--bg-primary)', borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '8px 10px', color: 'var(--text-primary)', fontWeight: 500 }}>{p.name}</td>
                      <td style={{ padding: '8px 10px', color: 'var(--text-secondary)' }}>{p.category}</td>
                      <td style={{ padding: '8px 10px', textAlign: 'right', color: 'var(--text-secondary)' }}>{p.units_sold?.toLocaleString()}</td>
                      <td style={{ padding: '8px 10px', textAlign: 'right', fontWeight: 600, color: 'var(--accent)' }}>{formatCurrency(p.revenue)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
