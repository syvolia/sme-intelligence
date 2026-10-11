import { Alert, Box, Stack, Typography } from '@mui/material';
import { useMemo, useState } from 'react';

import {
  InventoryFilterBar,
  type InventoryFilters,
} from './InventoryFilterBar';
import { InventorySummary } from './InventorySummary';
import { InventoryTable } from './InventoryTable';
import { useInventory } from '../../hooks/useInventory';
import { useMeta } from '../../hooks/useMeta';

const EMPTY_FILTERS: InventoryFilters = {
  branch_id: '',
  risk: '',
  search: '',
};

export function InventoryPage() {
  const [filters, setFilters] = useState<InventoryFilters>(EMPTY_FILTERS);
  const { branches } = useMeta();

  const query = useMemo(
    () => ({
      branch_id: filters.branch_id || undefined,
      risk: filters.risk || undefined,
      search: filters.search || undefined,
    }),
    [filters],
  );

  const { data, loading, error } = useInventory(query);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          Inventory Intelligence
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Stock position, demand velocity, and reorder signals per product and branch.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" variant="outlined">
          Failed to load inventory: {error}
        </Alert>
      )}

      <InventorySummary
        summary={data?.summary}
        loading={loading}
        activeRisk={filters.risk}
        onRiskClick={(risk) => setFilters((f) => ({ ...f, risk }))}
      />

      <InventoryFilterBar
        filters={filters}
        onChange={(patch) => setFilters((f) => ({ ...f, ...patch }))}
        onReset={() => setFilters(EMPTY_FILTERS)}
        branches={branches}
      />

      <InventoryTable items={data?.items ?? []} loading={loading} />
    </Stack>
  );
}