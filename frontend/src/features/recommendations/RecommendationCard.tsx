import { Box, Card, Divider, Stack, Typography } from "@mui/material";
import ArrowForwardRoundedIcon from "@mui/icons-material/ArrowForwardRounded";
import InsightsOutlinedIcon from "@mui/icons-material/InsightsOutlined";
import TrackChangesOutlinedIcon from "@mui/icons-material/TrackChangesOutlined";
import ReportProblemOutlinedIcon from "@mui/icons-material/ReportProblemOutlined";

import type { Recommendation } from "../../types/api";
import { PRIORITY_META, TYPE_META } from "./constants";

interface Props {
  rec: Recommendation;
}

function Section({
  icon,
  label,
  body,
  accent,
}: {
  icon: React.ReactNode;
  label: string;
  body: string;
  accent: string;
}) {
  return (
    <Box sx={{ display: "flex", gap: 1.5, alignItems: "flex-start" }}>
      <Box
        sx={{
          width: 24,
          height: 24,
          borderRadius: 1.5,
          backgroundColor: `${accent}14`,
          color: accent,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          mt: 0.25,
        }}
      >
        {icon}
      </Box>
      <Box sx={{ minWidth: 0 }}>
        <Typography
          variant="subtitle2"
          sx={{
            fontSize: 10,
            letterSpacing: "0.14em",
            color: "text.secondary",
            mb: 0.25,
          }}
        >
          {label}
        </Typography>
        <Typography
          sx={{ fontSize: 13.5, lineHeight: 1.55, color: "text.primary" }}
        >
          {body}
        </Typography>
      </Box>
    </Box>
  );
}

export function RecommendationCard({ rec }: Props) {
  const type = TYPE_META[rec.type];
  const priority = PRIORITY_META[rec.priority];

  return (
    <Card
      sx={{
        position: "relative",
        borderLeft: `4px solid ${type.color}`,
        transition: "transform 140ms ease, box-shadow 140ms ease",
        "&:hover": {
          transform: "translateY(-2px)",
          boxShadow: "0 8px 24px rgba(15, 23, 42, 0.06)",
        },
      }}
    >
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box
          sx={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: 2,
            mb: 2,
          }}
        >
          <Box sx={{ minWidth: 0 }}>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                gap: 1,
                mb: 1,
              }}
            >
              <Box
                sx={{
                  fontSize: 14,
                  lineHeight: 1,
                  display: "flex",
                  alignItems: "center",
                }}
              >
                {type.icon}
              </Box>
              <Typography
                variant="subtitle2"
                sx={{
                  fontSize: 10.5,
                  letterSpacing: "0.14em",
                  color: type.color,
                  fontWeight: 700,
                }}
              >
                {type.label}
              </Typography>
            </Box>
            <Typography
              sx={{
                fontSize: { xs: 15, md: 16 },
                fontWeight: 700,
                lineHeight: 1.3,
                letterSpacing: "-0.01em",
              }}
            >
              {rec.title}
            </Typography>
          </Box>

          <Box
            sx={{
              display: "inline-flex",
              alignItems: "center",
              gap: 0.5,
              backgroundColor: priority.bg,
              color: priority.fg,
              borderRadius: 999,
              px: 1.25,
              py: 0.4,
              fontSize: 10.5,
              fontWeight: 700,
              letterSpacing: "0.04em",
              textTransform: "uppercase",
              whiteSpace: "nowrap",
              flexShrink: 0,
            }}
          >
            <Box
              component="span"
              sx={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                backgroundColor: priority.dot,
              }}
            />
            {priority.label}
          </Box>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {/* Four-part body */}
        <Stack spacing={1.75}>
          <Section
            icon={<ReportProblemOutlinedIcon sx={{ fontSize: 14 }} />}
            label="Problem"
            body={rec.problem}
            accent="#DC2626"
          />
          <Section
            icon={<InsightsOutlinedIcon sx={{ fontSize: 14 }} />}
            label="Evidence"
            body={rec.evidence}
            accent="#0EA5E9"
          />
          <Section
            icon={<ArrowForwardRoundedIcon sx={{ fontSize: 14 }} />}
            label="Recommendation"
            body={rec.recommendation}
            accent={type.color}
          />
          <Section
            icon={<TrackChangesOutlinedIcon sx={{ fontSize: 14 }} />}
            label="Expected impact"
            body={rec.expected_impact}
            accent="#16A34A"
          />
        </Stack>
      </Box>
    </Card>
  );
}
