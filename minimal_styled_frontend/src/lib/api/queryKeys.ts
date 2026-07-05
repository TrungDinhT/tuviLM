import type { BuildLasoRequest, BuildSaoLuuRequest } from './schemas';

export const queryKeys = {
  laso: {
    build: (req: BuildLasoRequest) => ['laso', 'build', req] as const,
    saoLuu: (req: BuildSaoLuuRequest) => ['laso', 'sao-luu', req] as const,
  },
  chat: {
    chartProfiles: (ownerId: string | null) => ['chat', 'chart-profiles', ownerId] as const,
    sessions: (ownerId: string | null, chartProfileId: string | null) =>
      ['chat', 'sessions', ownerId, chartProfileId] as const,
    session: (ownerId: string | null, sessionId: string | null) =>
      ['chat', 'session', ownerId, sessionId] as const,
  },
} as const;
