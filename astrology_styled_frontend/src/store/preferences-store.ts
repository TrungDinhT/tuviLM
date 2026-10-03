import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import { safeStorage } from "@/lib/safe-storage";

export const MUTE_BIRTH_CONFIRM_KEY = "tuvi.muteBirthConfirm";

interface PreferencesState {
  /**
   * The user ticked "không nhắc lại" on the birth-date confirmation, so
   * casting should proceed without asking again.
   */
  muteBirthConfirm: boolean;
  setMuteBirthConfirm: (muted: boolean) => void;
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      muteBirthConfirm: false,
      setMuteBirthConfirm: (muted) => set({ muteBirthConfirm: muted }),
    }),
    {
      name: MUTE_BIRTH_CONFIRM_KEY,
      // Blocked storage reads as "no preference stored", so casting keeps
      // asking rather than failing. See lib/safe-storage.ts.
      storage: createJSONStorage(() => safeStorage),
      skipHydration: true,
    },
  ),
);
