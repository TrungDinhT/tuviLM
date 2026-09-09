"use client";

import { usePathname } from "next/navigation";

import { AN_SAO_ROUTE, screenFor } from "@/config/site";
import { useChartStore } from "@/store/chart-store";

import { ThemeProvider } from "./theme-provider";

/**
 * Connects the chart store to the accent.
 *
 * Kept separate from `ThemeProvider` so that provider stays a pure function of
 * its `outcome` prop and can be tested without a store.
 */
export function AccentTheme({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const outcome = useChartStore((state) => state.outcome);
  const previewOutcome = useChartStore((state) => state.previewOutcome);
  // Preview beats cast beats the :root default (a null prop clears the
  // properties, letting globals.css decide).
  //
  // On the casting screen the persisted cast outcome must not apply: An sao is
  // where a *new* chart is entered, so its accent comes from the live preview
  // alone, or falls back to the default. A cached chart would otherwise tint
  // the screen with a reading the user is about to replace. An sao clears the
  // preview when it unmounts, so it cannot leak onto the other tabs.
  // Standalone routes (auth and not-found) intentionally use the neutral
  // pre-chart palette from globals.css. They belong to the product shell,
  // not to whichever chart happened to be viewed most recently.
  const isStandalone = screenFor(pathname) === null;
  const effective = isStandalone
    ? null
    : pathname === AN_SAO_ROUTE
      ? previewOutcome
      : (previewOutcome ?? outcome);
  return <ThemeProvider outcome={effective}>{children}</ThemeProvider>;
}
