/**
 * `localStorage` that cannot throw.
 *
 * Storage is unavailable in a restricted embed, in some private modes, and
 * whenever a quota is exhausted. None of those may break a user flow, so every
 * access is contained here and failure reads as "nothing stored".
 *
 * The method names match the DOM `Storage` shape on purpose, so this can be
 * handed straight to Zustand's `createJSONStorage`.
 */
export const safeStorage = {
  getItem(key: string): string | null {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },

  setItem(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch {
      // Nothing to do: the value simply will not persist.
    }
  },

  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch {
      // As above.
    }
  },
};
