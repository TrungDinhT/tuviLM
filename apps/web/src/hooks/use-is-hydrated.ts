"use client";

import { useSyncExternalStore } from "react";

function subscribe() {
  // Hydration happens once and never reverses, so there is nothing to notify.
  return () => {};
}

/**
 * `false` while rendering on the server and for the hydrating render, `true`
 * afterwards.
 *
 * The gate for anything that must not run during render on the server —
 * random values above all. Deriving from this is safer than seeding into
 * state from an effect, because the value can never disagree between the
 * server markup and the first client render.
 */
export function useIsHydrated(): boolean {
  return useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );
}
