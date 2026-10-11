import { apiGet } from './client';
import type { InventoryResponse } from '../types/api';

export interface InventoryQuery {
  branch_id?: string;
  risk?: string;
  category?: string;
  search?: string;
  currency?: string;
}

export function fetchInventory(q: InventoryQuery = {}): Promise<InventoryResponse> {
  return apiGet<InventoryResponse>('/inventory', {
    branch_id: q.branch_id,
    risk: q.risk,
    category: q.category,
    search: q.search,
    currency: q.currency,
  });
}