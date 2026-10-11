import { useEffect, useState } from 'react';

import { fetchDemandForecast, type DemandForecastQuery } from '../api/forecast';
import type { DemandForecastResponse } from '../types/api';

interface State {
  data: DemandForecastResponse | null;
  loading: boolean;
  error: string | null;
}

export function useDemandForecast(query: DemandForecastQuery | null): State {
  const [state, setState] = useState<State>({
    data: null,
    loading: false,
    error: null,
  });

  const { product_id, location_id, horizon_days, history_days } = query ?? {};

  useEffect(() => {
    if (!product_id || !location_id) {
      setState({ data: null, loading: false, error: null });
      return;
    }

    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));

    fetchDemandForecast({ product_id, location_id, horizon_days, history_days })
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
  }, [product_id, location_id, horizon_days, history_days]);

  return state;
}