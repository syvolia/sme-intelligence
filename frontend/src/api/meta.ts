import { apiGet } from './client';
import type { BranchOption, CustomerOption, ProductOption } from '../types/api';

export function fetchBranches(): Promise<BranchOption[]> {
  return apiGet<BranchOption[]>('/meta/branches');
}

export function fetchProducts(): Promise<ProductOption[]> {
  return apiGet<ProductOption[]>('/meta/products');
}

export function fetchCustomers(q?: string): Promise<CustomerOption[]> {
  return apiGet<CustomerOption[]>('/meta/customers', { q });
}