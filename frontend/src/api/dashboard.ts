import { apiGet } from './client';
import type { DashboardResponse } from '../types/api';

export interface DashboardQuery {
  date_from?: string;
  date_to?: string;
  branch_id?: string;
  currency?: string;
}

export function fetchDashboard(query: DashboardQuery = {}): Promise<DashboardResponse> {
  return apiGet<DashboardResponse>('/dashboard', {
    date_from: query.date_from,
    date_to: query.date_to,
    branch_id: query.branch_id,
    currency: query.currency,
  });
}