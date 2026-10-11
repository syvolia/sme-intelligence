import {
  Box,
  Card,
  Chip,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TableSortLabel,
  Tooltip,
  Typography,
} from "@mui/material";

import {
  StatusPill,
  inventoryRiskLabel,
  inventoryRiskTone,
} from "../../components/common/StatusPill";
import { formatNumber } from "../../lib/format";
import type { InventoryItem } from "../../types/api";
import { useMemo, useState } from "react";

type SortKey =
  | "product"
  | "branch"
  | "current_stock"
  | "daily_demand"
  | "days_remaining"
  | "reorder_point"
  | "supplier"
  | "risk";

type SortDir = "asc" | "desc";

interface Props {
  items: InventoryItem[];
  loading: boolean;
}

const RISK_ORDER: Record<string, number> = {
  CRITICAL: 0,
  LOW: 1,
  HEALTHY: 2,
};

function compare(a: InventoryItem, b: InventoryItem, key: SortKey): number {
  switch (key) {
    case "product":
      return a.product.localeCompare(b.product);
    case "branch":
      return a.branch.localeCompare(b.branch);
    case "current_stock":
      return a.current_stock - b.current_stock;
    case "daily_demand":
      return a.daily_demand - b.daily_demand;
    case "days_remaining": {
      const av = a.days_remaining ?? Number.POSITIVE_INFINITY;
      const bv = b.days_remaining ?? Number.POSITIVE_INFINITY;
      return av - bv;
    }
    case "reorder_point":
      return a.reorder_point - b.reorder_point;
    case "supplier":
      return (a.supplier ?? "").localeCompare(b.supplier ?? "");
    case "risk":
      return (RISK_ORDER[a.risk] ?? 9) - (RISK_ORDER[b.risk] ?? 9);
    default:
      return 0;
  }
}

export function InventoryTable({ items, loading }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("risk");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const sorted = useMemo(() => {
    const copy = [...items];
    copy.sort((a, b) => {
      const v = compare(a, b, sortKey);
      return sortDir === "asc" ? v : -v;
    });
    return copy;
  }, [items, sortKey, sortDir]);

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
            height={40}
            sx={{ borderRadius: 1, mb: 0.5 }}
          />
        ))}
      </Card>
    );
  }

  if (!items.length) {
    return (
      <Card sx={{ p: 5, textAlign: "center", color: "text.secondary" }}>
        No inventory rows match the current filters.
      </Card>
    );
  }

  return (
    <Card sx={{ overflow: "hidden" }}>
      <Box sx={{ overflowX: "auto" }}>
        <Table size="small" sx={{ minWidth: 1080 }}>
          <TableHead>
            <TableRow sx={{ backgroundColor: "#F8FAFC" }}>
              {headCell("Product", "product")}
              {headCell("Branch", "branch")}
              {headCell("Stock", "current_stock", "right")}
              {headCell("Daily demand", "daily_demand", "right")}
              {headCell("Days left", "days_remaining", "right")}
              {headCell("Reorder pt.", "reorder_point", "right")}
              {headCell("Supplier", "supplier")}
              {headCell("Risk", "risk")}
            </TableRow>
          </TableHead>
          <TableBody>
            {sorted.map((item) => {
              const isCritical = item.risk === "CRITICAL";
              const isLow = item.risk === "LOW";

              return (
                <TableRow
                  key={`${item.product_id}-${item.branch_id}`}
                  sx={{
                    "&:last-child td": { borderBottom: 0 },
                    backgroundColor: isCritical
                      ? "rgba(220,38,38,0.04)"
                      : isLow
                      ? "rgba(217,119,6,0.035)"
                      : "transparent",
                    borderLeft: isCritical
                      ? "3px solid #DC2626"
                      : isLow
                      ? "3px solid #D97706"
                      : "3px solid transparent",
                    "&:hover": {
                      backgroundColor: isCritical
                        ? "rgba(220,38,38,0.07)"
                        : isLow
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
                      {item.product}
                    </Typography>
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{
                        fontFamily: "ui-monospace, monospace",
                        fontSize: 10.5,
                      }}
                    >
                      {item.sku}
                      {item.category ? ` · ${item.category}` : ""}
                    </Typography>
                  </TableCell>

                  <TableCell sx={{ fontSize: 13, whiteSpace: "nowrap" }}>
                    {item.branch}
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 600,
                      color: isCritical ? "error.main" : "text.primary",
                    }}
                  >
                    {formatNumber(item.current_stock)}
                    {item.unit ? (
                      <Typography
                        component="span"
                        variant="caption"
                        color="text.secondary"
                        sx={{ ml: 0.5 }}
                      >
                        {item.unit}
                      </Typography>
                    ) : null}
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums", fontSize: 13 }}
                  >
                    {item.daily_demand.toFixed(1)}
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 600,
                      color: isCritical
                        ? "error.main"
                        : isLow
                        ? "warning.main"
                        : "text.primary",
                    }}
                  >
                    {item.days_remaining !== null
                      ? `${item.days_remaining.toFixed(1)} d`
                      : "—"}
                    <Tooltip
                      title={`Lead time: ${
                        item.lead_time_days
                      } days · Lead-time demand: ${item.lead_time_demand.toFixed(
                        0,
                      )}`}
                      placement="top"
                      arrow
                    >
                      <Box
                        component="span"
                        sx={{ ml: 0.5, opacity: 0.5, cursor: "help" }}
                      >
                        ⓘ
                      </Box>
                    </Tooltip>
                  </TableCell>

                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums", fontSize: 13 }}
                  >
                    {formatNumber(item.reorder_point)}
                  </TableCell>

                  <TableCell sx={{ fontSize: 13, color: "text.secondary" }}>
                    {item.supplier ?? "—"}
                  </TableCell>

                  <TableCell>
                    <StatusPill
                      tone={inventoryRiskTone(item.risk)}
                      label={inventoryRiskLabel(item.risk)}
                    />
                    {isCritical && (
                      <Chip
                        label="Act now"
                        size="small"
                        color="error"
                        variant="outlined"
                        sx={{
                          ml: 1,
                          height: 20,
                          fontSize: 10,
                          fontWeight: 700,
                        }}
                      />
                    )}
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
