import { useEffect, useState } from 'react';

import { fetchBranches, fetchCustomers, fetchProducts } from '../api/meta';
import type { BranchOption, CustomerOption, ProductOption } from '../types/api';

interface MetaState {
  branches: BranchOption[];
  products: ProductOption[];
  customers: CustomerOption[];
  loading: boolean;
  error: string | null;
}

export function useMeta(): MetaState {
  const [state, setState] = useState<MetaState>({
    branches: [],
    products: [],
    customers: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;

    Promise.all([fetchBranches(), fetchProducts(), fetchCustomers()])
      .then(([branches, products, customers]) => {
        if (!cancelled)
          setState({ branches, products, customers, loading: false, error: null });
      })
      .catch((err: Error) => {
        if (!cancelled)
          setState((s) => ({ ...s, loading: false, error: err.message }));
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return state;
}