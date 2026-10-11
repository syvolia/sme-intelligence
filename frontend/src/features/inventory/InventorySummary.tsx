import { Box, Card, Grid, Stack, Typography } from "@mui/material";

import { formatCurrency, formatNumber } from "../../lib/format";
import type { InventorySummary as Summary } from "../../types/api";

interface Props {
  summary: Summary | undefined;
  loading: boolean;
  activeRisk: string;
  onRiskClick: (risk: string) => void;
}

interface StatProps {
  label: string;
  value: string;
  tone: "neutral" | "healthy" | "low" | "critical";
  active: boolean;
  onClick?: () => void;
}

const TONE_STYLE: Record<
  StatProps["tone"],
  { accent: string; bg: string; fg: string }
> = {
  neutral: { accent: "#0F172A", bg: "#0F172A", fg: "#FFFFFF" },
  healthy: { accent: "#16A34A", bg: "#DCFCE7", fg: "#166534" },
  low: { accent: "#D97706", bg: "#FEF3C7", fg: "#92400E" },
  critical: { accent: "#DC2626", bg: "#FEE2E2", fg: "#991B1B" },
};

function Stat({ label, value, tone, active, onClick }: StatProps) {
  const style = TONE_STYLE[tone];
  const interactive = Boolean(onClick);

  return (
    <Card
      onClick={onClick}
      sx={{
        p: 2,
        height: "100%",
        cursor: interactive ? "pointer" : "default",
        borderColor: active ? style.accent : "#EAECEF",
        boxShadow: active ? `0 0 0 1px ${style.accent}` : undefined,
        transition: "all 140ms ease",
        "&:hover": interactive
          ? { borderColor: style.accent, transform: "translateY(-1px)" }
          : undefined,
      }}
    >
      <Stack spacing={1}>
        <Typography
          variant="subtitle2"
          color="text.secondary"
          sx={{ fontSize: 10, letterSpacing: "0.1em" }}
        >
          {label}
        </Typography>
        <Box sx={{ display: "flex", alignItems: "baseline", gap: 1 }}>
          <Typography
            sx={{
              fontSize: { xs: 22, md: 26 },
              fontWeight: 700,
              letterSpacing: "-0.02em",
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {value}
          </Typography>
          {tone !== "neutral" && (
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                backgroundColor: style.accent,
                mb: 0.5,
              }}
            />
          )}
        </Box>
      </Stack>
    </Card>
  );
}

export function InventorySummary({
  summary,
  loading,
  activeRisk,
  onRiskClick,
}: Props) {
  const fmt = (n: number | undefined) => (loading ? "—" : formatNumber(n ?? 0));

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} sm={6} md={3}>
        <Stat
          label="Total SKUs"
          value={fmt(summary?.total_skus)}
          tone="neutral"
          active={activeRisk === ""}
          onClick={() => onRiskClick("")}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Stat
          label="Healthy"
          value={fmt(summary?.healthy)}
          tone="healthy"
          active={activeRisk === "HEALTHY"}
          onClick={() => onRiskClick("HEALTHY")}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Stat
          label="Low"
          value={fmt(summary?.low)}
          tone="low"
          active={activeRisk === "LOW"}
          onClick={() => onRiskClick("LOW")}
        />
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Stat
          label="Critical"
          value={fmt(summary?.critical)}
          tone="critical"
          active={activeRisk === "CRITICAL"}
          onClick={() => onRiskClick("CRITICAL")}
        />
      </Grid>

      <Grid item xs={12}>
        <Card sx={{ p: 2, display: "flex", alignItems: "center", gap: 2 }}>
          <Typography
            variant="subtitle2"
            color="text.secondary"
            sx={{ fontSize: 11 }}
          >
            Total inventory value (at cost)
          </Typography>
          <Box sx={{ flex: 1 }} />
          <Typography
            sx={{
              fontSize: 18,
              fontWeight: 700,
              fontVariantNumeric: "tabular-nums",
            }}
          >
            {loading
              ? "—"
              : formatCurrency(
                  summary?.total_inventory_value,
                  summary?.currency ?? "KES",
                )}
          </Typography>
        </Card>
      </Grid>
    </Grid>
  );
}
