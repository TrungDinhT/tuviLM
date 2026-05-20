import type { SessionStash } from "./types";

const KEY = "tuvi:laso";
const CLIENT_KEY = "tuvi:client-id";

export function saveStash(stash: SessionStash): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEY, JSON.stringify(stash));
}

export function loadStash(): SessionStash | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    if (
      !parsed ||
      typeof parsed.fetchedAt !== "string" ||
      !parsed.laso ||
      typeof parsed.laso.id !== "string" ||
      typeof parsed.laso.session_id !== "string" ||
      typeof parsed.laso.active_leaf_id !== "string" ||
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
  localStorage.removeItem(KEY);
}

export function getClientId(): string {
  if (typeof window === "undefined") return "";
  const existing = localStorage.getItem(CLIENT_KEY);
  if (existing) return existing;
  const id = typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `client-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  localStorage.setItem(CLIENT_KEY, id);
  return id;
}
