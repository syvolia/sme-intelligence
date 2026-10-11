import { Grid } from "@mui/material";
import SpeedOutlinedIcon from "@mui/icons-material/SpeedOutlined";
import BarChartOutlinedIcon from "@mui/icons-material/BarChartOutlined";
import PercentOutlinedIcon from "@mui/icons-material/PercentOutlined";

import { KpiCard } from "../../components/common/KpiCard";
import type { ForecastMetrics as Metrics } from "../../types/api";

interface Props {
  metrics: Metrics | undefined;
  loading: boolean;
}

export function ForecastMetrics({ metrics, loading }: Props) {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={4}>
        <KpiCard
          label="MAE"
          value={metrics ? metrics.mae.toFixed(3) : "—"}
          secondary="Mean absolute error · units/day"
          icon={<SpeedOutlinedIcon fontSize="small" />}
          accent="#4F46E5"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <KpiCard
          label="RMSE"
          value={metrics ? metrics.rmse.toFixed(3) : "—"}
          secondary="Root mean squared error · units/day"
          icon={<BarChartOutlinedIcon fontSize="small" />}
          accent="#0EA5E9"
          loading={loading}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <KpiCard
          label="MAPE"
          value={metrics ? `${(metrics.mape * 100).toFixed(1)}%` : "—"}
          secondary="Mean absolute percentage error"
          icon={<PercentOutlinedIcon fontSize="small" />}
          accent="#16A34A"
          loading={loading}
        />
      </Grid>
    </Grid>
  );
}
