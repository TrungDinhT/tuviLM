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
  // Cast beats preview beats the :root default (a null prop clears the
  // properties, letting globals.css decide).
  return <ThemeProvider outcome={outcome ?? previewOutcome}>{children}</ThemeProvider>;
}
