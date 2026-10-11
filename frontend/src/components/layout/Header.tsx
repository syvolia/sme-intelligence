import {
  AppBar,
  Avatar,
  Badge,
  Box,
  IconButton,
  MenuItem,
  Select,
  Stack,
  TextField,
  Toolbar,
  Tooltip,
  Typography,
} from "@mui/material";
import NotificationsNoneIcon from "@mui/icons-material/NotificationsNone";
import StorefrontIcon from "@mui/icons-material/Storefront";
import type { BranchOption } from "../../types/api";
import { todayIso, isoDaysAgo } from "../../lib/format";

interface Props {
  businessName: string;
  branches: BranchOption[];
  selectedBranchId: string;
  onBranchChange: (id: string) => void;
  dateFrom: string;
  dateTo: string;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
}

export function Header({
  businessName,
  branches,
  selectedBranchId,
  onBranchChange,
  dateFrom,
  dateTo,
  onDateFromChange,
  onDateToChange,
}: Props) {
  return (
    <AppBar
      position="sticky"
      color="inherit"
      elevation={0}
      sx={{
        backgroundColor: "#FFFFFF",
        borderBottom: "1px solid #EAECEF",
      }}
    >
      <Toolbar
        sx={{ minHeight: { xs: 64, md: 72 }, px: { xs: 2, md: 3 }, gap: 2 }}
      >
        {/* Business identity */}
        <Stack
          direction="row"
          spacing={1.5}
          alignItems="center"
          sx={{ minWidth: 0 }}
        >
          <Box
            sx={{
              width: 32,
              height: 32,
              borderRadius: 2,
              backgroundColor: "#4F46E5",
              color: "#FFFFFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <StorefrontIcon fontSize="small" />
          </Box>
          <Box sx={{ minWidth: 0 }}>
            <Typography
              variant="subtitle1"
              sx={{ fontWeight: 700, lineHeight: 1.1, whiteSpace: "nowrap" }}
            >
              {businessName}
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ lineHeight: 1 }}
            >
              Decision Intelligence
            </Typography>
          </Box>
        </Stack>

        <Box sx={{ flex: 1 }} />

        {/* Branch selector */}
        <Select
          size="small"
          value={selectedBranchId}
          onChange={(e) => onBranchChange(e.target.value)}
          displayEmpty
          sx={{ minWidth: 160, display: { xs: "none", md: "inline-flex" } }}
        >
          <MenuItem value="">All branches</MenuItem>
          {branches.map((b) => (
            <MenuItem key={b.id} value={b.id}>
              {b.name}
            </MenuItem>
          ))}
        </Select>

        {/* Date range */}
        <Stack
          direction="row"
          spacing={1}
          alignItems="center"
          sx={{ display: { xs: "none", lg: "flex" } }}
        >
          <TextField
            type="date"
            size="small"
            value={dateFrom}
            onChange={(e) => onDateFromChange(e.target.value)}
            InputLabelProps={{ shrink: true }}
            inputProps={{ max: dateTo || todayIso() }}
            sx={{ width: 150 }}
          />
          <Typography color="text.secondary" variant="body2">
            –
          </Typography>
          <TextField
            type="date"
            size="small"
            value={dateTo}
            onChange={(e) => onDateToChange(e.target.value)}
            InputLabelProps={{ shrink: true }}
            inputProps={{ min: dateFrom, max: todayIso() }}
            sx={{ width: 150 }}
          />
        </Stack>

        {/* Notifications */}
        <Tooltip title="Notifications">
          <IconButton size="small">
            <Badge color="error" variant="dot" overlap="circular">
              <NotificationsNoneIcon fontSize="small" />
            </Badge>
          </IconButton>
        </Tooltip>

        {/* User */}
        <Tooltip title="Account">
          <Avatar
            sx={{
              width: 32,
              height: 32,
              backgroundColor: "#0F172A",
              fontSize: 13,
            }}
          >
            AM
          </Avatar>
        </Tooltip>
      </Toolbar>
    </AppBar>
  );
}

export const DEFAULT_DATE_FROM = isoDaysAgo(90);
