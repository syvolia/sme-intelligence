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

import type { DemandForecastResponse } from "../../types/api";
import { formatDate } from "../../lib/format";

interface Props {
  data: DemandForecastResponse | null;
  loading: boolean;
  height?: number;
}

interface Row {
  date: string;
  actual?: number;
  forecast?: number;
  bandLow?: number;
  bandSize?: number;
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: Row }>;
}

function ChartTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const row = payload[0].payload;
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
      {row.actual !== undefined && (
        <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2 }}>
          <span>Actual</span>
          <b style={{ fontVariantNumeric: "tabular-nums" }}>
            {row.actual.toFixed(1)}
          </b>
        </Box>
      )}
      {row.forecast !== undefined && (
        <>
          <Box
            sx={{ display: "flex", justifyContent: "space-between", gap: 2 }}
          >
            <span>Forecast</span>
            <b style={{ fontVariantNumeric: "tabular-nums" }}>
              {row.forecast.toFixed(1)}
            </b>
          </Box>
          {row.bandLow !== undefined && row.bandSize !== undefined && (
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                gap: 2,
                opacity: 0.75,
                fontSize: 11,
              }}
            >
              <span>80% band</span>
              <span style={{ fontVariantNumeric: "tabular-nums" }}>
                {row.bandLow.toFixed(1)} –{" "}
                {(row.bandLow + row.bandSize).toFixed(1)}
              </span>
            </Box>
          )}
        </>
      )}
    </Box>
  );
}

export function ForecastChart({ data, loading, height = 380 }: Props) {
  if (loading) {
    return (
      <Skeleton
        variant="rectangular"
        height={height}
        sx={{ borderRadius: 2 }}
      />
    );
  }

  if (!data || (!data.history.length && !data.forecast.length)) {
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
        <Typography variant="body2">
          Pick a product and a location to see a forecast.
        </Typography>
      </Box>
    );
  }

  const rows: Row[] = [];

  for (const h of data.history) {
    rows.push({ date: h.date, actual: h.value });
  }

  // bridge point so the lines visually connect
  if (data.history.length && data.forecast.length) {
    const lastHistory = data.history[data.history.length - 1];
    const firstForecast = data.forecast[0];
    rows.push({
      date: lastHistory.date,
      actual: lastHistory.value,
      forecast: firstForecast.value,
      bandLow: firstForecast.lower,
      bandSize: Math.max(0, firstForecast.upper - firstForecast.lower),
    });
  }

  for (const f of data.forecast) {
    rows.push({
      date: f.date,
      forecast: f.value,
      bandLow: f.lower,
      bandSize: Math.max(0, f.upper - f.lower),
    });
  }

  const today = data.history.length
    ? data.history[data.history.length - 1].date
    : undefined;

  return (
    <Box sx={{ width: "100%", height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={rows}
          margin={{ top: 16, right: 16, bottom: 0, left: 0 }}
        >
          <defs>
            <linearGradient id="bandGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4F46E5" stopOpacity={0.22} />
              <stop offset="100%" stopColor="#4F46E5" stopOpacity={0.08} />
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
            tick={{ fill: "#94A3B8", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={44}
          />

          <Tooltip content={<ChartTooltip />} />

          {/* Stacked trick to draw a band: transparent base + colored fill */}
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
            fill="url(#bandGradient)"
            isAnimationActive={false}
            name="80% interval"
          />

          <Line
            type="monotone"
            dataKey="actual"
            stroke="#0F172A"
            strokeWidth={2}
            dot={false}
            name="Actual"
            connectNulls={false}
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#4F46E5"
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={false}
            name="Forecast"
            connectNulls={false}
          />

          {today && (
            <ReferenceLine
              x={today}
              stroke="#94A3B8"
              strokeDasharray="3 3"
              label={{
                value: "today",
                position: "insideTopRight",
                fill: "#64748B",
                fontSize: 10,
              }}
            />
          )}

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
