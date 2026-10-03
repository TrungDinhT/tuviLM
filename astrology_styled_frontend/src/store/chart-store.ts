import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import type { BirthInfo } from "@/lib/api/schemas";
import { safeStorage } from "@/lib/safe-storage";
import type { ChartOutcome } from "@/lib/theme";
import { dismissToast } from "@/lib/toast";

export const CHART_STORAGE_KEY = "tuvi.chart";

interface ChartState {
  /**
   * The single source of truth for navigation locking. True once a chart has
   * been cast, false again after a reset.
   */
  hasChart: boolean;
  /** Drives the runtime accent. Null until a chart exists. */
  outcome: ChartOutcome | null;
  /**
   * The preview-endpoint outcome, resolved while the user is still entering
   * birth data. It outranks `outcome` in the accent, being the newer intent,
   * and An sao clears it on unmount so it cannot outlive that screen. Never
   * persisted — a reload before casting starts from the default accent.
   */
  previewOutcome: ChartOutcome | null;
  /**
   * The id of the cast chart — the deterministic id from the build response,
   * which is also its key in the persisted query cache. Null until a cast.
   */
  chartId: string | null;
  /**
   * The birth tuple the chart was cast from. The chat backend rebuilds the
   * lá số from a chart profile's `birth_info`, not from the build response,
   * so this is the only place the cast tuple survives for the auto-save.
   */
  birthInfo: BirthInfo | null;
  /**
   * The id of the auto-created chart profile for this cast, or null when the
   * auto-save failed or has not finished. Chat resolves its session from this.
   */
  chartProfileId: string | null;

  castChart: (
    outcome: ChartOutcome,
    chartId: string,
    birthInfo?: BirthInfo | null,
    chartProfileId?: string | null,
  ) => void;
  setPreviewOutcome: (outcome: ChartOutcome | null) => void;
  reset: () => void;
}

const EMPTY = {
  hasChart: false,
  outcome: null,
  previewOutcome: null,
  chartId: null,
  birthInfo: null,
  chartProfileId: null,
} as const;

export const useChartStore = create<ChartState>()(
  persist(
    (set) => ({
      ...EMPTY,

      // The real outcome replaces any preview — a stale preview must never
      // leak into the cast accent.
      castChart: (outcome, chartId, birthInfo = null, chartProfileId = null) =>
        set({ hasChart: true, outcome, chartId, birthInfo, chartProfileId, previewOutcome: null }),

      setPreviewOutcome: (outcome) => set({ previewOutcome: outcome }),

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
        dismissToast();
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
      // previewOutcome is deliberately absent: a pre-cast preview is session
      // atmosphere, not state worth restoring.
      partialize: (state) => ({
        hasChart: state.hasChart,
        outcome: state.outcome,
        chartId: state.chartId,
        birthInfo: state.birthInfo,
        chartProfileId: state.chartProfileId,
      }),
    },
  ),
);
