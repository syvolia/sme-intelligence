import { Grid } from "@mui/material";
import MonetizationOnOutlinedIcon from "@mui/icons-material/MonetizationOnOutlined";
import ReceiptLongOutlinedIcon from "@mui/icons-material/ReceiptLongOutlined";
import ShoppingBagOutlinedIcon from "@mui/icons-material/ShoppingBagOutlined";
import TrendingUpOutlinedIcon from "@mui/icons-material/TrendingUpOutlined";

import { KpiCard } from "../../components/common/KpiCard";
import { formatCurrency, formatNumber, formatPercent } from "../../lib/format";
import type { SalesKpis as SalesKpisType } from "../../types/api";

interface Props {
  kpis: SalesKpisType | undefined;
  loading: boolean;
}

export function SalesKpis({ kpis, loading }: Props) {
  const currency = kpis?.currency ?? "KES";

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Revenue"
          value={formatCurrency(kpis?.revenue, currency, true)}
          secondary="Gross sales, discounts included"
          icon={<MonetizationOnOutlinedIcon fontSize="small" />}
          accent="#4F46E5"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Orders"
          value={formatNumber(kpis?.orders ?? 0)}
          secondary="Distinct non-cancelled sales"
          icon={<ReceiptLongOutlinedIcon fontSize="small" />}
          accent="#0EA5E9"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Avg order value"
          value={formatCurrency(kpis?.avg_order_value, currency)}
          secondary="Revenue ÷ orders"
          icon={<ShoppingBagOutlinedIcon fontSize="small" />}
          accent="#D97706"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Gross margin"
          value={formatPercent(kpis?.gross_margin ?? 0)}
          secondary="(Revenue − cost) ÷ revenue"
          icon={<TrendingUpOutlinedIcon fontSize="small" />}
          accent="#16A34A"
          loading={loading}
        />
      </Grid>
    </Grid>
  );
}
