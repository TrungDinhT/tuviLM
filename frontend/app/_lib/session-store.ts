import type { SessionStash } from "./types";

const KEY = "tuvi:laso";

export function saveStash(stash: SessionStash): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(KEY, JSON.stringify(stash));
}

export function loadStash(): SessionStash | null {
  if (typeof window === "undefined") return null;
  const raw = sessionStorage.getItem(KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (
      !parsed ||
      typeof parsed.fetchedAt !== "string" ||
      !parsed.laso ||
      typeof parsed.laso.id !== "string" ||
      !parsed.laso.cung_by_position ||
      !parsed.profile ||
      typeof parsed.profile.name !== "string"
    ) {
      clearStash();
      return null;
    }
    return parsed as SessionStash;
  } catch {
    return null;
  }
}

export function clearStash(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(KEY);
}
