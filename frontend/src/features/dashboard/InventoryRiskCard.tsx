import { Box, Stack, Typography } from "@mui/material";

import { SectionCard } from "../../components/common/SectionCard";
import { StatusPill, riskTone } from "../../components/common/StatusPill";
import type { InventoryRiskItem } from "../../types/api";

interface Props {
  items: InventoryRiskItem[];
  loading?: boolean;
}

export function InventoryRiskCard({ items, loading }: Props) {
  const top = items.slice(0, 4);

  return (
    <SectionCard
      title="Inventory risk"
      subtitle="Products approaching stockout"
      action={
        items.length > 0 ? (
          <StatusPill tone="critical" label={`${items.length} at risk`} />
        ) : undefined
      }
    >
      {loading && <Typography variant="body2">Loading…</Typography>}

      {!loading && top.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          All products are healthy.
        </Typography>
      )}

      <Stack
        divider={<Box sx={{ borderBottom: "1px solid #F1F5F9" }} />}
        spacing={0}
      >
        {top.map((item) => (
          <Box
            key={`${item.product_id}-${item.branch_id}`}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 2,
              py: 1.5,
              "&:first-of-type": { pt: 0 },
              "&:last-of-type": { pb: 0 },
            }}
          >
            <Box sx={{ minWidth: 0 }}>
              <Typography
                sx={{
                  fontSize: 13.5,
                  fontWeight: 600,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {item.product}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {item.branch} · {item.days_remaining.toFixed(0)} days left
              </Typography>
            </Box>
            <StatusPill tone={riskTone(item.risk)} label={item.risk} />
          </Box>
        ))}
      </Stack>
    </SectionCard>
  );
}
