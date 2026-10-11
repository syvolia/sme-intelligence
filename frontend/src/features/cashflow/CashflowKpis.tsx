import { Grid } from "@mui/material";
import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import TrendingUpOutlinedIcon from "@mui/icons-material/TrendingUpOutlined";
import TrendingDownOutlinedIcon from "@mui/icons-material/TrendingDownOutlined";
import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";

import { KpiCard } from "../../components/common/KpiCard";
import { formatCurrency } from "../../lib/format";
import type { CashflowSummary } from "../../types/api";

interface Props {
  summary: CashflowSummary | undefined;
  loading: boolean;
}

export function CashflowKpis({ summary, loading }: Props) {
  const currency = summary?.currency ?? "KES";
  const minBelow = summary
    ? summary.predicted_min_balance < summary.min_safe_balance
    : false;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Current cash"
          value={formatCurrency(summary?.current_cash, currency, true)}
          secondary="Across all branches"
          icon={<AccountBalanceWalletOutlinedIcon fontSize="small" />}
          accent="#0F172A"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Expected income"
          value={formatCurrency(summary?.expected_income, currency, true)}
          secondary="Next 30 days"
          icon={<TrendingUpOutlinedIcon fontSize="small" />}
          accent="#16A34A"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Expected expenses"
          value={formatCurrency(summary?.expected_expenses, currency, true)}
          secondary="Next 30 days"
          icon={<TrendingDownOutlinedIcon fontSize="small" />}
          accent="#D97706"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Predicted minimum"
          value={formatCurrency(summary?.predicted_min_balance, currency, true)}
          secondary={`Safe floor: ${formatCurrency(
            summary?.min_safe_balance,
            currency,
            true,
          )}`}
          icon={<WarningAmberOutlinedIcon fontSize="small" />}
          accent={minBelow ? "#DC2626" : "#4F46E5"}
          loading={loading}
        />
      </Grid>
    </Grid>
  );
}
