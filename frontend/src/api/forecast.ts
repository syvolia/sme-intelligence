import { apiGet } from './client';
import type { DemandForecastResponse } from '../types/api';

export interface DemandForecastQuery {
  product_id: string;
  location_id: string;
  horizon_days?: number;
  history_days?: number;
}

export function fetchDemandForecast(
  q: DemandForecastQuery,
): Promise<DemandForecastResponse> {
  return apiGet<DemandForecastResponse>('/forecast/demand', {
    product_id: q.product_id,
    location_id: q.location_id,
    horizon_days: q.horizon_days,
    history_days: q.history_days,
  });
}