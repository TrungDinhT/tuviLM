"use client";

import { useEffect } from "react";

import { useChartStore } from "@/store/chart-store";
import { usePreferencesStore } from "@/store/preferences-store";

/**
 * Rehydrates the persisted stores after mount.
 *
 * Both are created with `skipHydration`, so their first client render uses the
 * same defaults the server rendered. Rehydrating here rather than at module
 * load is what keeps hydration clean: a returning user's `hasChart` arrives on
 * the next render instead of contradicting the server's markup on the first
 * one.
 */
export function StoreHydration() {
  useEffect(() => {
    void useChartStore.persist.rehydrate();
    void usePreferencesStore.persist.rehydrate();
  }, []);

  return null;
}
