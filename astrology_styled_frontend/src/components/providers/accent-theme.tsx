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
  return <ThemeProvider outcome={outcome}>{children}</ThemeProvider>;
}
