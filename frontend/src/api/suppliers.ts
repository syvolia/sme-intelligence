import { apiGet } from './client';
import type { SuppliersResponse } from '../types/api';

export function fetchSuppliers(currency = 'KES'): Promise<SuppliersResponse> {
  return apiGet<SuppliersResponse>('/suppliers', { currency });
}