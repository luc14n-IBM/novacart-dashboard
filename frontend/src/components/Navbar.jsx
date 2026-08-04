import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTheme } from '../utils/ThemeContext';
import ServiceStatus from './ServiceStatus';

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { dark, toggle } = useTheme();

  const links = [
    {
      label: 'Orders',
      path: '/orders',
      icon: (
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="1" y="1" width="14" height="14" rx="2" stroke="currentColor" strokeWidth="1.4" fill="none"/>
          <line x1="4" y1="5.5" x2="12" y2="5.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
          <line x1="4" y1="8" x2="12" y2="8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
          <line x1="4" y1="10.5" x2="9" y2="10.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
        </svg>
      ),
    },
    {
      label: 'Products',
      path: '/products',
      icon: (
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 1L15 4.5V11.5L8 15L1 11.5V4.5L8 1Z" stroke="currentColor" strokeWidth="1.4" fill="none" strokeLinejoin="round"/>
          <line x1="8" y1="8" x2="8" y2="15" stroke="currentColor" strokeWidth="1.2"/>
          <line x1="1" y1="4.5" x2="8" y2="8" stroke="currentColor" strokeWidth="1.2"/>
          <line x1="15" y1="4.5" x2="8" y2="8" stroke="currentColor" strokeWidth="1.2"/>
        </svg>
      ),
    },
    {
      label: 'Customers',
      path: '/customers',
      icon: (
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="8" cy="5" r="3" stroke="currentColor" strokeWidth="1.4" fill="none"/>
          <path d="M2 14c0-3.314 2.686-5 6-5s6 1.686 6 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" fill="none"/>
        </svg>
      ),
    },
  ];

  return (
    <nav style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 24px', height: 56,
      background: '#051B3F',
      boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
      position: 'sticky', top: 0, zIndex: 100,
      fontFamily: "'IBM Plex Sans', -apple-system, sans-serif",
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}
           onClick={() => navigate('/')}>
        {/* Cart — NovaCart brand mark */}
        <svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="NovaCart">
          <path d="M2 4h4l3.5 14h14L27 8H9" stroke="#BBDEFB" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
          <circle cx="13.5" cy="27" r="2" fill="#00BFA5"/>
          <circle cx="23" cy="27" r="2" fill="#00BFA5"/>
        </svg>
        <span style={{ color: '#FFFFFF', fontWeight: 700, fontSize: 18, letterSpacing: '-0.2px' }}>NovaCart</span>
        <span style={{
          color: '#051B3F', background: '#00BFA5',
          fontSize: 10, fontWeight: 700, letterSpacing: '0.6px',
          padding: '1px 7px', borderRadius: 4, marginLeft: 2, textTransform: 'uppercase',
        }}>Dashboard</span>
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        {links.map(({ label, path, icon }) => {
          const active = location.pathname === path;
          return (
            <button key={path} onClick={() => navigate(path)}
              style={{
                fontFamily: "'IBM Plex Sans', sans-serif",
                fontSize: 13, fontWeight: 600,
                background: active ? 'rgba(28,78,245,0.2)' : 'transparent',
                border: active ? '1px solid #1C4EF5' : '1px solid transparent',
                color: active ? '#FFFFFF' : '#BBDEFB',
                borderRadius: 6, padding: '4px 14px', cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: 6,
              }}>
              {icon}
              {label}
            </button>
          );
        })}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <ServiceStatus />
        <button onClick={toggle} title={dark ? 'Light mode' : 'Dark mode'}
          style={{
            background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.15)',
            color: '#fff', borderRadius: 6, padding: '4px 10px', cursor: 'pointer', fontSize: 16,
          }}>
          {dark ? '☀️' : '🌙'}
        </button>
      </div>
    </nav>
  );
}
