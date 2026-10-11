import { Box, Card, CardContent, Stack, Typography } from "@mui/material";
import type { ReactNode } from "react";

interface Props {
  title: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  contentSx?: object;
}

export function SectionCard({
  title,
  subtitle,
  action,
  children,
  contentSx,
}: Props) {
  return (
    <Card sx={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Box
        sx={{
          px: 3,
          pt: 2.5,
          pb: 1.5,
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          gap: 2,
        }}
      >
        <Stack spacing={0.25}>
          <Typography variant="h6" sx={{ fontSize: 16 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Stack>
        {action}
      </Box>
      <CardContent sx={{ px: 3, pt: 0, pb: 3, flex: 1, ...contentSx }}>
        {children}
      </CardContent>
    </Card>
  );
}
