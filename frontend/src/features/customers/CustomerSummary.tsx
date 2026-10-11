import { Grid } from "@mui/material";
import PeopleAltOutlinedIcon from "@mui/icons-material/PeopleAltOutlined";
import BoltOutlinedIcon from "@mui/icons-material/BoltOutlined";
import RepeatOutlinedIcon from "@mui/icons-material/RepeatOutlined";
import PaidOutlinedIcon from "@mui/icons-material/PaidOutlined";

import { KpiCard } from "../../components/common/KpiCard";
import { formatCurrency, formatNumber } from "../../lib/format";
import type { CustomerTotals } from "../../types/api";

interface Props {
  totals: CustomerTotals | undefined;
  loading: boolean;
}

export function CustomerSummary({ totals, loading }: Props) {
  const currency = totals?.currency ?? "KES";

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Total customers"
          value={formatNumber(totals?.total_customers ?? 0)}
          secondary="All registered"
          icon={<PeopleAltOutlinedIcon fontSize="small" />}
          accent="#4F46E5"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Active"
          value={formatNumber(totals?.active_customers ?? 0)}
          secondary="Purchased in last 30 days"
          icon={<BoltOutlinedIcon fontSize="small" />}
          accent="#16A34A"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Repeat"
          value={formatNumber(totals?.repeat_customers ?? 0)}
          secondary="2 or more orders"
          icon={<RepeatOutlinedIcon fontSize="small" />}
          accent="#0EA5E9"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Avg value"
          value={formatCurrency(totals?.avg_customer_value, currency, true)}
          secondary="Lifetime revenue per customer"
          icon={<PaidOutlinedIcon fontSize="small" />}
          accent="#D97706"
          loading={loading}
        />
      </Grid>
    </Grid>
  );
}
