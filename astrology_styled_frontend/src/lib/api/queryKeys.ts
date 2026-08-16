import type { BirthInfo, PreviewLasoRequest } from "./schemas";

/**
 * Every TanStack Query key, defined once.
 *
 * Keys written inline at call sites drift: an invalidation ends up spelling a
 * key one way and the query another, and the refresh silently never happens.
 */
export const queryKeys = {
  health: () => ["health"] as const,

  laso: {
    all: () => ["laso"] as const,
    /** Prefix of the chart family, for query defaults and predicates. */
    chartAll: () => ["laso", "chart"] as const,
    /**
     * The cast chart, keyed by the response's deterministic id. This is the
     * only key family the query-cache persister whitelists — see
     * `components/providers/query-provider.tsx`.
     */
    chart: (id: string) => ["laso", "chart", id] as const,
    /** "idle" keeps the disabled query's key inside this module too. */
    preview: (birth: PreviewLasoRequest | null) =>
      ["laso", "preview", birth ?? "idle"] as const,
    build: (birth: BirthInfo) => ["laso", "build", birth] as const,
    saoLuu: (observation: BirthInfo) => ["laso", "saoLuu", observation] as const,
  },

  chartProfiles: {
    all: () => ["chartProfiles"] as const,
  },

  sessions: {
    all: () => ["sessions"] as const,
    detail: (sessionId: string) => ["sessions", sessionId] as const,
  },
} as const;

/**
 * The persistence whitelist: only the cast chart survives a reload. Every
 * other query — previews included — stays transient.
 */
export function isPersistedQueryKey(key: readonly unknown[]): boolean {
  return key[0] === "laso" && key[1] === "chart";
}
