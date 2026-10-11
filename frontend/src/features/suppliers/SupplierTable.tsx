import { useMemo, useState } from "react";
import {
  Box,
  Card,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableSortLabel,
  Typography,
  Chip,
} from "@mui/material";
import TrendingDownIcon from "@mui/icons-material/TrendingDown";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import TrendingFlatIcon from "@mui/icons-material/TrendingFlat";

import { StatusPill } from "../../components/common/StatusPill";
import { formatCurrency, formatPercent } from "../../lib/format";
import type { SupplierRow } from "../../types/api";

type SortKey =
  | "supplier"
  | "orders"
  | "avg_delivery_days"
  | "on_time_pct"
  | "recent_on_time_pct"
  | "avg_cost"
  | "reliability";

type SortDir = "asc" | "desc";

interface Props {
  suppliers: SupplierRow[];
  currency: string;
  loading: boolean;
}

function compare(a: SupplierRow, b: SupplierRow, key: SortKey): number {
  switch (key) {
    case "supplier":
      return a.supplier.localeCompare(b.supplier);
    case "orders":
      return a.orders - b.orders;
    case "avg_delivery_days":
      return a.avg_delivery_days - b.avg_delivery_days;
    case "on_time_pct":
      return a.on_time_pct - b.on_time_pct;
    case "recent_on_time_pct":
      return a.recent_on_time_pct - b.recent_on_time_pct;
    case "avg_cost":
      return a.avg_cost - b.avg_cost;
    case "reliability":
      return a.reliability - b.reliability;
    default:
      return 0;
  }
}

function reliabilityTone(tier: string) {
  if (tier === "Excellent") return "healthy" as const;
  if (tier === "Good") return "info" as const;
  if (tier === "Fair") return "low" as const;
  return "critical" as const;
}

function TrendIcon({ trend }: { trend: SupplierRow["trend"] }) {
  if (trend === "degrading")
    return <TrendingDownIcon sx={{ fontSize: 16, color: "error.main" }} />;
  if (trend === "improving")
    return <TrendingUpIcon sx={{ fontSize: 16, color: "success.main" }} />;
  return <TrendingFlatIcon sx={{ fontSize: 16, color: "text.secondary" }} />;
}

export function SupplierTable({ suppliers, currency, loading }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("reliability");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const sorted = useMemo(() => {
    const copy = [...suppliers];
    copy.sort((a, b) => {
      const v = compare(a, b, sortKey);
      return sortDir === "asc" ? v : -v;
    });
    return copy;
  }, [suppliers, sortKey, sortDir]);

  const handleSort = (key: SortKey) => {
    if (key === sortKey) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  const headCell = (
    label: string,
    key: SortKey,
    align: "left" | "right" = "left",
  ) => (
    <TableCell align={align} sx={{ fontWeight: 600, whiteSpace: "nowrap" }}>
      <TableSortLabel
        active={sortKey === key}
        direction={sortKey === key ? sortDir : "asc"}
        onClick={() => handleSort(key)}
      >
        {label}
      </TableSortLabel>
    </TableCell>
  );

  if (loading) {
    return (
      <Card sx={{ p: 3 }}>
        <Skeleton
          variant="rectangular"
          height={60}
          sx={{ borderRadius: 1, mb: 1 }}
        />
        {Array.from({ length: 8 }).map((_, i) => (
          <Skeleton
            key={i}
            variant="rectangular"
            height={44}
            sx={{ borderRadius: 1, mb: 0.5 }}
          />
        ))}
      </Card>
    );
  }

  return (
    <Card sx={{ overflow: "hidden" }}>
      <Box sx={{ px: 3, pt: 2.5, pb: 1.5 }}>
        <Typography variant="h6" sx={{ fontSize: 16 }}>
          Supplier scorecard
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {sorted.length} suppliers · click a column to sort
        </Typography>
      </Box>

      <Box sx={{ overflowX: "auto" }}>
        <Table size="small" sx={{ minWidth: 1080 }}>
          <TableHead>
            <TableRow sx={{ backgroundColor: "#F8FAFC" }}>
              {headCell("Supplier", "supplier")}
              {headCell("Orders", "orders", "right")}
              {headCell("Avg delivery", "avg_delivery_days", "right")}
              {headCell("On-time", "on_time_pct", "right")}
              {headCell("Recent 90d", "recent_on_time_pct", "right")}
              {headCell("Avg cost", "avg_cost", "right")}
              {headCell("Reliability", "reliability")}
            </TableRow>
          </TableHead>
          <TableBody>
            {sorted.map((s) => {
              const isDegrading = s.trend === "degrading";
              const isPoor = s.tier === "Poor" || s.tier === "Fair";

              return (
                <TableRow
                  key={s.supplier_id}
                  sx={{
                    "&:last-child td": { borderBottom: 0 },
                    backgroundColor: isDegrading
                      ? "rgba(220,38,38,0.04)"
                      : isPoor
                      ? "rgba(217,119,6,0.03)"
                      : "transparent",
                    borderLeft: isDegrading
                      ? "3px solid #DC2626"
                      : isPoor
                      ? "3px solid #D97706"
                      : "3px solid transparent",
                    "&:hover": {
                      backgroundColor: isDegrading
                        ? "rgba(220,38,38,0.07)"
                        : isPoor
                        ? "rgba(217,119,6,0.06)"
                        : "#FAFBFC",
                    },
                    transition: "background-color 120ms ease",
                  }}
                >
                  <TableCell>
                    <Typography
                      sx={{ fontSize: 13.5, fontWeight: 600, lineHeight: 1.2 }}
                    >
                      {s.supplier}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {s.country ?? "—"}
                    </Typography>
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums", fontSize: 13 }}
                  >
                    {s.orders}
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums", fontSize: 13 }}
                  >
                    {s.avg_delivery_days.toFixed(1)} d
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{
                      fontVariantNumeric: "tabular-nums",
                      fontSize: 13,
                      fontWeight: 600,
                      color:
                        s.on_time_pct >= 0.9
                          ? "success.main"
                          : s.on_time_pct >= 0.75
                          ? "text.primary"
                          : "warning.main",
                    }}
                  >
                    {formatPercent(s.on_time_pct, 1)}
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{
                      fontVariantNumeric: "tabular-nums",
                      fontSize: 13,
                      fontWeight: 600,
                    }}
                  >
                    <Box
                      sx={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 0.5,
                      }}
                    >
                      <TrendIcon trend={s.trend} />
                      {formatPercent(s.recent_on_time_pct, 1)}
                    </Box>
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums", fontSize: 13 }}
                  >
                    {formatCurrency(s.avg_cost, currency)}
                  </TableCell>

                  <TableCell>
                    <Box
                      sx={{ display: "flex", alignItems: "center", gap: 1.5 }}
                    >
                      <Typography
                        sx={{
                          fontSize: 15,
                          fontWeight: 700,
                          fontVariantNumeric: "tabular-nums",
                          minWidth: 38,
                        }}
                      >
                        {s.reliability.toFixed(1)}
                      </Typography>
                      <StatusPill
                        tone={reliabilityTone(s.tier)}
                        label={s.tier}
                      />
                      {isDegrading && (
                        <Chip
                          label="Degrading"
                          size="small"
                          color="error"
                          variant="outlined"
                          sx={{ height: 20, fontSize: 10, fontWeight: 700 }}
                        />
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </Box>
    </Card>
  );
}
