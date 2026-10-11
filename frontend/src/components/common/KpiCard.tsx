import { Box, Card, CardContent, Skeleton, Typography } from "@mui/material";
import type { ReactNode } from "react";

interface Props {
  label: string;
  value: string;
  secondary?: string;
  icon?: ReactNode;
  accent?: string;
  loading?: boolean;
}

export function KpiCard({
  label,
  value,
  secondary,
  icon,
  accent = "#4F46E5",
  loading = false,
}: Props) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent sx={{ p: 2.5, "&:last-child": { pb: 2.5 } }}>
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          mb={1.5}
        >
          <Typography
            variant="subtitle2"
            color="text.secondary"
            sx={{ fontSize: 11, letterSpacing: "0.08em" }}
          >
            {label}
          </Typography>
          {icon && (
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: 2,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: accent,
                backgroundColor: `${accent}14`,
              }}
            >
              {icon}
            </Box>
          )}
        </Box>

        {loading ? (
          <Skeleton variant="text" width="70%" height={44} />
        ) : (
          <Typography
            sx={{
              fontSize: { xs: 24, md: 30 },
              fontWeight: 700,
              letterSpacing: "-0.02em",
              lineHeight: 1.1,
              fontVariantNumeric: "tabular-nums",
              color: "text.primary",
            }}
          >
            {value}
          </Typography>
        )}

        {secondary && !loading && (
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 0.5, display: "block" }}
          >
            {secondary}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}
