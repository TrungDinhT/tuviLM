import type { BirthInfo } from "./schemas";

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
