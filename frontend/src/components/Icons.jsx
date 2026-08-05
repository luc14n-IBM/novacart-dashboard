/**
 * Icons.jsx — Shared inline SVG icon library for NovaCart Dashboard
 *
 * All icons use currentColor, 16x16 viewBox, outline style (1.2–1.5px stroke).
 * Pass size prop to override width/height (default 16).
 * Usage: <Icons.BarChart size={18} />
 */

import React from 'react';

const base = (size) => ({ width: size, height: size, display: 'inline-block', verticalAlign: 'middle' });

// Shopping Cart + Globe — brand mark, global commerce identity
export function CartGlobe({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.3"/>
      <ellipse cx="7" cy="7" rx="2.3" ry="5.5" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="1.5" y1="7" x2="12.5" y2="7" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="2.5" y1="4.5" x2="11.5" y2="4.5" stroke="currentColor" strokeWidth="0.9"/>
      <line x1="2.5" y1="9.5" x2="11.5" y2="9.5" stroke="currentColor" strokeWidth="0.9"/>
      <path d="M11 10.5h2.5l.8 2.5H11.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round"/>
      <circle cx="12" cy="13.8" r="0.6" fill="currentColor"/>
      <circle cx="13.8" cy="13.8" r="0.6" fill="currentColor"/>
    </svg>
  );
}

// Product Grid — product catalog / inventory
export function ProductGrid({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="1" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="9" y="1" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="1" y="9" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="9" y="9" width="6" height="6" rx="1" stroke="currentColor" strokeWidth="1.3"/>
    </svg>
  );
}

// Bar Chart — revenue charts, analytics
export function BarChartIcon({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="7" width="3" height="7" rx="0.5" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="6" y="4" width="3" height="10" rx="0.5" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="11" y="1" width="3" height="13" rx="0.5" stroke="currentColor" strokeWidth="1.3"/>
      <line x1="1" y1="14.5" x2="15" y2="14.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>
  );
}

// Document + Chart — orders overview, reports
export function DocumentChart({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M9 1H3a1 1 0 00-1 1v12a1 1 0 001 1h10a1 1 0 001-1V5L9 1z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/>
      <path d="M9 1v4h4" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/>
      <polyline points="5,11 7,8.5 9,10 11,7.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

// Magnifying Glass + Graph — search / explore products
export function SearchGraph({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="6.5" cy="6.5" r="4.5" stroke="currentColor" strokeWidth="1.3"/>
      <line x1="10" y1="10" x2="14.5" y2="14.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
      <polyline points="4,7.5 5.5,5.5 7,7 8.5,4.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  );
}

// Database + Gear — service status, data infrastructure
export function DatabaseGear({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <ellipse cx="7" cy="3.5" rx="5" ry="2" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M2 3.5v4c0 1.1 2.24 2 5 2s5-.9 5-2v-4" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M2 7.5v3c0 1.1 2.24 2 5 2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <circle cx="12.5" cy="12.5" r="2.5" stroke="currentColor" strokeWidth="1.2"/>
      <circle cx="12.5" cy="12.5" r="0.8" fill="currentColor"/>
      <line x1="12.5" y1="9.5" x2="12.5" y2="10.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="12.5" y1="14.5" x2="12.5" y2="15.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="9.5" y1="12.5" x2="10.5" y2="12.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="14.5" y1="12.5" x2="15.5" y2="12.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  );
}

// Connected Nodes / Flow Arrows — data pipeline, ETL flow
export function FlowNodes({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="2.5" cy="8" r="1.8" stroke="currentColor" strokeWidth="1.2"/>
      <circle cx="8" cy="2.5" r="1.8" stroke="currentColor" strokeWidth="1.2"/>
      <circle cx="8" cy="13.5" r="1.8" stroke="currentColor" strokeWidth="1.2"/>
      <circle cx="13.5" cy="8" r="1.8" stroke="currentColor" strokeWidth="1.2"/>
      <line x1="4.3" y1="8" x2="11.7" y2="8" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="8" y1="4.3" x2="8" y2="11.7" stroke="currentColor" strokeWidth="1.1"/>
      <polyline points="10.5,8 11.7,8" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>
  );
}

// User + Briefcase — account managers, B2B customers
export function UserBriefcase({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="6" cy="4.5" r="2.5" stroke="currentColor" strokeWidth="1.3"/>
      <path d="M1 14c0-2.76 2.24-4 5-4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
      <rect x="9" y="9" width="6" height="5" rx="1" stroke="currentColor" strokeWidth="1.2"/>
      <path d="M10.5 9V7.5a1.5 1.5 0 013 0V9" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="9" y1="11.5" x2="15" y2="11.5" stroke="currentColor" strokeWidth="1.1"/>
    </svg>
  );
}

// Globe + Location Pins — geographic / city revenue
export function GlobePin({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="8" cy="8" r="6.5" stroke="currentColor" strokeWidth="1.3"/>
      <ellipse cx="8" cy="8" rx="2.8" ry="6.5" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="1.5" y1="8" x2="14.5" y2="8" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="2.5" y1="5" x2="13.5" y2="5" stroke="currentColor" strokeWidth="0.9"/>
      <path d="M8 1.5C9.2 3 10 4.8 10 6a2 2 0 01-4 0c0-1.2.8-3 2-4.5z" stroke="currentColor" strokeWidth="1.1" fill="none"/>
      <circle cx="8" cy="5.8" r="0.7" fill="currentColor"/>
    </svg>
  );
}

// Gear — settings, filter/apply actions
export function Gear({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="8" cy="8" r="2.5" stroke="currentColor" strokeWidth="1.3"/>
      <path d="M8 1.5v1.2M8 13.3v1.2M1.5 8h1.2M13.3 8h1.2M3.4 3.4l.85.85M11.75 11.75l.85.85M3.4 12.6l.85-.85M11.75 4.25l.85-.85"
        stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
    </svg>
  );
}

// Calendar — date range, time-based filters
export function Calendar({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="3" width="12" height="11" rx="1" stroke="currentColor" strokeWidth="1.3"/>
      <line x1="2" y1="6" x2="14" y2="6" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="5" y1="1" x2="5" y2="3.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <line x1="11" y1="1" x2="11" y2="3.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
      <circle cx="4.5" cy="9" r="0.6" fill="currentColor"/>
      <circle cx="8" cy="9" r="0.6" fill="currentColor"/>
      <circle cx="11.5" cy="9" r="0.6" fill="currentColor"/>
      <circle cx="4.5" cy="12" r="0.6" fill="currentColor"/>
      <circle cx="8" cy="12" r="0.6" fill="currentColor"/>
    </svg>
  );
}


// Line Chart — line/trend chart view toggle
export function LineChartIcon({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <polyline points="1,13 4,8 7,10 10,5 13,7 15,3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
      <line x1="1" y1="14.5" x2="15" y2="14.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>
  );
}

// Area Chart — area/fill chart view toggle
export function AreaChartIcon({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <polyline points="1,13 4,8 7,10 10,5 13,7 15,3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/>
      <polygon points="1,13 4,8 7,10 10,5 13,7 15,3 15,14.5 1,14.5" fill="currentColor" fillOpacity="0.15" stroke="none"/>
      <line x1="1" y1="14.5" x2="15" y2="14.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>
  );
}

// Horizontal Bars — horizontal bar chart view toggle
export function HBarChartIcon({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="2"  width="10" height="3" rx="0.5" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="1" y="6.5" width="7"  height="3" rx="0.5" stroke="currentColor" strokeWidth="1.3"/>
      <rect x="1" y="11" width="13" height="3" rx="0.5" stroke="currentColor" strokeWidth="1.3"/>
      <line x1="1" y1="1" x2="1" y2="15" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/>
    </svg>
  );
}

// Table — table view toggle
export function TableIcon({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="1" y="1" width="14" height="14" rx="1" stroke="currentColor" strokeWidth="1.3"/>
      <line x1="1" y1="5" x2="15" y2="5" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="1" y1="9" x2="15" y2="9" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="1" y1="13" x2="15" y2="13" stroke="currentColor" strokeWidth="1.1"/>
      <line x1="6" y1="5" x2="6" y2="15" stroke="currentColor" strokeWidth="1.1"/>
    </svg>
  );
}


// Pie / Donut Chart — category breakdown toggle
export function PieChartIcon({ size = 16 }) {
  return (
    <svg style={base(size)} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M8 2a6 6 0 1 0 6 6H8V2z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/>
      <path d="M10 2.8A6 6 0 0 1 14 8" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/>
    </svg>
  );
}
