import {
  Box,
  Divider,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Stack,
  Typography,
} from "@mui/material";
import DashboardOutlinedIcon from "@mui/icons-material/DashboardOutlined";
import PointOfSaleOutlinedIcon from "@mui/icons-material/PointOfSaleOutlined";
import Inventory2OutlinedIcon from "@mui/icons-material/Inventory2Outlined";
import InsightsOutlinedIcon from "@mui/icons-material/InsightsOutlined";
import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import PeopleAltOutlinedIcon from "@mui/icons-material/PeopleAltOutlined";
import LocalShippingOutlinedIcon from "@mui/icons-material/LocalShippingOutlined";
import AutoAwesomeOutlinedIcon from "@mui/icons-material/AutoAwesomeOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import { NavLink } from "react-router-dom";
import type { SvgIconComponent } from "@mui/icons-material";

interface NavItem {
  to: string;
  label: string;
  icon: SvgIconComponent;
  end?: boolean;
}

const PRIMARY_NAV: NavItem[] = [
  { to: "/dashboard", label: "Dashboard", icon: DashboardOutlinedIcon },
  { to: "/sales", label: "Sales", icon: PointOfSaleOutlinedIcon },
  { to: "/inventory", label: "Inventory", icon: Inventory2OutlinedIcon },
  {
    to: "/forecast/demand",
    label: "Demand Forecast",
    icon: InsightsOutlinedIcon,
  },
  {
    to: "/forecast/cashflow",
    label: "Cash Flow",
    icon: AccountBalanceWalletOutlinedIcon,
  },
  { to: "/customers", label: "Customers", icon: PeopleAltOutlinedIcon },
  { to: "/suppliers", label: "Suppliers", icon: LocalShippingOutlinedIcon },
  {
    to: "/recommendations",
    label: "Recommendations",
    icon: AutoAwesomeOutlinedIcon,
  },
];

const SECONDARY_NAV: NavItem[] = [
  { to: "/settings", label: "Settings", icon: SettingsOutlinedIcon },
];

function renderItems(items: NavItem[]) {
  return items.map(({ to, label, icon: Icon, end }) => (
    <ListItemButton key={to} component={NavLink} to={to} end={end}>
      <ListItemIcon sx={{ minWidth: 36 }}>
        <Icon fontSize="small" />
      </ListItemIcon>
      <ListItemText
        primary={label}
        primaryTypographyProps={{ fontSize: 13.5, fontWeight: 500 }}
      />
    </ListItemButton>
  ));
}

export function Sidebar() {
  return (
    <Box
      component="nav"
      sx={{
        width: 240,
        flexShrink: 0,
        borderRight: "1px solid #EAECEF",
        backgroundColor: "#FFFFFF",
        display: { xs: "none", md: "flex" },
        flexDirection: "column",
        height: "100vh",
        position: "sticky",
        top: 0,
      }}
    >
      <Stack spacing={0.25} sx={{ px: 3, pt: 2.5, pb: 2 }}>
        <Typography
          variant="subtitle2"
          color="text.secondary"
          sx={{ fontSize: 10, letterSpacing: "0.14em" }}
        >
          Workspace
        </Typography>
        <Typography sx={{ fontWeight: 700, fontSize: 14 }}>
          GreenHarvest
        </Typography>
      </Stack>

      <Divider />

      <List sx={{ pt: 1, pb: 1, flex: 1 }}>{renderItems(PRIMARY_NAV)}</List>

      <Divider />

      <List sx={{ pt: 1, pb: 1 }}>{renderItems(SECONDARY_NAV)}</List>

      <Box sx={{ px: 3, py: 2 }}>
        <Typography variant="caption" color="text.secondary">
          v0.1.0 · Kenya
        </Typography>
      </Box>
    </Box>
  );
}
