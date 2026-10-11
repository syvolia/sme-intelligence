import { Box } from "@mui/material";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { SectionCard } from "../../components/common/SectionCard";
import { formatCurrency } from "../../lib/format";
import type { ProductRevenue } from "../../types/api";

interface Props {
  data: ProductRevenue[];
  currency: string;
  loading: boolean;
}

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ payload: ProductRevenue; value: number }>;
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
      <Box sx={{ opacity: 0.7, mb: 0.25 }}>{row.product}</Box>
      <Box sx={{ fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
        {formatCurrency(row.revenue, currency)}
      </Box>
      <Box sx={{ opacity: 0.7, mt: 0.25 }}>{row.units} units</Box>
    </Box>
  );
}

export function TopProductsBarCard({ data, currency, loading }: Props) {
  const top = data.slice(0, 8);

  return (
    <SectionCard title="Revenue by product" subtitle="Top products by revenue">
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

      {!loading && top.length === 0 && (
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

      {!loading && top.length > 0 && (
        <Box sx={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={top}
              layout="vertical"
              margin={{ top: 4, right: 16, bottom: 0, left: 0 }}
            >
              <CartesianGrid
                stroke="#EAECEF"
                strokeDasharray="3 3"
                horizontal={false}
              />
              <XAxis
                type="number"
                tickFormatter={(v: number) => formatCurrency(v, currency, true)}
                tick={{ fill: "#94A3B8", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="product"
                width={140}
                tick={{ fill: "#334155", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                content={<ChartTooltip currency={currency} />}
                cursor={{ fill: "rgba(79,70,229,0.06)" }}
              />
              <Bar
                dataKey="revenue"
                fill="#4F46E5"
                radius={[0, 8, 8, 0]}
                maxBarSize={18}
              />
            </BarChart>
          </ResponsiveContainer>
        </Box>
      )}
    </SectionCard>
  );
}
