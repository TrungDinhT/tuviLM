import type { BuildLasoRequest, BuildSaoLuuRequest } from './schemas';

export const queryKeys = {
  laso: {
    build: (req: BuildLasoRequest) => ['laso', 'build', req] as const,
    saoLuu: (req: BuildSaoLuuRequest) => ['laso', 'sao-luu', req] as const,
  },
} as const;
