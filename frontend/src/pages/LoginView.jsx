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
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
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

        {/* Logo / Brand */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>🛒</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.3px' }}>
            NovaCart
          </div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4 }}>
            Sign in to your dashboard
          </div>
        </div>

        <hr style={{ border: 'none', borderTop: '1px solid var(--border)', marginBottom: 24 }} />

        <form onSubmit={handleSubmit}>

          {/* Email */}
          <div style={{ marginBottom: 16 }}>
            <label style={{
              display: 'block', fontSize: 13, fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 6,
            }}>
              Email address
            </label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              style={{
                width: '100%', padding: '9px 12px', fontSize: 14,
                fontFamily: 'inherit', color: 'var(--text-primary)',
                background: 'var(--bg-primary)', border: '1px solid var(--border)',
                borderRadius: 6, outline: 'none',
              }}
            />
          </div>

          {/* Password */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)' }}>
                Password
              </label>
              <a href="#" style={{ fontSize: 12, color: 'var(--accent)', textDecoration: 'none' }}>
                Forgot password?
              </a>
            </div>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              style={{
                width: '100%', padding: '9px 12px', fontSize: 14,
                fontFamily: 'inherit', color: 'var(--text-primary)',
                background: 'var(--bg-primary)', border: '1px solid var(--border)',
                borderRadius: 6, outline: 'none',
              }}
            />
          </div>

          {/* Error message */}
          {error && (
            <div style={{ color: '#C62828', background: '#FFEBEE', border: '1px solid #FFCDD2', borderRadius: 6, padding: '9px 12px', fontSize: 13, marginBottom: 16 }}>
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
