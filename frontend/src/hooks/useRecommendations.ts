import { useEffect, useState } from 'react';

import { fetchRecommendations } from '../api/recommendations';
import type { RecommendationsResponse } from '../types/api';

interface State {
  data: RecommendationsResponse | null;
  loading: boolean;
  error: string | null;
}

export function useRecommendations(currency = 'KES'): State {
  const [state, setState] = useState<State>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));

    fetchRecommendations(currency)
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
  }, [currency]);

  return state;
}