import { Box, Stack, Typography } from "@mui/material";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";

import { SectionCard } from "../../components/common/SectionCard";
import { StatusPill, priorityTone } from "../../components/common/StatusPill";
import type { RecommendationSummary } from "../../types/api";

interface Props {
  items: RecommendationSummary[];
  loading?: boolean;
}

const TYPE_LABEL: Record<string, string> = {
  inventory: "Inventory",
  cashflow: "Cash flow",
  pricing: "Pricing",
  customer: "Customer",
  supplier: "Supplier",
};

export function RecommendationsCard({ items, loading }: Props) {
  const top = items.slice(0, 4);

  return (
    <SectionCard
      title="AI recommendations"
      subtitle="Ranked actions for the next 7 days"
      action={
        <Box
          sx={{
            width: 28,
            height: 28,
            borderRadius: 2,
            backgroundColor: "#EEF2FF",
            color: "#4F46E5",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <AutoAwesomeOutlinedIcon fontSize="small" />
        </Box>
      }
    >
      {loading && <Typography variant="body2">Loading…</Typography>}

      {!loading && top.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          No recommendations right now.
        </Typography>
      )}

      <Stack spacing={1.5}>
        {top.map((rec) => (
          <Box
            key={rec.id}
            sx={{
              border: "1px solid #EAECEF",
              borderRadius: 2,
              p: 1.5,
              backgroundColor: "#FFFFFF",
              "&:hover": { borderColor: "#CBD5E1" },
              transition: "border-color 120ms ease",
            }}
          >
            <Box
              sx={{ display: "flex", alignItems: "center", gap: 1, mb: 0.75 }}
            >
              <Typography
                variant="subtitle2"
                sx={{
                  fontSize: 10,
                  letterSpacing: "0.12em",
                  color: "text.secondary",
                }}
              >
                {TYPE_LABEL[rec.type] ?? rec.type}
              </Typography>
              <Box sx={{ flex: 1 }} />
              <StatusPill
                tone={priorityTone(rec.priority)}
                label={rec.priority}
              />
            </Box>
            <Typography
              sx={{ fontSize: 13.5, fontWeight: 500, lineHeight: 1.4 }}
            >
              {rec.title}
            </Typography>
          </Box>
        ))}
      </Stack>
    </SectionCard>
  );
}
