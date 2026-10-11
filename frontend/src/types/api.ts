export interface DashboardKpis {
  revenue: number;
  gross_profit: number;
  inventory_value: number;
  outstanding_payments: number;
  cash_balance: number;
  currency: string;
}

export interface RevenuePoint {
  date: string;
  value: number;
}

export interface CashflowPoint {
  date: string;
  balance: number;
  lower: number;
  upper: number;
}

export interface InventoryRiskItem {
  product_id: string;
  product: string;
  branch_id: string;
  branch: string;
  current_stock: number;
  daily_demand: number;
  days_remaining: number;
  reorder_point: number;
  risk: 'LOW' | 'MEDIUM' | 'HIGH';
}

export interface RecommendationSummary {
  id: string;
  type: 'inventory' | 'cashflow' | 'pricing' | 'customer' | 'supplier' | string;
  title: string;
  priority: 'low' | 'medium' | 'high';
}

export interface DashboardResponse {
  kpis: DashboardKpis;
  revenue_trend: RevenuePoint[];
  cashflow_forecast: CashflowPoint[];
  inventory_risk: InventoryRiskItem[];
  recommendations: RecommendationSummary[];
}

export interface BranchOption {
  id: string;
  name: string;
}
// ---------------------------------------------------------------------------
// Meta options (filter dropdowns)
// ---------------------------------------------------------------------------
export interface ProductOption {
  id: string;
  name: string;
  sku: string;
  category?: string;
}

export interface CustomerOption {
  id: string;
  name: string;
  phone?: string;
}

// ---------------------------------------------------------------------------
// Sales analytics
// ---------------------------------------------------------------------------
export interface SalesKpis {
  revenue: number;
  orders: number;
  avg_order_value: number;
  gross_margin: number;
  currency: string;
}

export interface TimePoint {
  date: string;
  value: number;
}

export interface ProductRevenue {
  product_id: string;
  product: string;
  category?: string;
  revenue: number;
  units: number;
}

export interface CategoryRevenue {
  category: string;
  revenue: number;
}

export interface LocationRevenue {
  location_id: string;
  location: string;
  revenue: number;
}

export interface SalesResponse {
  kpis: SalesKpis;
  revenue_over_time: TimePoint[];
  revenue_by_product: ProductRevenue[];
  revenue_by_category: CategoryRevenue[];
  revenue_by_location: LocationRevenue[];
  top_products: ProductRevenue[];
  bottom_products: ProductRevenue[];
}
// ---------------------------------------------------------------------------
// Inventory
// ---------------------------------------------------------------------------
export type InventoryRisk = 'HEALTHY' | 'LOW' | 'CRITICAL';

export interface InventoryItem {
  product_id: string;
  sku: string;
  product: string;
  category?: string;
  unit?: string;

  branch_id: string;
  branch: string;

  supplier_id?: string;
  supplier?: string;

  current_stock: number;
  daily_demand: number;
  units_last_30d: number;
  days_remaining: number | null;
  lead_time_days: number;
  lead_time_demand: number;
  reorder_point: number;
  risk: InventoryRisk;
}

export interface InventorySummary {
  total_skus: number;
  healthy: number;
  low: number;
  critical: number;
  total_inventory_value: number;
  currency: string;
}

export interface InventoryResponse {
  summary: InventorySummary;
  items: InventoryItem[];
}

// ---------------------------------------------------------------------------
// Demand forecast
// ---------------------------------------------------------------------------
export interface DemandHistoryPoint {
  date: string;
  value: number;
}

export interface DemandForecastPoint {
  date: string;
  value: number;
  lower: number;
  upper: number;
}

export interface ForecastMetrics {
  model: string;
  mae: number;
  rmse: number;
  mape: number;
}

export interface DemandForecastResponse {
  product_id: string;
  product: string;
  location_id: string;
  location: string;
  horizon_days: number;
  history: DemandHistoryPoint[];
  forecast: DemandForecastPoint[];
  metrics: ForecastMetrics;
}

// ---------------------------------------------------------------------------
// Cash-flow forecast
// ---------------------------------------------------------------------------
export interface CashflowPoint {
  date: string;
  balance: number;
  lower: number;
  upper: number;
  inflow: number;
  outflow: number;
}

export interface CashflowSummary {
  current_cash: number;
  expected_income: number;
  expected_expenses: number;
  predicted_min_balance: number;
  min_safe_balance: number;
  currency: string;
}

export interface ShortageAlert {
  predicted_date: string;
  expected_minimum: number;
  minimum_safe_balance: number;
  recommendation: string;
}

export interface CashflowForecastResponse {
  summary: CashflowSummary;
  forecast: CashflowPoint[];
  alert: ShortageAlert | null;
}

// ---------------------------------------------------------------------------
// Customers (RFM)
// ---------------------------------------------------------------------------
export interface CustomerTotals {
  total_customers: number;
  active_customers: number;
  repeat_customers: number;
  avg_customer_value: number;
  currency: string;
}

export interface SegmentSummary {
  segment: string;
  count: number;
  revenue: number;
  revenue_share: number;
  avg_monetary: number;
  avg_frequency: number;
  avg_recency_days: number;
}

export interface CustomerScatterPoint {
  customer_id: string;
  name?: string;
  segment: string;
  recency_days: number;
  frequency: number;
  monetary: number;
}

export interface CustomerListRow {
  customer_id: string;
  name?: string;
  segment: string;
  recency_days: number;
  frequency: number;
  monetary: number;
  r_score: number;
  f_score: number;
  m_score: number;
}

export interface CustomersResponse {
  totals: CustomerTotals;
  segments: SegmentSummary[];
  scatter: CustomerScatterPoint[];
  top_customers: CustomerListRow[];
}

// ---------------------------------------------------------------------------
// Suppliers
// ---------------------------------------------------------------------------
export interface SupplierRow {
  supplier_id: string;
  supplier: string;
  country?: string;
  orders: number;
  received_orders: number;
  avg_delivery_days: number;
  avg_lateness_days: number;
  on_time_pct: number;
  recent_on_time_pct: number;
  avg_cost: number;
  total_spend: number;
  reliability: number;
  trend: 'improving' | 'stable' | 'degrading';
  tier: 'Excellent' | 'Good' | 'Fair' | 'Poor';
}

export interface SupplierSummary {
  total_suppliers: number;
  avg_reliability: number;
  avg_on_time_pct: number;
  best_supplier?: string;
  worst_supplier?: string;
  at_risk_count: number;
  currency: string;
}

export interface SuppliersResponse {
  summary: SupplierSummary;
  suppliers: SupplierRow[];
}

// ---------------------------------------------------------------------------
// Recommendations
// ---------------------------------------------------------------------------
export type RecommendationType =
  | 'inventory'
  | 'cashflow'
  | 'pricing'
  | 'customer'
  | 'supplier';

export type RecommendationPriority = 'high' | 'medium' | 'low';

export interface Recommendation {
  id: string;
  type: RecommendationType;
  priority: RecommendationPriority;
  priority_score: number;
  title: string;
  problem: string;
  evidence: string;
  recommendation: string;
  expected_impact: string;
}

export interface RecommendationTotals {
  total: number;
  high: number;
  medium: number;
  low: number;
  by_type: Record<string, number>;
}

export interface RecommendationsResponse {
  generated_at: string;
  currency: string;
  totals: RecommendationTotals;
  cards: Recommendation[];
}