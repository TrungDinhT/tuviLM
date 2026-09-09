import { create } from "zustand";

interface ToastState {
  message: string | null;
  show: (message: string) => void;
  dismiss: () => void;
}

/**
 * One transient message at a time, matching the design.
 *
 * Not persisted: a toast that survives a reload would be reporting on
 * something the user can no longer see.
 */
export const useToastStore = create<ToastState>((set) => ({
  message: null,
  show: (message) => set({ message }),
  dismiss: () => set({ message: null }),
}));
