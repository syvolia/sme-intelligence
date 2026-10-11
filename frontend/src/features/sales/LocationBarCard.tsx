import { Box } from "@mui/material";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { SectionCard } from "../../components/common/SectionCard";
import { formatCurrency } from "../../lib/format";
import type { LocationRevenue } from "../../types/api";

const COLORS = ["#4F46E5", "#0EA5E9", "#16A34A", "#D97706", "#DC2626"];

interface Props {
  data: LocationRevenue[];
  currency: string;
  loading: boolean;
}

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ payload: LocationRevenue; value: number }>;
  currency: string;
}

function ChartTooltip({ active, payload, currency }: TooltipPayload) {
  if (!active || !payload || !payload.length) return null;
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
      }}
    >
      <Box sx={{ opacity: 0.7, mb: 0.25 }}>{row.location}</Box>
      <Box sx={{ fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
        {formatCurrency(row.revenue, currency)}
      </Box>
    </Box>
  );
}

export function LocationBarCard({ data, currency, loading }: Props) {
  return (
    <SectionCard title="Revenue by location" subtitle="Branch contribution">
      {loading && (
        <Box
          sx={{
            height: 300,
            display: "flex",
            alignItems: "center",
            color: "text.secondary",
          }}
        >
          Loading…
        </Box>
      )}

      {!loading && data.length === 0 && (
        <Box
          sx={{
            height: 300,
            display: "flex",
            alignItems: "center",
            color: "text.secondary",
          }}
        >
          No data.
        </Box>
      )}

      {!loading && data.length > 0 && (
        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{ top: 8, right: 8, bottom: 0, left: 0 }}
            >
              <CartesianGrid
                stroke="#EAECEF"
                strokeDasharray="3 3"
                vertical={false}
              />
              <XAxis
                dataKey="location"
                tick={{ fill: "#94A3B8", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
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
                cursor={{ fill: "rgba(79,70,229,0.06)" }}
              />
              <Bar dataKey="revenue" radius={[8, 8, 0, 0]} maxBarSize={56}>
                {data.map((entry, i) => (
                  <Cell
                    key={entry.location_id}
                    fill={COLORS[i % COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </Box>
      )}
    </SectionCard>
  );
}
