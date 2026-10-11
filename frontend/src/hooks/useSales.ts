import { useEffect, useState } from 'react';

import { fetchSales, type SalesQuery } from '../api/sales';
import type { SalesResponse } from '../types/api';

interface State {
  data: SalesResponse | null;
  loading: boolean;
  error: string | null;
}

export function useSales(query: SalesQuery): State {
  const [state, setState] = useState<State>({
    data: null,
    loading: true,
    error: null,
  });

  const { date_from, date_to, branch_id, product_id, customer_id, currency } = query;

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));

    fetchSales({ date_from, date_to, branch_id, product_id, customer_id, currency })
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
  }, [date_from, date_to, branch_id, product_id, customer_id, currency]);

  return state;
}