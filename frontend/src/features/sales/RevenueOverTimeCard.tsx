import { SectionCard } from "../../components/common/SectionCard";
import { RevenueTrendChart } from "../../components/charts/RevenueTrendChart";
import type { TimePoint } from "../../types/api";

interface Props {
  data: TimePoint[];
  currency: string;
  loading: boolean;
}

export function RevenueOverTimeCard({ data, currency, loading }: Props) {
  return (
    <SectionCard
      title="Revenue over time"
      subtitle="Daily gross revenue for the selected period"
    >
      <RevenueTrendChart
        data={data}
        currency={currency}
        loading={loading}
        height={340}
      />
    </SectionCard>
  );
}
