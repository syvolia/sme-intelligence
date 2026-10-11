import { Alert, Box, Stack, Typography } from "@mui/material";

import { SupplierSummary } from "./SupplierSummary";
import { SupplierHighlights } from "./SupplierHighlights";
import { SupplierTable } from "./SupplierTable";
import { useSuppliers } from "../../hooks/useSuppliers";

export function SupplierPage() {
  const { data, loading, error } = useSuppliers("KES");

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          Supplier Analytics
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Delivery performance, cost, and a composite reliability score per
          supplier.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" variant="outlined">
          Failed to load suppliers: {error}
        </Alert>
      )}

      <SupplierSummary summary={data?.summary} loading={loading} />

      <SupplierHighlights
        summary={data?.summary}
        suppliers={data?.suppliers ?? []}
        loading={loading}
      />

      <SupplierTable
        suppliers={data?.suppliers ?? []}
        currency={data?.summary.currency ?? "KES"}
        loading={loading}
      />
    </Stack>
  );
}
