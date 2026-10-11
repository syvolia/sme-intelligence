import type { RecommendationType } from '../../types/api';

export const TYPE_META: Record<
  RecommendationType,
  { label: string; color: string; icon: string }
> = {
  inventory: { label: 'Inventory', color: '#4F46E5', icon: '📦' },
  cashflow: { label: 'Cash flow', color: '#DC2626', icon: '💰' },
  pricing: { label: 'Pricing', color: '#D97706', icon: '🏷️' },
  customer: { label: 'Customer', color: '#0EA5E9', icon: '👥' },
  supplier: { label: 'Supplier', color: '#7C3AED', icon: '🚚' },
};

export const TYPE_ORDER: RecommendationType[] = [
  'inventory',
  'cashflow',
  'pricing',
  'customer',
  'supplier',
];

export const PRIORITY_META: Record<
  'high' | 'medium' | 'low',
  { label: string; bg: string; fg: string; dot: string }
> = {
  high: { label: 'High priority', bg: '#FEE2E2', fg: '#991B1B', dot: '#DC2626' },
  medium: { label: 'Medium', bg: '#FEF3C7', fg: '#92400E', dot: '#D97706' },
  low: { label: 'Low', bg: '#E0E7FF', fg: '#3730A3', dot: '#4F46E5' },
};