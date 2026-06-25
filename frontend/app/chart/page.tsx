"use client";

import { useIsCompact } from "../_components/useIsCompact";
import { ChartView } from "../_components/ChartView";
import { MobileChartView } from "../_components/MobileChartView";

export default function ChartPage() {
  const isCompact = useIsCompact();
  return isCompact ? <MobileChartView /> : <ChartView />;
}
