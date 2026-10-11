import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";
import { useState } from "react";

import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import type { BranchOption } from "../../types/api";
import { isoDaysAgo, todayIso } from "../../lib/format";
import type { AppShellContext } from "../../types/shell";
// Hardcoded for now — will be replaced by a /branches endpoint in a later slice.
const BRANCHES: BranchOption[] = [
  { id: "", name: "All branches" },
  { id: "nairobi-cbd", name: "Nairobi CBD" },
  { id: "westlands", name: "Westlands" },
  { id: "thika-road", name: "Thika Road" },
];

export function AppShell() {
  
  const [branchId, setBranchId] = useState<string>("");
  const [dateFrom, setDateFrom] = useState<string>(isoDaysAgo(90));
  const [dateTo, setDateTo] = useState<string>(todayIso());
<Outlet
  context={
    {
      branchId,
      dateFrom,
      dateTo,
      setBranchId,
      setDateFrom,
      setDateTo,
    } satisfies AppShellContext
  }
/>
  return (
    <Box
      sx={{ display: "flex", minHeight: "100vh", backgroundColor: "#F7F8FA" }}
    >
      <Sidebar />
      <Box
        sx={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}
      >
        <Header
          businessName="GreenHarvest Agro Supplies"
          branches={BRANCHES.filter((b) => b.id !== "")}
          selectedBranchId={branchId}
          onBranchChange={setBranchId}
          dateFrom={dateFrom}
          dateTo={dateTo}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
        />
        <Box
          component="main"
          sx={{
            flex: 1,
            px: { xs: 2, md: 4 },
            py: { xs: 3, md: 4 },
            maxWidth: 1600,
            width: "100%",
            mx: "auto",
          }}
        >
          <Outlet
            context={{
              branchId,
              dateFrom,
              dateTo,
              setDateFrom,
              setDateTo,
              setBranchId,
            }}
          />
        </Box>
      </Box>
    </Box>
  );
}
