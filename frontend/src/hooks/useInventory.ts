import { useEffect, useState } from 'react';

import { fetchInventory, type InventoryQuery } from '../api/inventory';
import type { InventoryResponse } from '../types/api';

interface State {
  data: InventoryResponse | null;
  loading: boolean;
  error: string | null;
}

export function useInventory(query: InventoryQuery): State {
  const [state, setState] = useState<State>({
    data: null,
    loading: true,
    error: null,
  });

  const { branch_id, risk, category, search, currency } = query;

  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));

    fetchInventory({ branch_id, risk, category, search, currency })
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
  }, [branch_id, risk, category, search, currency]);

  return state;
}