import { Box, Skeleton, Typography } from "@mui/material";
import {
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { SectionCard } from "../../components/common/SectionCard";
import { formatCurrency, formatNumber } from "../../lib/format";
import type { CustomerScatterPoint } from "../../types/api";
import { SEGMENT_ORDER, segmentColor } from "./constants";

interface Props {
  points: CustomerScatterPoint[];
  currency: string;
  loading: boolean;
}

interface Row {
  x: number;
  y: number;
  customer_id: string;
  name?: string;
  segment: string;
  monetary: number;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: Row }>;
  currency: string;
}

function ChartTooltip({ active, payload, currency }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const p = payload[0].payload;
  return (
    <Box
      sx={{
        backgroundColor: "#0F172A",
        color: "#FFFFFF",
        borderRadius: 1.5,
        px: 1.5,
        py: 1,
        fontSize: 12,
        boxShadow: "0 8px 20px rgba(15,23,42,0.25)",
      }}
    >
      <Box sx={{ fontWeight: 700, mb: 0.5 }}>
        {p.name || "Unnamed customer"}
      </Box>
      <Box sx={{ fontSize: 11, opacity: 0.7, mb: 0.5 }}>{p.segment}</Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2 }}>
        <span>Recency</span>
        <span style={{ fontVariantNumeric: "tabular-nums" }}>{p.x} d</span>
      </Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2 }}>
        <span>Frequency</span>
        <span style={{ fontVariantNumeric: "tabular-nums" }}>
          {formatNumber(p.y)}
        </span>
      </Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2 }}>
        <span>Monetary</span>
        <span style={{ fontVariantNumeric: "tabular-nums" }}>
          {formatCurrency(p.monetary, currency, true)}
        </span>
      </Box>
    </Box>
  );
}

export function RfmScatter({ points, currency, loading }: Props) {
  if (loading) {
    return (
      <SectionCard
        title="RFM distribution"
        subtitle="Recency × frequency by segment"
      >
        <Skeleton variant="rectangular" height={380} sx={{ borderRadius: 2 }} />
      </SectionCard>
    );
  }

  if (points.length === 0) {
    return (
      <SectionCard
        title="RFM distribution"
        subtitle="Recency × frequency by segment"
      >
        <Typography variant="body2" color="text.secondary">
          No customer data.
        </Typography>
      </SectionCard>
    );
  }

  // Group points by segment so each gets its own colored series
  const series = SEGMENT_ORDER.map((seg) => ({
    segment: seg,
    data: points
      .filter((p) => p.segment === seg)
      .map((p) => ({
        x: p.recency_days,
        y: p.frequency,
        customer_id: p.customer_id,
        name: p.name,
        segment: p.segment,
        monetary: p.monetary,
      })),
  })).filter((s) => s.data.length > 0);

  return (
    <SectionCard
      title="RFM distribution"
      subtitle="Recency (x, lower = better) vs frequency (y) · color = segment"
    >
      <Box sx={{ height: 380, width: "100%" }}>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 12, right: 16, bottom: 12, left: 0 }}>
            <CartesianGrid stroke="#EAECEF" strokeDasharray="3 3" />

            <XAxis
              type="number"
              dataKey="x"
              name="Recency (days)"
              tick={{ fill: "#94A3B8", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              label={{
                value: "Recency (days ago)",
                position: "insideBottom",
                offset: -4,
                fill: "#64748B",
                fontSize: 11,
              }}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Frequency"
              tick={{ fill: "#94A3B8", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
              width={52}
              label={{
                value: "Frequency",
                angle: -90,
                position: "insideLeft",
                fill: "#64748B",
                fontSize: 11,
              }}
            />

            <Tooltip
              content={<ChartTooltip currency={currency} />}
              cursor={{ strokeDasharray: "4 4", stroke: "#CBD5E1" }}
            />

            <Legend
              wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
              iconType="circle"
            />

            {series.map((s) => (
              <Scatter
                key={s.segment}
                name={s.segment}
                data={s.data}
                fill={segmentColor(s.segment)}
                fillOpacity={0.72}
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </Box>
    </SectionCard>
  );
}
