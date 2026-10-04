"use client";

import { useEffect } from "react";

import { usePreferencesStore } from "@/store/preferences-store";

/**
 * Rehydrates preferences after mount. Chart hydration belongs to QueryProvider,
 * which checks the signed-in account before exposing any restored chart.
 *
 * The store uses skipHydration so the first client render matches the server.
 */
export function StoreHydration() {
  useEffect(() => {
    void usePreferencesStore.persist.rehydrate();
  }, []);

  return null;
}
