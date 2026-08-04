import React, { useEffect, useState } from 'react';
import { getHealth } from '../utils/api';
import { DatabaseGear } from './Icons';

export default function ServiceStatus() {
  const [status, setStatus] = useState('checking');
  const [detail, setDetail] = useState('');

  async function check() {
    try {
      const data = await getHealth();
      setStatus(data.status === 'healthy' ? 'healthy' : 'degraded');
      setDetail(data.database?.status === 'connected' ? 'Connected' : 'DB issue');
    } catch {
      setStatus('error');
      setDetail('Backend unreachable');
    }
  }

  useEffect(() => {
    check();
    const interval = setInterval(check, 30000);
    return () => clearInterval(interval);
  }, []);

  const colors = { healthy: '#00897B', degraded: '#F9A825', error: '#C62828', checking: '#90A4AE' };
  const labels = { healthy: 'Service healthy', degraded: 'Degraded', error: 'Offline', checking: 'Checking…' };

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }} title={detail}>
      <span style={{ color: colors[status], display: 'flex', alignItems: 'center' }}>
        <DatabaseGear size={14} />
      </span>
      <span style={{ color: colors[status], fontWeight: 500 }}>{labels[status]}</span>
    </div>
  );
}
