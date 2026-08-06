/**
 * ServiceStatus.test.jsx — Tests for the ServiceStatus component.
 *
 * getHealth is mocked at the module level so no real fetch is made.
 * Each test controls what getHealth resolves/rejects with.
 */

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, afterEach } from 'vitest';

// Mock the api module before importing the component
vi.mock('../utils/api', () => ({
  getHealth: vi.fn(),
}));

import { getHealth } from '../utils/api';
import ServiceStatus from './ServiceStatus';

afterEach(() => {
  vi.clearAllMocks();
});

// ── Smoke test ────────────────────────────────────────────────────────────────

describe('ServiceStatus', () => {
  it('renders without crashing', () => {
    getHealth.mockResolvedValue({ status: 'healthy', database: { status: 'connected' } });
    render(<ServiceStatus />);
  });

  // ── Loading / checking state ─────────────────────────────────────────────────

  it('renders "Checking…" before the health response resolves', () => {
    // Return a never-resolving promise so the component stays in loading state
    getHealth.mockReturnValue(new Promise(() => {}));
    render(<ServiceStatus />);
    expect(screen.getByText('Checking…')).toBeInTheDocument();
  });

  // ── Healthy state ─────────────────────────────────────────────────────────────

  it('renders "Service healthy" when status is healthy', async () => {
    getHealth.mockResolvedValue({ status: 'healthy', database: { status: 'connected' } });
    render(<ServiceStatus />);
    await waitFor(() => {
      expect(screen.getByText('Service healthy')).toBeInTheDocument();
    });
  });

  // ── Degraded state ────────────────────────────────────────────────────────────

  it('renders "Degraded" when status is degraded', async () => {
    getHealth.mockResolvedValue({ status: 'degraded', database: { status: 'error' } });
    render(<ServiceStatus />);
    await waitFor(() => {
      expect(screen.getByText('Degraded')).toBeInTheDocument();
    });
  });

  // ── Error state ───────────────────────────────────────────────────────────────

  it('renders "Offline" when getHealth throws', async () => {
    getHealth.mockRejectedValue(new Error('Network error'));
    render(<ServiceStatus />);
    await waitFor(() => {
      expect(screen.getByText('Offline')).toBeInTheDocument();
    });
  });

  it('shows title="Backend unreachable" when getHealth throws', async () => {
    getHealth.mockRejectedValue(new Error('Network error'));
    const { container } = render(<ServiceStatus />);
    await waitFor(() => {
      expect(container.firstChild).toHaveAttribute('title', 'Backend unreachable');
    });
  });
});
