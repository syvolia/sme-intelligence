import { Box, Card, Stack, Typography } from "@mui/material";
import WarningAmberRoundedIcon from "@mui/icons-material/WarningAmberRounded";

import { formatCurrency, formatDate } from "../../lib/format";
import type { ShortageAlert } from "../../types/api";

interface Props {
  alert: ShortageAlert;
  currency: string;
}

export function ShortageAlertCard({ alert, currency }: Props) {
  return (
    <Card
      sx={{
        borderColor: "#FCA5A5",
        backgroundColor: "#FEF2F2",
        borderLeft: "4px solid #DC2626",
      }}
    >
      <Stack spacing={2} sx={{ p: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.25 }}>
          <Box
            sx={{
              width: 34,
              height: 34,
              borderRadius: 2,
              backgroundColor: "#FEE2E2",
              color: "#DC2626",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <WarningAmberRoundedIcon fontSize="small" />
          </Box>
          <Typography
            sx={{
              fontSize: 15,
              fontWeight: 700,
              color: "#991B1B",
              letterSpacing: "-0.01em",
            }}
          >
            Potential cash shortage
          </Typography>
        </Box>

        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "repeat(3, 1fr)" },
            gap: 2,
            pt: 1,
            borderTop: "1px dashed #FCA5A5",
          }}
        >
          <AlertStat
            label="Predicted date"
            value={formatDate(alert.predicted_date, { dateStyle: "long" })}
          />
          <AlertStat
            label="Expected minimum"
            value={formatCurrency(alert.expected_minimum, currency)}
            emphasize
          />
          <AlertStat
            label="Minimum safe balance"
            value={formatCurrency(alert.minimum_safe_balance, currency)}
          />
        </Box>

        <Box
          sx={{
            backgroundColor: "#FFFFFF",
            border: "1px solid #FECACA",
            borderRadius: 2,
            p: 2,
            mt: 0.5,
          }}
        >
          <Typography
            variant="subtitle2"
            sx={{
              fontSize: 10,
              letterSpacing: "0.14em",
              color: "#991B1B",
              mb: 0.75,
            }}
          >
            Recommendation
          </Typography>
          <Typography
            sx={{ fontSize: 13.5, color: "#7F1D1D", lineHeight: 1.5 }}
          >
            {alert.recommendation}
          </Typography>
        </Box>
      </Stack>
    </Card>
  );
}

function AlertStat({
  label,
  value,
  emphasize = false,
}: {
  label: string;
  value: string;
  emphasize?: boolean;
}) {
  return (
    <Box>
      <Typography
        variant="subtitle2"
        sx={{
          fontSize: 10,
          letterSpacing: "0.12em",
          color: "#991B1B",
          mb: 0.5,
        }}
      >
        {label}
      </Typography>
      <Typography
        sx={{
          fontSize: emphasize ? 18 : 15,
          fontWeight: emphasize ? 700 : 600,
          color: emphasize ? "#7F1D1D" : "#991B1B",
          fontVariantNumeric: "tabular-nums",
          lineHeight: 1.2,
        }}
      >
        {value}
      </Typography>
    </Box>
  );
}
