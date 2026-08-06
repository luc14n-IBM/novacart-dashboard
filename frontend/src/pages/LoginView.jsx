import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authorize } from '../utils/api';

export default function LoginView() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await authorize();
      navigate('/orders');
    } catch (err) {
      setError('Unable to authenticate. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-primary)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: "var(--font, 'IBM Plex Sans', sans-serif)",
    }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius)',
        boxShadow: 'var(--shadow)',
        width: '100%',
        maxWidth: 400,
        padding: '40px 36px 32px',
      }}>

        {/* Brand mark */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 12 }}>
            <div style={{
              width: 56, height: 56, borderRadius: 14,
              background: '#051B3F',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 4px 16px rgba(5,27,63,0.18)',
            }}>
              {/* Cart — NovaCart brand mark */}
              <svg width="40" height="34" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="NovaCart">
                <path d="M2 4h4l3.5 14h14L27 8H9" stroke="#BBDEFB" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                <circle cx="13.5" cy="27" r="2" fill="#00BFA5"/>
                <circle cx="23" cy="27" r="2" fill="#00BFA5"/>
              </svg>
            </div>
          </div>
          <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.3px' }}>
            NovaCart
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>
            Sign in to your account
          </div>
        </div>

        <hr style={{ border: 'none', borderTop: '1px solid var(--border)', marginBottom: 24 }} />

        <form onSubmit={handleSubmit}>

          {/* Email */}
          <div style={{ marginBottom: 16 }}>
            <label htmlFor="login-email" style={{
              display: 'block', fontSize: 13, fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 6,
            }}>
              Email address
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              style={{
                width: '100%', padding: '9px 12px', fontSize: 14,
                fontFamily: 'inherit', color: 'var(--text-primary)',
                background: 'var(--bg-primary)', border: '1px solid var(--border)',
                borderRadius: 6,
              }}
            />
          </div>

          {/* Password */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <label htmlFor="login-password" style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>
                Password
              </label>
              <a href="#" style={{ fontSize: 12, color: 'var(--accent)', textDecoration: 'none' }}>
                Forgot password?
              </a>
            </div>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              style={{
                width: '100%', padding: '9px 12px', fontSize: 14,
                fontFamily: 'inherit', color: 'var(--text-primary)',
                background: 'var(--bg-primary)', border: '1px solid var(--border)',
                borderRadius: 6,
              }}
            />
          </div>

          {/* Error message */}
          {error && (
            <div role="alert" style={{ color: '#C62828', background: '#FFEBEE', border: '1px solid #FFCDD2', borderRadius: 6, padding: '9px 12px', fontSize: 13, marginBottom: 16 }}>
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            className="btn-apply"
            disabled={loading}
            style={{ width: '100%', padding: '10px', fontSize: 14, borderRadius: 6, opacity: loading ? 0.7 : 1 }}
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>

        </form>

        <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-muted)', marginTop: 20 }}>
          Don't have an account?{' '}
          <a href="#" style={{ color: 'var(--accent)', textDecoration: 'none' }}>Sign up</a>
        </p>

      </div>
    </div>
  );
}
