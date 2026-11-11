import type { BuildLasoResponse } from "@/lib/api/schemas";
import { type ChartOutcome, starKeyFromName } from "@/lib/theme";

/**
 * Derive the accent-driving outcome from a cast chart: the chính tinh of the
 * cung whose role is Mệnh, normalised to content keys. The payload's
 * trạng thái suffixes ("Tử Vi (Miếu)") are stripped by the normaliser.
 */
export function outcomeFromChart(chart: BuildLasoResponse): ChartOutcome {
  const menh = Object.values(chart.cung_by_position).find((cung) => cung.role === "Mệnh");
  return { stars: (menh?.chinh_tinh ?? []).map(starKeyFromName) };
}
