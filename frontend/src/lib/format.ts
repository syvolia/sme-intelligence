export function formatCurrency(
  amount: number | null | undefined,
  currency: string = 'KES',
  compact: boolean = false,
): string {
  const value = Number(amount ?? 0);
  const symbol = currency === 'USD' ? '$' : 'KES ';

  if (compact) {
    const abs = Math.abs(value);
    if (abs >= 1_000_000_000) return `${symbol}${(value / 1_000_000_000).toFixed(2)}B`;
    if (abs >= 1_000_000) return `${symbol}${(value / 1_000_000).toFixed(2)}M`;
    if (abs >= 1_000) return `${symbol}${(value / 1_000).toFixed(1)}K`;
  }

  return `${symbol}${value.toLocaleString('en-KE', { maximumFractionDigits: 0 })}`;
}

export function formatNumber(n: number | null | undefined): string {
  return Number(n ?? 0).toLocaleString('en-KE');
}

export function formatPercent(n: number | null | undefined, digits = 1): string {
  return `${(Number(n ?? 0) * 100).toFixed(digits)}%`;
}

export function formatDate(
  iso: string,
  opts: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric' },
): string {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('en-KE', opts);
}

export function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function isoDaysAgo(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}