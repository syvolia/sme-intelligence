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
import { formatCurrency, formatDate } from "../../lib/format";
import type { CashflowPoint } from "../../types/api";

interface Props {
  data: CashflowPoint[];
  currency: string;
  loading: boolean;
}

export function DailyFlowsCard({ data, currency, loading }: Props) {
  const rows = data.slice(0, 12);

  return (
    <SectionCard
      title="Next 12 days"
      subtitle="Projected daily inflow, outflow, and closing balance"
    >
      {loading && (
        <Typography variant="body2" color="text.secondary">
          Loading…
        </Typography>
      )}

      {!loading && rows.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          No projection available.
        </Typography>
      )}

      {!loading && rows.length > 0 && (
        <Box sx={{ overflowX: "auto", mx: -3 }}>
          <Table size="small" sx={{ minWidth: 480 }}>
            <TableHead>
              <TableRow>
                <TableCell sx={{ pl: 3 }}>Date</TableCell>
                <TableCell align="right">Inflow</TableCell>
                <TableCell align="right">Outflow</TableCell>
                <TableCell align="right" sx={{ pr: 3 }}>
                  Balance
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((r) => (
                <TableRow
                  key={r.date}
                  sx={{ "&:last-child td": { borderBottom: 0 } }}
                >
                  <TableCell sx={{ pl: 3, fontSize: 13 }}>
                    {formatDate(r.date, {
                      weekday: "short",
                      month: "short",
                      day: "numeric",
                    })}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      fontVariantNumeric: "tabular-nums",
                      color: "success.main",
                      fontWeight: 600,
                    }}
                  >
                    {r.inflow > 0
                      ? `+${formatCurrency(r.inflow, currency, true)}`
                      : "—"}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      fontVariantNumeric: "tabular-nums",
                      color: "warning.main",
                      fontWeight: 600,
                    }}
                  >
                    {r.outflow > 0
                      ? `−${formatCurrency(r.outflow, currency, true)}`
                      : "—"}
                  </TableCell>
                  <TableCell
                    align="right"
                    sx={{
                      pr: 3,
                      fontVariantNumeric: "tabular-nums",
                      fontWeight: 700,
                    }}
                  >
                    {formatCurrency(r.balance, currency, true)}
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
