"use client";

import { useChartStore } from "@/store/chart-store";

import { ThemeProvider } from "./theme-provider";

/**
 * Connects the chart store to the accent.
 *
 * Kept separate from `ThemeProvider` so that provider stays a pure function of
 * its `outcome` prop and can be tested without a store.
 */
export function AccentTheme({ children }: { children: React.ReactNode }) {
  const outcome = useChartStore((state) => state.outcome);
  const previewOutcome = useChartStore((state) => state.previewOutcome);
  // Preview beats cast beats the :root default (a null prop clears the
  // properties, letting globals.css decide).
  //
  // A preview only exists while An sao is on screen and the user is entering
  // birth data — it is the newer intent, and after a cast the accent would
  // otherwise stay frozen on the previous chart while the dials move. An sao
  // clears the preview when it unmounts, so leaving without casting hands the
  // accent straight back to the cast chart.
  return <ThemeProvider outcome={previewOutcome ?? outcome}>{children}</ThemeProvider>;
}
