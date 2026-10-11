import { Box, Skeleton, Typography } from "@mui/material";
import { ResponsiveContainer, Tooltip, Treemap } from "recharts";

import { SectionCard } from "../../components/common/SectionCard";
import { formatCurrency, formatNumber } from "../../lib/format";
import type { SegmentSummary } from "../../types/api";
import { segmentColor } from "./constants";

interface Props {
  segments: SegmentSummary[];
  currency: string;
  loading: boolean;
}

interface TreemapNode {
  name: string;
  size: number;
  segment: string;
  count: number;
  revenue: number;
  revenue_share: number;
  [key: string]: unknown;
}

interface ContentProps {
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  name?: string;
  count?: number;
  segment?: string;
}

function CustomContent(props: ContentProps) {
  const { x = 0, y = 0, width = 0, height = 0, name, count, segment } = props;
  const fill = segment ? segmentColor(segment) : "#4F46E5";

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={10}
        ry={10}
        style={{
          fill,
          stroke: "#FFFFFF",
          strokeWidth: 3,
          opacity: 0.95,
        }}
      />
      {width > 70 && height > 44 && (
        <>
          <text
            x={x + 12}
            y={y + 22}
            fill="#FFFFFF"
            fontSize={11}
            fontWeight={600}
            style={{ letterSpacing: "0.04em", textTransform: "uppercase" }}
          >
            {name}
          </text>
          <text
            x={x + 12}
            y={y + 46}
            fill="#FFFFFF"
            fontSize={22}
            fontWeight={700}
            style={{ fontVariantNumeric: "tabular-nums" }}
          >
            {count}
          </text>
        </>
      )}
    </g>
  );
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: TreemapNode }>;
  currency: string;
}

function ChartTooltip({ active, payload, currency }: TooltipProps) {
  if (!active || !payload?.length) return null;
  const node = payload[0].payload;
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
      <Box sx={{ fontWeight: 700, mb: 0.5 }}>{node.segment}</Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2 }}>
        <span>Customers</span>
        <b style={{ fontVariantNumeric: "tabular-nums" }}>
          {formatNumber(node.count)}
        </b>
      </Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", gap: 2 }}>
        <span>Revenue</span>
        <b style={{ fontVariantNumeric: "tabular-nums" }}>
          {formatCurrency(node.revenue, currency, true)}
        </b>
      </Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          gap: 2,
          opacity: 0.7,
        }}
      >
        <span>Share</span>
        <span style={{ fontVariantNumeric: "tabular-nums" }}>
          {(node.revenue_share * 100).toFixed(1)}%
        </span>
      </Box>
    </Box>
  );
}

export function SegmentTreemap({ segments, currency, loading }: Props) {
  if (loading) {
    return (
      <SectionCard
        title="Customer segments"
        subtitle="Size by number of customers"
      >
        <Skeleton variant="rectangular" height={320} sx={{ borderRadius: 2 }} />
      </SectionCard>
    );
  }

  const data: TreemapNode[] = segments
    .filter((s) => s.count > 0)
    .map((s) => ({
      name: s.segment,
      segment: s.segment,
      size: s.count,
      count: s.count,
      revenue: s.revenue,
      revenue_share: s.revenue_share,
    }));

  return (
    <SectionCard
      title="Customer segments"
      subtitle="Tile size by customer count · color by segment"
    >
      {data.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No segment data available.
        </Typography>
      ) : (
        <Box sx={{ height: 320, width: "100%" }}>
          <ResponsiveContainer width="100%" height="100%">
            <Treemap
              data={data}
              dataKey="size"
              aspectRatio={4 / 3}
              stroke="#FFFFFF"
              content={<CustomContent />}
            >
              <Tooltip content={<ChartTooltip currency={currency} />} />
            </Treemap>
          </ResponsiveContainer>
        </Box>
      )}
    </SectionCard>
  );
}
