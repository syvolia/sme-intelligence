import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import { SectionCard } from "../../components/common/SectionCard";
import { StatusPill } from "../../components/common/StatusPill";
import { formatCurrency, formatNumber, formatPercent } from "../../lib/format";
import type { SegmentSummary } from "../../types/api";
import { segmentColor } from "./constants";

interface Props {
  segments: SegmentSummary[];
  currency: string;
  loading: boolean;
}

const TONE_FOR_SEGMENT: Record<
  string,
  "healthy" | "low" | "critical" | "info" | "neutral"
> = {
  "High Value": "info",
  Loyal: "healthy",
  "At Risk": "low",
  New: "info",
  Inactive: "neutral",
};

export function SegmentTable({ segments, currency, loading }: Props) {
  return (
    <SectionCard
      title="Segment breakdown"
      subtitle="RFM aggregates per segment"
    >
      {loading ? (
        <Typography variant="body2" color="text.secondary">
          Loading…
        </Typography>
      ) : (
        <Box sx={{ overflowX: "auto", mx: -3 }}>
          <Table size="small" sx={{ minWidth: 620 }}>
            <TableHead>
              <TableRow>
                <TableCell sx={{ pl: 3 }}>Segment</TableCell>
                <TableCell align="right">Customers</TableCell>
                <TableCell align="right">Revenue</TableCell>
                <TableCell align="right">Share</TableCell>
                <TableCell align="right">Avg value</TableCell>
                <TableCell align="right">Avg freq</TableCell>
                <TableCell align="right" sx={{ pr: 3 }}>
                  Avg recency
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {segments.map((s) => (
                <TableRow
                  key={s.segment}
                  sx={{ "&:last-child td": { borderBottom: 0 } }}
                >
                  <TableCell sx={{ pl: 3 }}>
                    <Box
                      sx={{ display: "flex", alignItems: "center", gap: 1.25 }}
                    >
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          backgroundColor: segmentColor(s.segment),
                          flexShrink: 0,
                        }}
                      />
                      <StatusPill
                        tone={TONE_FOR_SEGMENT[s.segment] ?? "neutral"}
                        label={s.segment}
                      />
                    </Box>
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums", fontWeight: 600 }}
                  >
                    {formatNumber(s.count)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums" }}
                  >
                    {formatCurrency(s.revenue, currency, true)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      fontVariantNumeric: "tabular-nums",
                      color: "text.secondary",
                    }}
                  >
                    {formatPercent(s.revenue_share, 1)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums" }}
                  >
                    {formatCurrency(s.avg_monetary, currency, true)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums" }}
                  >
                    {s.avg_frequency.toFixed(1)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ pr: 3, fontVariantNumeric: "tabular-nums" }}
                  >
                    {s.avg_recency_days.toFixed(0)} d
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      )}
    </SectionCard>
  );
}
