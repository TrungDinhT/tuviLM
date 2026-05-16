"use client";

import { useIsMobile } from "../_components/useIsMobile";
import { ChartView } from "../_components/ChartView";
import { MobileChartView } from "../_components/MobileChartView";

export default function ChartPage() {
  const isMobile = useIsMobile();
  return isMobile ? <MobileChartView /> : <ChartView />;
}
