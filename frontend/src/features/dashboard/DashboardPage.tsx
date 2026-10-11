import { Alert, Box, Grid, Stack, Typography } from "@mui/material";
import MonetizationOnOutlinedIcon from "@mui/icons-material/MonetizationOnOutlined";
import TrendingUpOutlinedIcon from "@mui/icons-material/TrendingUpOutlined";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
import HourglassEmptyOutlinedIcon from "@mui/icons-material/HourglassEmptyOutlined";
import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import { useOutletContext } from "react-router-dom";

import { KpiCard } from "../../components/common/KpiCard";
import { SectionCard } from "../../components/common/SectionCard";
import { RevenueTrendChart } from "../../components/charts/RevenueTrendChart";
import { CashflowCard } from "./CashflowCard";
import { InventoryRiskCard } from "./InventoryRiskCard";
import { RecommendationsCard } from "./RecommendationsCard";
import { useDashboard } from "../../hooks/useDashboard";
import { formatCurrency } from "../../lib/format";
import type { AppShellContext } from "../../types/shell";

export function DashboardPage() {
  const { branchId, dateFrom, dateTo } = useOutletContext<AppShellContext>();
  const { data, loading, error } = useDashboard({
    branch_id: branchId || undefined,
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
  });

  const kpis = data?.kpis;

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          Overview
        </Typography>
        <Typography variant="body2" color="text.secondary">
          A snapshot of your business performance, cash position, and operating
          risks.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" variant="outlined">
          Failed to load dashboard: {error}
        </Alert>
      )}

      {/* KPI ROW */}
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <KpiCard
            label="Revenue"
            value={formatCurrency(kpis?.revenue, kpis?.currency, true)}
            secondary="Selected period"
            icon={<MonetizationOnOutlinedIcon fontSize="small" />}
            accent="#4F46E5"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <KpiCard
            label="Gross profit"
            value={formatCurrency(kpis?.gross_profit, kpis?.currency, true)}
            secondary="Revenue minus cost of goods"
            icon={<TrendingUpOutlinedIcon fontSize="small" />}
            accent="#16A34A"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <KpiCard
            label="Inventory value"
            value={formatCurrency(kpis?.inventory_value, kpis?.currency, true)}
            secondary="At cost price"
            icon={<Inventory2OutlinedIcon fontSize="small" />}
            accent="#0EA5E9"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <KpiCard
            label="Outstanding"
            value={formatCurrency(
              kpis?.outstanding_payments,
              kpis?.currency,
              true,
            )}
            secondary="Pending customer payments"
            icon={<HourglassEmptyOutlinedIcon fontSize="small" />}
            accent="#D97706"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4} lg={2.4}>
          <KpiCard
            label="Cash balance"
            value={formatCurrency(kpis?.cash_balance, kpis?.currency, true)}
            secondary="Across all branches"
            icon={<AccountBalanceWalletOutlinedIcon fontSize="small" />}
            accent="#0F172A"
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* REVENUE TREND */}
      <SectionCard
        title="Revenue trend"
        subtitle="Daily gross revenue for the selected period"
      >
        <RevenueTrendChart
          data={data?.revenue_trend ?? []}
          currency={kpis?.currency ?? "KES"}
          loading={loading}
        />
      </SectionCard>

      {/* LOWER GRID */}
      <Grid container spacing={3}>
        <Grid item xs={12} lg={4}>
          <CashflowCard
            kpis={kpis}
            forecast={data?.cashflow_forecast ?? []}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} lg={4}>
          <InventoryRiskCard
            items={data?.inventory_risk ?? []}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} lg={4}>
          <RecommendationsCard
            items={data?.recommendations ?? []}
            loading={loading}
          />
        </Grid>
      </Grid>
    </Stack>
  );
}
