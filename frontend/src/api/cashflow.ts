import { apiGet } from './client';
import type { CashflowForecastResponse } from '../types/api';

export interface CashflowQuery {
  horizon_days?: number;
  currency?: string;
}

export function fetchCashflowForecast(
  q: CashflowQuery = {},
): Promise<CashflowForecastResponse> {
  return apiGet<CashflowForecastResponse>('/forecast/cashflow', {
    horizon_days: q.horizon_days,
    currency: q.currency,
  });
}