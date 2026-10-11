import { Alert, Box, Grid, Stack, Typography } from '@mui/material';
import { useMemo, useState } from 'react';

import { SalesFilterBar, type SalesFilters } from './SalesFilterBar';
import { SalesKpis } from './SalesKpis';
import { RevenueOverTimeCard } from './RevenueOverTimeCard';
import { CategoryDonutCard } from './CategoryDonutCard';
import { LocationBarCard } from './LocationBarCard';
import { TopProductsBarCard } from './TopProductsBarCard';
import { ProductsTableCard } from './ProductsTableCard';
import { useSales } from '../../hooks/useSales';
import { useMeta } from '../../hooks/useMeta';

const EMPTY_FILTERS: SalesFilters = {
  date_from: '',
  date_to: '',
  branch_id: '',
  product_id: '',
  customer_id: '',
};

export function SalesPage() {
  const [filters, setFilters] = useState<SalesFilters>(EMPTY_FILTERS);

  const { branches, products, customers, loading: metaLoading } = useMeta();

  const query = useMemo(
    () => ({
      date_from: filters.date_from || undefined,
      date_to: filters.date_to || undefined,
      branch_id: filters.branch_id || undefined,
      product_id: filters.product_id || undefined,
      customer_id: filters.customer_id || undefined,
    }),
    [filters],
  );

  const { data, loading, error } = useSales(query);

  const currency = data?.kpis.currency ?? 'KES';

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          Sales Analytics
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Revenue, orders, and product-level performance for the selected period.
        </Typography>
      </Box>

      <SalesFilterBar
        filters={filters}
        onChange={(patch) => setFilters((f) => ({ ...f, ...patch }))}
        onReset={() => setFilters(EMPTY_FILTERS)}
        branches={branches}
        products={products}
        customers={customers}
      />

      {error && (
        <Alert severity="error" variant="outlined">
          Failed to load sales data: {error}
        </Alert>
      )}

      <SalesKpis kpis={data?.kpis} loading={loading || metaLoading} />

      <RevenueOverTimeCard
        data={data?.revenue_over_time ?? []}
        currency={currency}
        loading={loading}
      />

      <Grid container spacing={3}>
        <Grid item xs={12} lg={4}>
          <CategoryDonutCard
            data={data?.revenue_by_category ?? []}
            currency={currency}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} lg={4}>
          <LocationBarCard
            data={data?.revenue_by_location ?? []}
            currency={currency}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} lg={4}>
          <TopProductsBarCard
            data={data?.revenue_by_product ?? []}
            currency={currency}
            loading={loading}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={6}>
          <ProductsTableCard
            title="Top products"
            subtitle="Highest revenue for the period"
            data={data?.top_products ?? []}
            currency={currency}
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} lg={6}>
          <ProductsTableCard
            title="Bottom products"
            subtitle="Lowest revenue with sales in the period"
            data={data?.bottom_products ?? []}
            currency={currency}
            loading={loading}
          />
        </Grid>
      </Grid>
    </Stack>
  );
}