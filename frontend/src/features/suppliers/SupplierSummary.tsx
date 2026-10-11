import { Grid } from "@mui/material";
import LocalShippingOutlinedIcon from "@mui/icons-material/LocalShippingOutlined";
import VerifiedOutlinedIcon from "@mui/icons-material/VerifiedOutlined";
import AccessTimeOutlinedIcon from "@mui/icons-material/AccessTimeOutlined";
import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";

import { KpiCard } from "../../components/common/KpiCard";
import { formatNumber, formatPercent } from "../../lib/format";
import type { SupplierSummary as Summary } from "../../types/api";

interface Props {
  summary: Summary | undefined;
  loading: boolean;
}

export function SupplierSummary({ summary, loading }: Props) {
  const atRisk = summary?.at_risk_count ?? 0;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Total suppliers"
          value={formatNumber(summary?.total_suppliers ?? 0)}
          secondary="In the network"
          icon={<LocalShippingOutlinedIcon fontSize="small" />}
          accent="#4F46E5"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Avg reliability"
          value={summary ? `${summary.avg_reliability.toFixed(1)}` : "—"}
          secondary="Composite score / 100"
          icon={<VerifiedOutlinedIcon fontSize="small" />}
          accent="#16A34A"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="Avg on-time"
          value={summary ? formatPercent(summary.avg_on_time_pct, 1) : "—"}
          secondary="Across all POs"
          icon={<AccessTimeOutlinedIcon fontSize="small" />}
          accent="#0EA5E9"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <KpiCard
          label="At risk"
          value={formatNumber(atRisk)}
          secondary="Reliability below 75"
          icon={<WarningAmberOutlinedIcon fontSize="small" />}
          accent={atRisk > 0 ? "#DC2626" : "#16A34A"}
          loading={loading}
        />
      </Grid>
    </Grid>
  );
}
