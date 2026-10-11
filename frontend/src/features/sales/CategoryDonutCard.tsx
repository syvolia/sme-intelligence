import { Box, Stack, Typography } from "@mui/material";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { SectionCard } from "../../components/common/SectionCard";
import { formatCurrency } from "../../lib/format";
import type { CategoryRevenue } from "../../types/api";

const COLORS = [
  "#4F46E5",
  "#0EA5E9",
  "#16A34A",
  "#D97706",
  "#DC2626",
  "#8B5CF6",
  "#EC4899",
  "#06B6D4",
];

interface Props {
  data: CategoryRevenue[];
  currency: string;
  loading: boolean;
}

interface TooltipPayload {
  active?: boolean;
  payload?: Array<{ payload: CategoryRevenue; value: number }>;
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
        boxShadow: "0 8px 20px rgba(15,23,42,0.25)",
      }}
    >
      <Box sx={{ opacity: 0.7, mb: 0.25 }}>{row.category}</Box>
      <Box sx={{ fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
        {formatCurrency(row.revenue, currency)}
      </Box>
    </Box>
  );
}

export function CategoryDonutCard({ data, currency, loading }: Props) {
  const total = data.reduce((acc, d) => acc + d.revenue, 0);

  return (
    <SectionCard title="Revenue by category" subtitle="Share of total revenue">
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
        <Stack spacing={2}>
          <Box sx={{ height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  dataKey="revenue"
                  nameKey="category"
                  cx="50%"
                  cy="50%"
                  innerRadius={58}
                  outerRadius={88}
                  paddingAngle={2}
                  stroke="#FFFFFF"
                  strokeWidth={2}
                >
                  {data.map((entry, i) => (
                    <Cell
                      key={entry.category}
                      fill={COLORS[i % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip currency={currency} />} />
              </PieChart>
            </ResponsiveContainer>
          </Box>

          <Stack spacing={1}>
            {data.map((row, i) => {
              const pct = total > 0 ? (row.revenue / total) * 100 : 0;
              return (
                <Box
                  key={row.category}
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: 1.5,
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      minWidth: 0,
                    }}
                  >
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: "50%",
                        backgroundColor: COLORS[i % COLORS.length],
                        flexShrink: 0,
                      }}
                    />
                    <Typography
                      sx={{
                        fontSize: 13,
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {row.category}
                    </Typography>
                  </Box>
                  <Typography
                    sx={{
                      fontSize: 12.5,
                      fontWeight: 600,
                      fontVariantNumeric: "tabular-nums",
                    }}
                  >
                    {pct.toFixed(1)}%
                  </Typography>
                </Box>
              );
            })}
          </Stack>
        </Stack>
      )}
    </SectionCard>
  );
}
