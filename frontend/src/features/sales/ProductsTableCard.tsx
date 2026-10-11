import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

import { SectionCard } from "../../components/common/SectionCard";
import { formatCurrency, formatNumber } from "../../lib/format";
import type { ProductRevenue } from "../../types/api";

interface Props {
  title: string;
  subtitle: string;
  data: ProductRevenue[];
  currency: string;
  loading: boolean;
}

export function ProductsTableCard({
  title,
  subtitle,
  data,
  currency,
  loading,
}: Props) {
  return (
    <SectionCard title={title} subtitle={subtitle}>
      {loading && (
        <Typography variant="body2" color="text.secondary">
          Loading…
        </Typography>
      )}

      {!loading && data.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          No products to display.
        </Typography>
      )}

      {!loading && data.length > 0 && (
        <Box sx={{ overflowX: "auto", mx: -3 }}>
          <Table size="small" sx={{ minWidth: 420 }}>
            <TableHead>
              <TableRow>
                <TableCell sx={{ pl: 3 }}>Product</TableCell>
                <TableCell align="right">Units</TableCell>
                <TableCell align="right" sx={{ pr: 3 }}>
                  Revenue
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.map((row) => (
                <TableRow
                  key={row.product_id}
                  sx={{ "&:last-child td": { borderBottom: 0 } }}
                >
                  <TableCell sx={{ pl: 3 }}>
                    <Typography
                      sx={{ fontSize: 13, fontWeight: 600, lineHeight: 1.2 }}
                    >
                      {row.product}
                    </Typography>
                    {row.category && (
                      <Typography variant="caption" color="text.secondary">
                        {row.category}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{ fontVariantNumeric: "tabular-nums" }}
                  >
                    {formatNumber(row.units)}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      pr: 3,
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 600,
                    }}
                  >
                    {formatCurrency(row.revenue, currency)}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      )}
    </SectionCard>
  );
}
