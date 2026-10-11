import { Box, Skeleton } from "@mui/material";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { RevenuePoint } from "../../types/api";
import { formatCurrency, formatDate } from "../../lib/format";

interface Props {
  data: RevenuePoint[];
  currency: string;
  loading?: boolean;
  height?: number;
}

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ value: number; payload: RevenuePoint }>;
  currency: string;
}

function ChartTooltip({ active, payload, currency }: TooltipPayload) {
  if (!active || !payload || !payload.length) return null;
  const point = payload[0].payload;
  return (
    <Box
      sx={{
        backgroundColor: "#0F172A",
        color: "#FFFFFF",
        borderRadius: 1.5,
        px: 1.5,
        py: 1,
        boxShadow: "0 8px 20px rgba(15,23,42,0.25)",
        fontSize: 12,
      }}
    >
      <Box sx={{ opacity: 0.7, mb: 0.25 }}>
        {formatDate(point.date, { dateStyle: "medium" })}
      </Box>
      <Box sx={{ fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
        {formatCurrency(point.value, currency)}
      </Box>
    </Box>
  );
}

export function RevenueTrendChart({
  data,
  currency,
  loading,
  height = 320,
}: Props) {
  if (loading) {
    return (
      <Box sx={{ height, display: "flex", alignItems: "center" }}>
        <Skeleton
          variant="rectangular"
          width="100%"
          height={height}
          sx={{ borderRadius: 2 }}
        />
      </Box>
    );
  }

  if (!data.length) {
    return (
      <Box
        sx={{
          height,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "text.secondary",
          fontSize: 13,
        }}
      >
        No revenue data for this range.
      </Box>
    );
  }

  return (
    <Box sx={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 8, right: 8, bottom: 0, left: 0 }}
        >
          <defs>
            <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4F46E5" stopOpacity={0.22} />
              <stop offset="100%" stopColor="#4F46E5" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid
            stroke="#EAECEF"
            strokeDasharray="3 3"
            vertical={false}
          />

          <XAxis
            dataKey="date"
            tickFormatter={(d: string) =>
              formatDate(d, { month: "short", day: "numeric" })
            }
            tick={{ fill: "#94A3B8", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            minTickGap={32}
          />

          <YAxis
            tickFormatter={(v: number) => formatCurrency(v, currency, true)}
            tick={{ fill: "#94A3B8", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={70}
          />

          <Tooltip
            content={<ChartTooltip currency={currency} />}
            cursor={{ stroke: "#CBD5E1", strokeDasharray: "4 4" }}
          />

          <Area
            type="monotone"
            dataKey="value"
            stroke="#4F46E5"
            strokeWidth={2}
            fill="url(#revenueGradient)"
            activeDot={{ r: 4, strokeWidth: 2, stroke: "#FFFFFF" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </Box>
  );
}
