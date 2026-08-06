/**
 * CustomersView.js — Customer List page
 *
 * Views:
 *   - Table: sortable top customers by revenue
 *   - Bar Chart: top 10 customers by spend (horizontal bar)
 *   Toggle buttons at the top of the card switch between views.
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts';
import Navbar from '../components/Navbar';
import { getCustomers } from '../utils/api';
import { UserBriefcase, Gear, BarChartIcon, TableIcon, HBarChartIcon } from '../components/Icons';

function formatCurrency(value) {
  if (!value) return '$0';
  return `$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function CustomersView({ startDate, endDate, setStartDate, setEndDate }) {
  const [customers,  setCustomers]  = useState([]);
  const [sortBy,     setSortBy]     = useState('total_spent');
  const [sortDir,    setSortDir]    = useState('desc');
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState(null);
  const [view,       setView]       = useState('table'); // 'table' | 'hbar' | 'vbar'
  const [topN,       setTopN]       = useState(10);     // how many customers to display

  useEffect(() => { loadData(); }, []);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const data = await getCustomers(startDate, endDate);
      setCustomers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // Sort handler — toggles direction if same column, resets to desc if new column
  function handleSort(column) {
    if (sortBy === column) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortDir('desc');
    }
  }

  // Apply sort to customers array
  const sorted = [...customers].sort((a, b) => {
    const va = a[sortBy], vb = b[sortBy];
    if (typeof va === 'number') return sortDir === 'asc' ? va - vb : vb - va;
    return sortDir === 'asc'
      ? String(va).localeCompare(String(vb))
      : String(vb).localeCompare(String(va));
  });

  // Sort indicator helper
  const sortIcon = (col) => sortBy === col ? (sortDir === 'asc' ? ' ↑' : ' ↓') : '';

  const xTickProps = { fontSize: 12, fill: 'var(--text-muted)' };
  const gridStroke = 'var(--border)';

  // Top-N customers by total_spent for charts (respects the topN dropdown)
  const topN_ALL = topN === 'all';
  const topSlice = [...customers]
    .sort((a, b) => b.total_spent - a.total_spent)
    .slice(0, topN_ALL ? undefined : topN)
    .map(c => ({ ...c, shortName: c.name.length > 18 ? c.name.slice(0, 18) + '…' : c.name }));

  // Table rows also respect topN
  const displayedRows = topN_ALL ? sorted : sorted.slice(0, topN);

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <div className="page">

        <div className="filter-bar">
          <label htmlFor="customers-from">From</label>
          <input id="customers-from" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
          <label htmlFor="customers-to">To</label>
          <input id="customers-to" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
          <button className="btn-apply" onClick={loadData} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <Gear size={13} />Apply
          </button>
          <label htmlFor="customers-topn" style={{ marginLeft: 'auto' }}>Show</label>
          <select
            id="customers-topn"
            value={topN}
            onChange={e => setTopN(e.target.value === 'all' ? 'all' : Number(e.target.value))}
          >
            <option value={5}>Top 5</option>
            <option value={10}>Top 10</option>
            <option value={25}>Top 25</option>
            <option value={50}>Top 50</option>
            <option value="all">All</option>
          </select>
          <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            {topN_ALL ? customers.length : Math.min(topN, customers.length)} of {customers.length} customers
          </span>
        </div>

        {error && (
          <div role="alert" style={{ color: '#C62828', padding: 16, background: '#FFEBEE', borderRadius: 8, marginBottom: 16 }}>
            Error: {error}
          </div>
        )}

        {loading && <div role="status" className="loading">Loading customers…</div>}

        {!loading && !error && (
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16, flexWrap: 'wrap', gap: 8 }}>
              <div className="section-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <UserBriefcase size={18} />Top Customers by Revenue
              </div>
              <div className="chart-toggle">
                <button className={view === 'table' ? 'active' : ''} onClick={() => setView('table')}>
                  <TableIcon size={13} />Table
                </button>
                <button className={view === 'hbar' ? 'active' : ''} onClick={() => setView('hbar')}>
                  <HBarChartIcon size={13} />Horizontal
                </button>
                <button className={view === 'vbar' ? 'active' : ''} onClick={() => setView('vbar')}>
                  <BarChartIcon size={13} />Vertical
                </button>
              </div>
            </div>

            {/* ── Table view ──────────────────────────────────────────────── */}
            {view === 'table' && (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid var(--border)', textAlign: 'left', color: 'var(--text-muted)', fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    {[
                      { key: 'name',         label: 'Name' },
                      { key: 'city',         label: 'City' },
                      { key: 'state',        label: 'State' },
                      { key: 'total_orders', label: 'Orders' },
                      { key: 'total_spent',  label: 'Total Spent' },
                    ].map(col => (
                      <th
                        key={col.key}
                        onClick={() => handleSort(col.key)}
                        style={{ padding: '8px 10px', cursor: 'pointer', userSelect: 'none', textAlign: col.key === 'total_orders' || col.key === 'total_spent' ? 'right' : 'left' }}
                      >
                        {col.label}{sortIcon(col.key)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {displayedRows.map((c, i) => (
                    <tr key={c.customer_id} style={{ background: i % 2 === 0 ? 'transparent' : 'var(--bg-primary)', borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '8px 10px', fontWeight: 500, color: 'var(--text-primary)' }}>{c.name}</td>
                      <td style={{ padding: '8px 10px', color: 'var(--text-secondary)' }}>{c.city}</td>
                      <td style={{ padding: '8px 10px', color: 'var(--text-secondary)' }}>{c.state}</td>
                      <td style={{ padding: '8px 10px', textAlign: 'right', color: 'var(--text-secondary)' }}>{c.total_orders}</td>
                      <td style={{ padding: '8px 10px', textAlign: 'right', fontWeight: 600, color: 'var(--accent)' }}>{formatCurrency(c.total_spent)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}

            {/* ── Horizontal bar chart view ───────────────────────────────── */}
            {view === 'hbar' && (
              <ResponsiveContainer width="100%" height={340}>
                <BarChart
                  layout="vertical"
                  data={topSlice}
                  margin={{ top: 4, right: 24, left: 8, bottom: 4 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} horizontal={false} />
                  <XAxis type="number" tickFormatter={v => `$${(v / 1000).toFixed(0)}K`} tick={xTickProps} />
                  <YAxis type="category" dataKey="shortName" width={130} tick={xTickProps} />
                  <Tooltip formatter={v => [formatCurrency(v), 'Total Spent']} labelFormatter={(_, payload) => payload?.[0]?.payload?.name ?? ''} />
                  <Bar dataKey="total_spent" fill="var(--accent)" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}

            {/* ── Vertical bar chart view ─────────────────────────────────── */}
            {view === 'vbar' && (
              <ResponsiveContainer width="100%" height={340}>
                <BarChart
                  data={topSlice}
                  margin={{ top: 4, right: 16, left: 0, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke={gridStroke} />
                  <XAxis dataKey="shortName" tick={{ fontSize: 11, fill: 'var(--text-muted)' }} angle={-40} textAnchor="end" interval={0} />
                  <YAxis tickFormatter={v => `$${(v / 1000).toFixed(0)}K`} tick={xTickProps} width={56} />
                  <Tooltip formatter={v => [formatCurrency(v), 'Total Spent']} labelFormatter={(_, payload) => payload?.[0]?.payload?.name ?? ''} />
                  <Bar dataKey="total_spent" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}

          </div>
        )}
      </div>
    </div>
  );
}
