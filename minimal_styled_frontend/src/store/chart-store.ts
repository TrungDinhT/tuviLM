import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  BuildLasoRequest,
  BuildLasoResponse,
  BuildSaoLuuResponse,
} from '@/lib/api/schemas';

export type BirthInput = BuildLasoRequest & {
  name?: string;
};

export interface HistoryEntry {
  id: string;
  builtAt: number;
  input: BirthInput;
  response: BuildLasoResponse;
}

interface ChartState {
  lastInput: BirthInput | null;
  current: BuildLasoResponse | null;
  saoLuuOverlay: BuildSaoLuuResponse | null;
  selectedCungPosition: string | null;
  history: HistoryEntry[];

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
      lastInput: null,
      current: null,
      saoLuuOverlay: null,
      selectedCungPosition: null,
      history: [],

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
        lastInput: state.lastInput,
        current: state.current,
        history: state.history,
      }),
    },
  ),
);
