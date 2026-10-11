import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/layout/AppShell";
import { DashboardPage } from "./features/dashboard/DashboardPage";
import { SalesPage } from "./features/sales/SalesPage";
import { InventoryPage } from "./features/inventory/InventoryPage";
import { DemandForecastPage } from "./features/demand-forecast/DemandForecastPage";
import { CashflowPage } from "./features/cashflow/CashflowPage";
import { CustomerPage } from "./features/customers/CustomerPage";
import { SupplierPage } from "./features/suppliers/SupplierPage";
import { RecommendationsPage } from "./features/recommendations/RecommendationsPage";
import { PlaceholderPage } from "./features/common/PlaceholderPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppShell />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="sales" element={<SalesPage />} />
        <Route path="inventory" element={<InventoryPage />} />
        <Route path="forecast/demand" element={<DemandForecastPage />} />
        <Route path="forecast/cashflow" element={<CashflowPage />} />
        <Route path="customers" element={<CustomerPage />} />
        <Route path="suppliers" element={<SupplierPage />} />
        <Route path="recommendations" element={<RecommendationsPage />} />

        <Route
          path="settings"
          element={
            <PlaceholderPage
              title="Settings"
              description="Business profile, branches, currencies, and users."
            />
          }
        />

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  );
}
