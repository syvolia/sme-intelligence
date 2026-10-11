import {
  Box,
  Button,
  Card,
  Chip,
  InputAdornment,
  Stack,
  TextField,
} from "@mui/material";
import SearchIcon from "@mui/icons-material/Search";
import RestartAltOutlinedIcon from "@mui/icons-material/RestartAltOutlined";

import type { BranchOption } from "../../types/api";

export interface InventoryFilters {
  branch_id: string;
  risk: string;
  search: string;
}

interface Props {
  filters: InventoryFilters;
  onChange: (next: Partial<InventoryFilters>) => void;
  onReset: () => void;
  branches: BranchOption[];
}

const RISK_OPTIONS: Array<{ value: string; label: string }> = [
  { value: "", label: "All" },
  { value: "CRITICAL", label: "Critical" },
  { value: "LOW", label: "Low" },
  { value: "HEALTHY", label: "Healthy" },
];

export function InventoryFilterBar({
  filters,
  onChange,
  onReset,
  branches,
}: Props) {
  const isDirty = Boolean(filters.branch_id || filters.risk || filters.search);

  return (
    <Card sx={{ p: 2 }}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={1.5}
        alignItems={{ xs: "stretch", md: "center" }}
        flexWrap="wrap"
        useFlexGap
      >
        <TextField
          select
          size="small"
          label="Branch"
          value={filters.branch_id}
          onChange={(e) => onChange({ branch_id: e.target.value })}
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

        <Box sx={{ display: "flex", gap: 0.75, alignItems: "center" }}>
          {RISK_OPTIONS.map((opt) => {
            const selected = filters.risk === opt.value;
            return (
              <Chip
                key={opt.value || "all"}
                label={opt.label}
                onClick={() => onChange({ risk: opt.value })}
                variant={selected ? "filled" : "outlined"}
                color={
                  opt.value === "CRITICAL"
                    ? "error"
                    : opt.value === "LOW"
                    ? "warning"
                    : opt.value === "HEALTHY"
                    ? "success"
                    : "default"
                }
                size="small"
                sx={{
                  fontWeight: 600,
                  cursor: "pointer",
                  ...(selected && opt.value === ""
                    ? { backgroundColor: "#0F172A", color: "#FFFFFF" }
                    : {}),
                }}
              />
            );
          })}
        </Box>

        <TextField
          size="small"
          placeholder="Search by name or SKU"
          value={filters.search}
          onChange={(e) => onChange({ search: e.target.value })}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" sx={{ color: "text.secondary" }} />
              </InputAdornment>
            ),
          }}
          sx={{ minWidth: 240, flex: { md: "0 1 320px" } }}
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
    </Card>
  );
}
