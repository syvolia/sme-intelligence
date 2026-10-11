import { Box, Skeleton, Typography } from "@mui/material";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatCurrency, formatDate } from "../../lib/format";
import type { CashflowPoint } from "../../types/api";

interface Props {
  data: CashflowPoint[];
  minSafe: number;
  currency: string;
  loading: boolean;
  height?: number;
}

interface Row {
  date: string;
  balance: number;
  bandLow: number;
  bandSize: number;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: Row }>;
  currency: string;
  minSafe: number;
}

function ChartTooltip({ active, payload, currency, minSafe }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
  const below = row.balance < minSafe;

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
      <Box sx={{ opacity: 0.7, mb: 0.5 }}>
        {formatDate(row.date, { dateStyle: "medium" })}
      </Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          gap: 2,
          fontWeight: 700,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        <span>Balance</span>
        <span style={{ color: below ? "#FCA5A5" : "#FFFFFF" }}>
          {formatCurrency(row.balance, currency)}
        </span>
      </Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          gap: 2,
          opacity: 0.7,
          fontSize: 11,
          mt: 0.25,
        }}
      >
        <span>80% CI</span>
        <span style={{ fontVariantNumeric: "tabular-nums" }}>
          {formatCurrency(row.bandLow, currency, true)} –{" "}
          {formatCurrency(row.bandLow + row.bandSize, currency, true)}
        </span>
      </Box>
    </Box>
  );
}

export function CashflowChart({
  data,
  minSafe,
  currency,
  loading,
  height = 380,
}: Props) {
  if (loading) {
    return (
      <Skeleton
        variant="rectangular"
        height={height}
        sx={{ borderRadius: 2 }}
      />
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
        }}
      >
        <Typography variant="body2">No projection available.</Typography>
      </Box>
    );
  }

  const rows: Row[] = data.map((p) => ({
    date: p.date,
    balance: p.balance,
    bandLow: p.lower,
    bandSize: Math.max(0, p.upper - p.lower),
  }));

  return (
    <Box sx={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={rows}
          margin={{ top: 16, right: 16, bottom: 0, left: 0 }}
        >
          <defs>
            <linearGradient id="cashBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4F46E5" stopOpacity={0.2} />
              <stop offset="100%" stopColor="#4F46E5" stopOpacity={0.05} />
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
            width={72}
          />

          <Tooltip
            content={<ChartTooltip currency={currency} minSafe={minSafe} />}
            cursor={{ stroke: "#CBD5E1", strokeDasharray: "4 4" }}
          />

          {/* confidence band */}
          <Area
            type="monotone"
            dataKey="bandLow"
            stackId="band"
            stroke="none"
            fill="transparent"
            isAnimationActive={false}
          />
          <Area
            type="monotone"
            dataKey="bandSize"
            stackId="band"
            stroke="none"
            fill="url(#cashBand)"
            isAnimationActive={false}
            name="80% interval"
          />

          {/* median balance */}
          <Line
            type="monotone"
            dataKey="balance"
            stroke="#4F46E5"
            strokeWidth={2}
            dot={false}
            name="Projected balance"
          />

          {/* safe floor */}
          <ReferenceLine
            y={minSafe}
            stroke="#DC2626"
            strokeDasharray="4 4"
            label={{
              value: `Min safe: ${formatCurrency(minSafe, currency, true)}`,
              position: "insideTopLeft",
              fill: "#DC2626",
              fontSize: 11,
            }}
          />

          <Legend
            iconType="line"
            wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
            verticalAlign="top"
            height={28}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </Box>
  );
}
