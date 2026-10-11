import { useEffect, useState } from 'react';

import { fetchCashflowForecast, type CashflowQuery } from '../api/cashflow';
import type { CashflowForecastResponse } from '../types/api';

interface State {
  data: CashflowForecastResponse | null;
  loading: boolean;
  error: string | null;
}

export function useCashflowForecast(query: CashflowQuery = {}): State {
  const [state, setState] = useState<State>({
    data: null,
    loading: true,
    error: null,
  });

  const { horizon_days, currency } = query;

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));

    fetchCashflowForecast({ horizon_days, currency })
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((err: Error) => {
        if (!cancelled)
          setState({ data: null, loading: false, error: err.message });
      });

    return () => {
      cancelled = true;
    };
  }, [horizon_days, currency]);

  return state;
}