'use client';

import { useMutation } from '@tanstack/react-query';
import { buildLaso, buildSaoLuu } from './client';
import type {
  BuildLasoRequest,
  BuildLasoResponse,
  BuildSaoLuuRequest,
  BuildSaoLuuResponse,
} from './schemas';
import type { ApiError } from '@/lib/http/errors';

export function useBuildLaso() {
  return useMutation<BuildLasoResponse, ApiError, BuildLasoRequest>({
    mutationFn: buildLaso,
  });
}

export function useBuildSaoLuu() {
  return useMutation<BuildSaoLuuResponse, ApiError, BuildSaoLuuRequest>({
    mutationFn: buildSaoLuu,
  });
}
