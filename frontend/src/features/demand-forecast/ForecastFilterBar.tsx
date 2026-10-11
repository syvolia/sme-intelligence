import {
  Autocomplete,
  Box,
  Button,
  Card,
  Chip,
  Stack,
  TextField,
  Typography,
} from "@mui/material";

import type { BranchOption, ProductOption } from "../../types/api";

export interface ForecastFilters {
  product_id: string;
  location_id: string;
  horizon_days: number;
}

interface Props {
  filters: ForecastFilters;
  onChange: (next: Partial<ForecastFilters>) => void;
  products: ProductOption[];
  branches: BranchOption[];
}

const HORIZONS = [7, 14, 30];

export function ForecastFilterBar({
  filters,
  onChange,
  products,
  branches,
}: Props) {
  const selectedProduct =
    products.find((p) => p.id === filters.product_id) ?? null;

  return (
    <Card sx={{ p: 2 }}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={1.5}
        alignItems={{ xs: "stretch", md: "center" }}
        flexWrap="wrap"
        useFlexGap
      >
        <Autocomplete
          size="small"
          options={products}
          value={selectedProduct}
          onChange={(_, v) => onChange({ product_id: v?.id ?? "" })}
          getOptionLabel={(o) => o.name}
          isOptionEqualToValue={(a, b) => a.id === b.id}
          groupBy={(o) => o.category ?? "Other"}
          renderInput={(params) => (
            <TextField {...params} label="Product" size="small" />
          )}
          sx={{ minWidth: 260, flex: { md: "0 1 320px" } }}
        />

        <TextField
          select
          size="small"
          label="Location"
          value={filters.location_id}
          onChange={(e) => onChange({ location_id: e.target.value })}
          InputLabelProps={{ shrink: true }}
          SelectProps={{ native: true }}
          sx={{ minWidth: 180 }}
        >
          <option value="">Select a branch…</option>
          {branches.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </TextField>

        <Stack
          direction="row"
          spacing={1}
          alignItems="center"
          sx={{ ml: { md: 2 } }}
        >
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ fontWeight: 600 }}
          >
            Horizon
          </Typography>
          {HORIZONS.map((h) => {
            const selected = filters.horizon_days === h;
            return (
              <Chip
                key={h}
                label={`${h}d`}
                onClick={() => onChange({ horizon_days: h })}
                variant={selected ? "filled" : "outlined"}
                size="small"
                sx={{
                  fontWeight: 600,
                  cursor: "pointer",
                  ...(selected
                    ? { backgroundColor: "#0F172A", color: "#FFFFFF" }
                    : {}),
                }}
              />
            );
          })}
        </Stack>

        <Box sx={{ flex: 1 }} />
      </Stack>
    </Card>
  );
}
