import { Box, Chip, Skeleton, Stack, Typography } from "@mui/material";
import TrendingDownOutlinedIcon from "@mui/icons-material/TrendingDownOutlined";

import { SectionCard } from "../../components/common/SectionCard";
import type { CashflowPoint, DashboardKpis } from "../../types/api";
import { formatCurrency, formatDate } from "../../lib/format";

interface Props {
  kpis?: DashboardKpis;
  forecast: CashflowPoint[];
  minSafe?: number;
  loading?: boolean;
}

export function CashflowCard({
  kpis,
  forecast,
  minSafe = 150_000,
  loading = false,
}: Props) {
  const currency = kpis?.currency ?? "KES";
  const current = kpis?.cash_balance ?? 0;

  const shortest = forecast.find((p) => p.balance < minSafe);
  const last = forecast[forecast.length - 1];

  return (
    <SectionCard
      title="Cash-flow forecast"
      subtitle="Next 30 days · placeholder model"
      action={
        <Chip
          size="small"
          label={shortest ? "Attention" : "Stable"}
          color={shortest ? "warning" : "success"}
          variant="outlined"
          sx={{ fontSize: 11, height: 22 }}
        />
      }
    >
      {loading ? (
        <Stack spacing={2}>
          <Box>
            <Skeleton variant="text" width="50%" />
            <Skeleton variant="text" width="70%" height={32} />
          </Box>
          <Box>
            <Skeleton variant="text" width="40%" />
            <Skeleton variant="text" width="60%" height={28} />
          </Box>
        </Stack>
      ) : (
        <Stack spacing={2}>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Current balance
            </Typography>
            <Typography
              sx={{
                fontSize: 22,
                fontWeight: 700,
                fontVariantNumeric: "tabular-nums",
              }}
            >
              {formatCurrency(current, currency)}
            </Typography>
          </Box>

          <Box>
            <Typography variant="caption" color="text.secondary">
              Projected ·{" "}
              {last
                ? formatDate(last.date, { month: "short", day: "numeric" })
                : "—"}
            </Typography>
            <Typography
              sx={{
                fontSize: 18,
                fontWeight: 600,
                fontVariantNumeric: "tabular-nums",
              }}
              color={
                last && last.balance < minSafe ? "error.main" : "text.primary"
              }
            >
              {last ? formatCurrency(last.balance, currency) : "—"}
            </Typography>
          </Box>

          {shortest && (
            <Box
              sx={{
                border: "1px solid #FDE68A",
                backgroundColor: "#FFFBEB",
                borderRadius: 2,
                p: 1.5,
                display: "flex",
                gap: 1.25,
                alignItems: "flex-start",
              }}
            >
              <TrendingDownOutlinedIcon
                fontSize="small"
                sx={{ color: "#D97706", mt: 0.25 }}
              />
              <Box>
                <Typography
                  sx={{ fontSize: 13, fontWeight: 600, color: "#92400E" }}
                >
                  Shortage risk on{" "}
                  {formatDate(shortest.date, { dateStyle: "medium" })}
                </Typography>
                <Typography
                  sx={{ fontSize: 12, color: "#92400E", opacity: 0.85 }}
                >
                  Projected {formatCurrency(shortest.balance, currency)} below
                  minimum {formatCurrency(minSafe, currency)}.
                </Typography>
              </Box>
            </Box>
          )}

          {!shortest && (
            <Typography variant="caption" color="text.secondary">
              No projected breach of the minimum safe balance in the next 30
              days.
            </Typography>
          )}
        </Stack>
      )}
    </SectionCard>
  );
}
