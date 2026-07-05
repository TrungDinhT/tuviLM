import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  BuildLasoResponse,
  BuildSaoLuuResponse,
  Gender,
} from '@/lib/api/schemas';

export interface BirthInput {
  date: number;
  month: number;
  year: number;
  hour: number;
  gender: Gender;
  name?: string;
}

export interface HistoryEntry {
  id: string;
  builtAt: number;
  input: BirthInput;
  response: BuildLasoResponse;
}

interface ChartState {
  ownerId: string | null;
  chartProfileId: string | null;
  sessionId: string | null;
  lastInput: BirthInput | null;
  current: BuildLasoResponse | null;
  saoLuuOverlay: BuildSaoLuuResponse | null;
  selectedCungPosition: string | null;
  history: HistoryEntry[];

  setConversationContext: (ownerId: string, chartProfileId: string, sessionId: string) => void;
  setCurrent: (input: BirthInput, response: BuildLasoResponse) => void;
  setSaoLuuOverlay: (overlay: BuildSaoLuuResponse) => void;
  clearSaoLuu: () => void;
  selectCung: (position: string | null) => void;
  addToHistory: (entry: HistoryEntry) => void;
  removeFromHistory: (id: string) => void;
  loadFromHistory: (id: string) => void;
}

const HISTORY_CAP = 20;

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
      history: [],

      setConversationContext: (ownerId, chartProfileId, sessionId) =>
        set({ ownerId, chartProfileId, sessionId }),

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

      addToHistory: (entry) =>
        set((state) => ({
          history: [entry, ...state.history.filter((h) => h.id !== entry.id)].slice(0, HISTORY_CAP),
        })),

      removeFromHistory: (id) =>
        set((state) => ({
          history: state.history.filter((h) => h.id !== id),
        })),

      loadFromHistory: (id) =>
        set((state) => {
          const entry = state.history.find((h) => h.id === id);
          if (!entry) return state;
          return {
            ...state,
            lastInput: entry.input,
            current: entry.response,
            saoLuuOverlay: null,
            selectedCungPosition: null,
          };
        }),
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
        history: state.history,
      }),
    },
  ),
);
