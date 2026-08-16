import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import { safeStorage } from "@/lib/safe-storage";
import type { ChartOutcome } from "@/lib/theme";
import { useToastStore } from "@/store/toast-store";

export const CHART_STORAGE_KEY = "tuvi.chart";

interface ChartState {
  /**
   * The single source of truth for navigation locking. True once a chart has
   * been cast, false again after a reset.
   */
  hasChart: boolean;
  /** Drives the runtime accent. Null until a chart exists. */
  outcome: ChartOutcome | null;

  castChart: (outcome: ChartOutcome) => void;
  reset: () => void;
}

const EMPTY = { hasChart: false, outcome: null } as const;

export const useChartStore = create<ChartState>()(
  persist(
    (set) => ({
      ...EMPTY,

      castChart: (outcome) => set({ hasChart: true, outcome }),

      /**
       * Clears every chart-derived value at once.
       *
       * Resetting only the birth input leaves the deck, the Thiên Bàn
       * selection, the chart grid and the conversation showing data from the
       * previous chart. Two mechanisms cover the rest:
       *
       * - the accent reverts on its own, because `AccentTheme` reads `outcome`
       *   and a null outcome restores the `:root` defaults
       * - any transient message is dismissed here, since it may well be
       *   describing the chart that just went away
       *
       * Screens holding their own derived state subscribe to `hasChart` and
       * clear when it goes false — including closing any open overlay.
       */
      reset: () => {
        useToastStore.getState().dismiss();
        set({ ...EMPTY });
      },
    }),
    {
      name: CHART_STORAGE_KEY,
      storage: createJSONStorage(() => safeStorage),
      // Rehydrate from an effect instead of at module load, so the first
      // client render matches the server's and hydration stays clean.
      // See components/providers/store-hydration.tsx.
      skipHydration: true,
      partialize: (state) => ({ hasChart: state.hasChart, outcome: state.outcome }),
    },
  ),
);
