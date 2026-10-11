import { apiGet } from './client';
import type { CustomersResponse } from '../types/api';

export function fetchCustomers(currency = 'KES'): Promise<CustomersResponse> {
  return apiGet<CustomersResponse>('/customers', { currency });
}