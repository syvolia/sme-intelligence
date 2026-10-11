import { Box, Card, Chip, Grid, Stack, Typography } from "@mui/material";
import EmojiEventsOutlinedIcon from "@mui/icons-material/EmojiEventsOutlined";
import WarningAmberOutlinedIcon from "@mui/icons-material/WarningAmberOutlined";

import { StatusPill } from "../../components/common/StatusPill";
import type { SupplierRow, SupplierSummary } from "../../types/api";

interface Props {
  summary: SupplierSummary | undefined;
  suppliers: SupplierRow[];
  loading: boolean;
}

function reliabilityTone(tier: string) {
  if (tier === "Excellent") return "healthy" as const;
  if (tier === "Good") return "info" as const;
  if (tier === "Fair") return "low" as const;
  return "critical" as const;
}

function HighlightCard({
  supplier,
  label,
  accent,
  icon,
}: {
  supplier: SupplierRow | undefined;
  label: string;
  accent: string;
  icon: React.ReactNode;
}) {
  if (!supplier) return null;

  return (
    <Card
      sx={{
        p: 2.5,
        borderLeft: `4px solid ${accent}`,
      }}
    >
      <Stack spacing={1.5}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Box
            sx={{
              width: 28,
              height: 28,
              borderRadius: 1.5,
              backgroundColor: `${accent}14`,
              color: accent,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {icon}
          </Box>
          <Typography
            variant="subtitle2"
            color="text.secondary"
            sx={{ fontSize: 10, letterSpacing: "0.12em" }}
          >
            {label}
          </Typography>
        </Box>

        <Box>
          <Typography
            sx={{ fontSize: 15, fontWeight: 700, lineHeight: 1.2, mb: 0.5 }}
          >
            {supplier.supplier}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {supplier.orders} POs · {supplier.avg_delivery_days.toFixed(1)} days
            avg
          </Typography>
        </Box>

        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <StatusPill
            tone={reliabilityTone(supplier.tier)}
            label={supplier.tier}
          />
          <Typography
            sx={{
              fontSize: 20,
              fontWeight: 700,
              fontVariantNumeric: "tabular-nums",
              color: accent,
            }}
          >
            {supplier.reliability.toFixed(1)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            / 100
          </Typography>
          {supplier.trend === "degrading" && (
            <Chip
              label="Degrading"
              size="small"
              color="error"
              variant="outlined"
              sx={{ height: 20, fontSize: 10, fontWeight: 700, ml: "auto" }}
            />
          )}
        </Box>
      </Stack>
    </Card>
  );
}

export function SupplierHighlights({ summary, suppliers, loading }: Props) {
  if (loading) return null;

  const best = suppliers.find((s) => s.supplier === summary?.best_supplier);
  const worst = suppliers.find((s) => s.supplier === summary?.worst_supplier);
  const degrading = suppliers.find((s) => s.trend === "degrading");

  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <HighlightCard
          supplier={best}
          label="Top performer"
          accent="#16A34A"
          icon={<EmojiEventsOutlinedIcon fontSize="small" />}
        />
      </Grid>
      <Grid item xs={12} md={6}>
        <HighlightCard
          supplier={degrading ?? worst}
          label={degrading ? "Degrading supplier" : "Needs attention"}
          accent="#DC2626"
          icon={<WarningAmberOutlinedIcon fontSize="small" />}
        />
      </Grid>
    </Grid>
  );
}
