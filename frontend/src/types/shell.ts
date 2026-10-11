export interface AppShellContext {
  branchId: string;
  dateFrom: string;
  dateTo: string;
  setBranchId: (id: string) => void;
  setDateFrom: (value: string) => void;
  setDateTo: (value: string) => void;
}