import { Alert, Box, Grid, Stack, Typography } from "@mui/material";

import { CustomerSummary } from "./CustomerSummary";
import { SegmentTreemap } from "./SegmentTreemap";
import { RfmScatter } from "./RfmScatter";
import { SegmentTable } from "./SegmentTable";
import { useCustomers } from "../../hooks/useCustomers";

export function CustomerPage() {
  const { data, loading, error } = useCustomers("KES");
  const currency = data?.totals.currency ?? "KES";

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          Customer Intelligence
        </Typography>
        <Typography variant="body2" color="text.secondary">
          RFM segmentation across the customer base — recency, frequency, and
          monetary value.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" variant="outlined">
          Failed to load customers: {error}
        </Alert>
      )}

      <CustomerSummary totals={data?.totals} loading={loading} />

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <SegmentTreemap
            segments={data?.segments ?? []}
            currency={currency}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} lg={6}>
          <RfmScatter
            points={data?.scatter ?? []}
            currency={currency}
            loading={loading}
          />
        </Grid>
      </Grid>

      <SegmentTable
        segments={data?.segments ?? []}
        currency={currency}
        loading={loading}
      />
    </Stack>
  );
}
