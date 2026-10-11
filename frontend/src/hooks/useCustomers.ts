import { useEffect, useState } from 'react';

import { fetchCustomers } from '../api/customers';
import type { CustomersResponse } from '../types/api';

interface State {
  data: CustomersResponse | null;
  loading: boolean;
  error: string | null;
}

export function useCustomers(currency = 'KES'): State {
  const [state, setState] = useState<State>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));

    fetchCustomers(currency)
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