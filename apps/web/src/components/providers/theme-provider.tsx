"use client";

import { useEffect } from "react";

import { type ChartOutcome, resolveAccent } from "@/lib/theme";

/**
 * The one and only writer of `--accent`, `--accent-2` and `--accent-glow`.
 *
 * Nothing else in the application may call `setProperty` for these names. See
 * `lib/theme.ts` for the scoped-accent pattern to use instead when a subtree
 * needs its own colour.
 *
 * Before a chart exists (`outcome === null`) the properties are cleared rather
 * than written, so the `:root` defaults in globals.css apply — which is also
 * what the server renders, so there is nothing to hydrate.
 */
export function ThemeProvider({
  outcome,
  children,
}: {
  outcome: ChartOutcome | null;
  children: React.ReactNode;
}) {
  useEffect(() => {
    const root = document.documentElement;

    if (outcome === null) {
      root.style.removeProperty("--accent");
      root.style.removeProperty("--accent-2");
      root.style.removeProperty("--accent-glow");
      return;
    }

    const { accent, accent2, glow } = resolveAccent(outcome);
    root.style.setProperty("--accent", accent);
    root.style.setProperty("--accent-2", accent2);
    root.style.setProperty("--accent-glow", glow);
  }, [outcome]);

  return children;
}
