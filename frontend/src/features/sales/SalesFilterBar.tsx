import {
  Autocomplete,
  Box,
  Button,
  Card,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import RestartAltOutlinedIcon from "@mui/icons-material/RestartAltOutlined";

import type {
  BranchOption,
  CustomerOption,
  ProductOption,
} from "../../types/api";

export interface SalesFilters {
  date_from: string;
  date_to: string;
  branch_id: string;
  product_id: string;
  customer_id: string;
}

interface Props {
  filters: SalesFilters;
  onChange: (next: Partial<SalesFilters>) => void;
  onReset: () => void;
  branches: BranchOption[];
  products: ProductOption[];
  customers: CustomerOption[];
}

export function SalesFilterBar({
  filters,
  onChange,
  onReset,
  branches,
  products,
  customers,
}: Props) {
  const selectedProduct =
    products.find((p) => p.id === filters.product_id) ?? null;
  const selectedCustomer =
    customers.find((c) => c.id === filters.customer_id) ?? null;
  const isDirty =
    Boolean(filters.date_from) ||
    Boolean(filters.date_to) ||
    Boolean(filters.branch_id) ||
    Boolean(filters.product_id) ||
    Boolean(filters.customer_id);

  return (
    <Card sx={{ p: 2 }}>
      <Stack
        direction={{ xs: "column", lg: "row" }}
        spacing={1.5}
        alignItems={{ xs: "stretch", lg: "center" }}
        flexWrap="wrap"
        useFlexGap
      >
        <Stack direction="row" spacing={1} alignItems="center">
          <TextField
            type="date"
            size="small"
            label="From"
            value={filters.date_from}
            onChange={(e) => onChange({ date_from: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ width: 160 }}
          />
          <TextField
            type="date"
            size="small"
            label="To"
            value={filters.date_to}
            onChange={(e) => onChange({ date_to: e.target.value })}
            InputLabelProps={{ shrink: true }}
            sx={{ width: 160 }}
          />
        </Stack>

        <TextField
          select
          size="small"
          label="Branch"
          value={filters.branch_id}
          onChange={(e) => onChange({ branch_id: e.target.value })}
          InputLabelProps={{ shrink: true }}
          SelectProps={{ native: true }}
          sx={{ minWidth: 180 }}
        >
          <option value="">All branches</option>
          {branches.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </TextField>

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
          sx={{ minWidth: 240, flex: { lg: "0 1 260px" } }}
        />

        <Autocomplete
          size="small"
          options={customers}
          value={selectedCustomer}
          onChange={(_, v) => onChange({ customer_id: v?.id ?? "" })}
          getOptionLabel={(o) => o.name || "(unnamed)"}
          isOptionEqualToValue={(a, b) => a.id === b.id}
          renderInput={(params) => (
            <TextField {...params} label="Customer" size="small" />
          )}
          sx={{ minWidth: 240, flex: { lg: "0 1 260px" } }}
        />

        <Box sx={{ flex: 1 }} />

        <Button
          variant="text"
          size="small"
          color="inherit"
          startIcon={<RestartAltOutlinedIcon fontSize="small" />}
          onClick={onReset}
          disabled={!isDirty}
          sx={{ color: "text.secondary" }}
        >
          Reset
        </Button>
      </Stack>

      {!filters.date_from && !filters.date_to && (
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: "block", mt: 1.25, ml: 0.25 }}
        >
          Leave dates empty to use the latest 90 days of activity.
        </Typography>
      )}
    </Card>
  );
}
