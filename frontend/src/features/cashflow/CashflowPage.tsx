import {
  Box,
  Card,
  Chip,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { useState } from "react";
import { Alert } from "@mui/material";

import { CashflowKpis } from "./CashflowKpis";
import { CashflowChart } from "./CashflowChart";
import { ShortageAlertCard } from "./ShortageAlertCard";
import { DailyFlowsCard } from "./DailyFlowsCard";
import { useCashflowForecast } from "../../hooks/useCashflowForecast";

const HORIZONS = [14, 30, 60];

export function CashflowPage() {
  const [horizon, setHorizon] = useState<number>(30);
  const { data, loading, error } = useCashflowForecast({
    horizon_days: horizon,
  });

  const currency = data?.summary.currency ?? "KES";
  const minSafe = data?.summary.min_safe_balance ?? 150_000;

  return (
    <Stack spacing={3}>
      <Box
        sx={{
          display: "flex",
          alignItems: { xs: "flex-start", md: "center" },
          justifyContent: "space-between",
          flexDirection: { xs: "column", md: "row" },
          gap: 2,
        }}
      >
        <Box>
          <Typography variant="h5" sx={{ mb: 0.5 }}>
            Cash Flow Intelligence
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Projected cash position with shortage alerts and recommended
            actions.
          </Typography>
        </Box>

        <Stack direction="row" spacing={1.5} alignItems="center">
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ fontWeight: 600 }}
          >
            Horizon
          </Typography>
          <ToggleButtonGroup
            size="small"
            exclusive
            value={horizon}
            onChange={(_, v) => v && setHorizon(v)}
          >
            {HORIZONS.map((h) => (
              <ToggleButton
                key={h}
                value={h}
                sx={{ px: 2, py: 0.5, fontSize: 12, fontWeight: 600 }}
              >
                {h}d
              </ToggleButton>
            ))}
          </ToggleButtonGroup>
        </Stack>
      </Box>

      {error && (
        <Alert severity="error" variant="outlined">
          Failed to load cash-flow forecast: {error}
        </Alert>
      )}

      {data?.alert && (
        <ShortageAlertCard alert={data.alert} currency={currency} />
      )}

      {!data?.alert && !loading && data && (
        <Card
          sx={{
            p: 2.5,
            borderColor: "#BBF7D0",
            backgroundColor: "#F0FDF4",
            borderLeft: "4px solid #16A34A",
          }}
        >
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <Chip
              size="small"
              label="Stable"
              color="success"
              sx={{ fontWeight: 700, height: 22, fontSize: 11 }}
            />
            <Typography
              sx={{ fontSize: 13.5, color: "#166534", fontWeight: 500 }}
            >
              No projected breach of the minimum safe balance in the next{" "}
              {horizon} days.
            </Typography>
          </Stack>
        </Card>
      )}

      <CashflowKpis summary={data?.summary} loading={loading} />

      <Card sx={{ p: 3 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ fontSize: 16 }}>
            Projected cash balance
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Median projection with an 80 % confidence interval, over the next{" "}
            {horizon} days.
          </Typography>
        </Box>
        <CashflowChart
          data={data?.forecast ?? []}
          minSafe={minSafe}
          currency={currency}
          loading={loading}
          height={380}
        />
      </Card>

      <DailyFlowsCard
        data={data?.forecast ?? []}
        currency={currency}
        loading={loading}
      />
    </Stack>
  );
}
