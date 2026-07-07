import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  BuildLasoResponse,
  BuildSaoLuuResponse,
  DiaChiId,
  Gender,
} from '@/lib/api/schemas';

export interface BirthInput {
  calendar?: 'solar' | 'lunar';
  date: number;
  month: number;
  year: number;
  hour?: number;
  hour_in_dia_chi?: DiaChiId;
  is_leap_month?: boolean;
  gender: Gender;
  name?: string;
}

interface ChartState {
  ownerId: string | null;
  chartProfileId: string | null;
  sessionId: string | null;
  lastInput: BirthInput | null;
  current: BuildLasoResponse | null;
  saoLuuOverlay: BuildSaoLuuResponse | null;
  selectedCungPosition: string | null;

  setConversationContext: (ownerId: string, chartProfileId: string, sessionId: string) => void;
  clearConversationContext: () => void;
  setCurrent: (input: BirthInput, response: BuildLasoResponse) => void;
  setSaoLuuOverlay: (overlay: BuildSaoLuuResponse) => void;
  clearSaoLuu: () => void;
  selectCung: (position: string | null) => void;
}

export const useChartStore = create<ChartState>()(
  persist(
    (set) => ({
      ownerId: null,
      chartProfileId: null,
      sessionId: null,
      lastInput: null,
      current: null,
      saoLuuOverlay: null,
      selectedCungPosition: null,

      setConversationContext: (ownerId, chartProfileId, sessionId) =>
        set({ ownerId, chartProfileId, sessionId }),

      clearConversationContext: () =>
        set({
          chartProfileId: null,
          sessionId: null,
          lastInput: null,
          current: null,
          saoLuuOverlay: null,
          selectedCungPosition: null,
        }),

      setCurrent: (input, response) =>
        set({
          lastInput: input,
          current: response,
          saoLuuOverlay: null,
          selectedCungPosition: null,
        }),

      setSaoLuuOverlay: (overlay) => set({ saoLuuOverlay: overlay }),
      clearSaoLuu: () => set({ saoLuuOverlay: null }),
      selectCung: (position) => set({ selectedCungPosition: position }),
    }),
    {
      name: 'tuvilm:store:v1',
      version: 1,
      partialize: (state) => ({
        ownerId: state.ownerId,
        chartProfileId: state.chartProfileId,
        sessionId: state.sessionId,
        lastInput: state.lastInput,
        current: state.current,
      }),
    },
  ),
);
