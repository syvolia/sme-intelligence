import {
  Alert,
  Box,
  Card,
  Chip,
  Grid,
  Skeleton,
  Stack,
  Typography,
} from "@mui/material";
import { useMemo, useState } from "react";

import { RecommendationCard } from "./RecommendationCard";
import { TYPE_META, TYPE_ORDER } from "./constants";
import { useRecommendations } from "../../hooks/useRecommendations";
import type { RecommendationType } from "../../types/api";

type TypeFilter = RecommendationType | "all";

export function RecommendationsPage() {
  const { data, loading, error } = useRecommendations("KES");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("all");

  const cards = useMemo(() => {
    const all = data?.cards ?? [];
    return typeFilter === "all"
      ? all
      : all.filter((c) => c.type === typeFilter);
  }, [data, typeFilter]);

  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = { all: data?.cards.length ?? 0 };
    for (const t of TYPE_ORDER) {
      counts[t] = data?.totals.by_type[t] ?? 0;
    }
    return counts;
  }, [data]);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          AI Recommendations
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Ranked actions across inventory, cash flow, pricing, customers, and
          suppliers — every recommendation traces back to a number in your data.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" variant="outlined">
          Failed to load recommendations: {error}
        </Alert>
      )}

      {/* Summary strip */}
      {!loading && data && (
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryTile
              label="Total recommendations"
              value={data.totals.total}
              accent="#0F172A"
              active={typeFilter === "all"}
              onClick={() => setTypeFilter("all")}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryTile
              label="High priority"
              value={data.totals.high}
              accent="#DC2626"
              sub="Immediate action"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryTile
              label="Medium priority"
              value={data.totals.medium}
              accent="#D97706"
              sub="Plan this week"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <SummaryTile
              label="Low priority"
              value={data.totals.low}
              accent="#4F46E5"
              sub="Monitor"
            />
          </Grid>
        </Grid>
      )}

      {/* Type filter chips */}
      {!loading && (
        <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
          <Chip
            label={`All (${typeCounts.all})`}
            onClick={() => setTypeFilter("all")}
            variant={typeFilter === "all" ? "filled" : "outlined"}
            sx={{
              fontWeight: 600,
              ...(typeFilter === "all"
                ? { backgroundColor: "#0F172A", color: "#FFFFFF" }
                : {}),
            }}
          />
          {TYPE_ORDER.map((t) => {
            const meta = TYPE_META[t];
            const selected = typeFilter === t;
            return (
              <Chip
                key={t}
                label={`${meta.icon} ${meta.label} (${typeCounts[t] ?? 0})`}
                onClick={() => setTypeFilter(t)}
                variant={selected ? "filled" : "outlined"}
                sx={{
                  fontWeight: 600,
                  ...(selected
                    ? {
                        backgroundColor: meta.color,
                        color: "#FFFFFF",
                        "&:hover": { backgroundColor: meta.color },
                      }
                    : { color: meta.color, borderColor: `${meta.color}55` }),
                }}
              />
            );
          })}
        </Box>
      )}

      {/* Cards grid */}
      {loading && (
        <Grid container spacing={3}>
          {Array.from({ length: 4 }).map((_, i) => (
            <Grid item xs={12} lg={6} key={i}>
              <Card sx={{ p: 3 }}>
                <Skeleton variant="text" width="40%" />
                <Skeleton
                  variant="text"
                  width="80%"
                  height={32}
                  sx={{ mb: 2 }}
                />
                <Skeleton
                  variant="rectangular"
                  height={140}
                  sx={{ borderRadius: 1 }}
                />
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {!loading && cards.length === 0 && (
        <Card
          sx={{
            p: 6,
            textAlign: "center",
            color: "text.secondary",
            borderStyle: "dashed",
          }}
        >
          <Typography sx={{ fontWeight: 600, mb: 0.5 }}>
            No recommendations in this category
          </Typography>
          <Typography variant="body2">
            Either everything is healthy or the filter is too narrow.
          </Typography>
        </Card>
      )}

      {!loading && cards.length > 0 && (
        <Grid container spacing={3}>
          {cards.map((rec) => (
            <Grid item xs={12} lg={6} key={rec.id}>
              <RecommendationCard rec={rec} />
            </Grid>
          ))}
        </Grid>
      )}
    </Stack>
  );
}

function SummaryTile({
  label,
  value,
  accent,
  sub,
  active,
  onClick,
}: {
  label: string;
  value: number;
  accent: string;
  sub?: string;
  active?: boolean;
  onClick?: () => void;
}) {
  const interactive = Boolean(onClick);
  return (
    <Card
      onClick={onClick}
      sx={{
        p: 2.5,
        cursor: interactive ? "pointer" : "default",
        borderColor: active ? accent : "#EAECEF",
        boxShadow: active ? `0 0 0 1px ${accent}` : undefined,
        transition: "all 140ms ease",
        "&:hover": interactive
          ? { borderColor: accent, transform: "translateY(-1px)" }
          : undefined,
      }}
    >
      <Typography
        variant="subtitle2"
        color="text.secondary"
        sx={{ fontSize: 10, letterSpacing: "0.12em", mb: 1 }}
      >
        {label}
      </Typography>
      <Typography
        sx={{
          fontSize: 28,
          fontWeight: 700,
          letterSpacing: "-0.02em",
          fontVariantNumeric: "tabular-nums",
          lineHeight: 1.1,
        }}
      >
        {value}
      </Typography>
      {sub && (
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ mt: 0.5, display: "block" }}
        >
          {sub}
        </Typography>
      )}
    </Card>
  );
}
