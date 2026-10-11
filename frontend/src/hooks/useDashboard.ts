import { useEffect, useState } from 'react';

import { fetchDashboard, type DashboardQuery } from '../api/dashboard';
import type { DashboardResponse } from '../types/api';

interface State {
  data: DashboardResponse | null;
  loading: boolean;
  error: string | null;
}

export function useDashboard(query: DashboardQuery): State & { refresh: () => void } {
  const [state, setState] = useState<State>({
    data: null,
    loading: true,
    error: null,
  });
  const [tick, setTick] = useState(0);

  const { date_from, date_to, branch_id, currency } = query;

  useEffect(() => {
    let cancelled = false;

    setState((s) => ({ ...s, loading: true, error: null }));

    fetchDashboard({ date_from, date_to, branch_id, currency })
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((err: Error) => {
        if (!cancelled) setState({ data: null, loading: false, error: err.message });
      });

    return () => {
      cancelled = true;
    };
  }, [date_from, date_to, branch_id, currency, tick]);

  return { ...state, refresh: () => setTick((t) => t + 1) };
}