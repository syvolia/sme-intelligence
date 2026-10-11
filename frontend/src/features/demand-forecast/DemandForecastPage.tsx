import { Alert, Box, Card, Stack, Typography } from '@mui/material';
import { useMemo, useState } from 'react';

import {
  ForecastFilterBar,
  type ForecastFilters,
} from './ForecastFilterBar';
import { ForecastChart } from './ForecastChart';
import { ForecastMetrics } from './ForecastMetrics';
import { useDemandForecast } from '../../hooks/useDemandForecast';
import { useMeta } from '../../hooks/useMeta';

const INITIAL_FILTERS: ForecastFilters = {
  product_id: '',
  location_id: '',
  horizon_days: 30,
};

export function DemandForecastPage() {
  const [filters, setFilters] = useState<ForecastFilters>(INITIAL_FILTERS);
  const { products, branches } = useMeta();

  const query = useMemo(() => {
    if (!filters.product_id || !filters.location_id) return null;
    return {
      product_id: filters.product_id,
      location_id: filters.location_id,
      horizon_days: filters.horizon_days,
      history_days: 60,
    };
  }, [filters]);

  const { data, loading, error } = useDemandForecast(query);

  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h5" sx={{ mb: 0.5 }}>
          Demand Forecasting
        </Typography>
        <Typography variant="body2" color="text.secondary">
          XGBoost forecast of daily demand per product and branch, with an 80 %
          prediction interval.
        </Typography>
      </Box>

      <ForecastFilterBar
        filters={filters}
        onChange={(patch) => setFilters((f) => ({ ...f, ...patch }))}
        products={products}
        branches={branches}
      />

      {error && (
        <Alert severity="error" variant="outlined" sx={{ whiteSpace: 'pre-line' }}>
          {error}
        </Alert>
      )}

      <ForecastMetrics metrics={data?.metrics} loading={loading} />

      <Card sx={{ p: 3 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ fontSize: 16 }}>
            {data ? `${data.product} · ${data.location}` : 'Forecast'}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {data
              ? `Historical: 60 days · Forecast horizon: ${data.horizon_days} days · Model: ${data.metrics.model}`
              : 'Pick a product and location, then choose a horizon.'}
          </Typography>
        </Box>

        <ForecastChart data={data} loading={loading} height={380} />
      </Card>
    </Stack>
  );
}