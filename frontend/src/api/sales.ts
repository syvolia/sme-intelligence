import { apiGet } from './client';
import type { SalesResponse } from '../types/api';

export interface SalesQuery {
  date_from?: string;
  date_to?: string;
  branch_id?: string;
  product_id?: string;
  customer_id?: string;
  currency?: string;
}

export function fetchSales(q: SalesQuery = {}): Promise<SalesResponse> {
  return apiGet<SalesResponse>('/sales', {
    date_from: q.date_from,
    date_to: q.date_to,
    branch_id: q.branch_id,
    product_id: q.product_id,
    customer_id: q.customer_id,
    currency: q.currency,
  });
}