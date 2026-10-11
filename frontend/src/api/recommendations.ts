import { apiGet } from './client';
import type { RecommendationsResponse } from '../types/api';

export function fetchRecommendations(currency = 'KES'): Promise<RecommendationsResponse> {
  return apiGet<RecommendationsResponse>('/recommendations', { currency });
}