export const SEGMENT_COLORS: Record<string, string> = {
  'High Value': '#4F46E5',
  Loyal: '#16A34A',
  'At Risk': '#D97706',
  New: '#0EA5E9',
  Inactive: '#94A3B8',
};

export const SEGMENT_ORDER = [
  'High Value',
  'Loyal',
  'At Risk',
  'New',
  'Inactive',
] as const;

export function segmentColor(segment: string): string {
  return SEGMENT_COLORS[segment] ?? '#64748B';
}