'use client';

import { useMutation } from '@tanstack/react-query';
import {
  buildLaso,
  buildSaoLuu,
  createAnonymous,
  createChartProfile,
  createSession,
  streamSessionChat,
} from './client';
import {
  type BuildLasoRequest,
  type BuildLasoResponse,
  type BuildSaoLuuRequest,
  type BuildSaoLuuResponse,
  type ChatResponse,
} from './schemas';
import type { ApiError } from '@/lib/http/errors';

function idempotencyKey(prefix: string): string {
  return `${prefix}-${crypto.randomUUID()}`;
}

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

export interface CreateChartSessionArgs {
  ownerId: string | null;
  displayName: string;
  birthInfo: BuildLasoRequest;
}

export interface CreateChartSessionResult {
  ownerId: string;
  chartProfileId: string;
  sessionId: string;
}

export function useCreateChartSession() {
  return useMutation<CreateChartSessionResult, ApiError, CreateChartSessionArgs>({
    mutationFn: async ({ ownerId, displayName, birthInfo }) => {
      const owner = ownerId ?? (await createAnonymous()).owner_id;
      const profile = await createChartProfile(
        {
          display_name: displayName,
          birth_info: { calendar: 'solar', ...birthInfo },
        },
        owner,
        idempotencyKey('profile'),
      );
      const session = await createSession(
        profile.chart_profile.id,
        { title: displayName },
        owner,
        idempotencyKey('session'),
      );
      return {
        ownerId: owner,
        chartProfileId: profile.chart_profile.id,
        sessionId: session.session.id,
      };
    },
  });
}

export interface ChatMutateArgs {
  message: string;
  ownerId: string | null;
  sessionId: string | null;
  onTextDelta?: (delta: string) => void;
}

export function useChat() {
  return useMutation<ChatResponse, ApiError, ChatMutateArgs>({
    mutationFn: ({ message, ownerId, sessionId, onTextDelta }) => {
      if (!ownerId || !sessionId) throw { kind: 'no-session' } satisfies ApiError;
      return streamSessionChat(
        sessionId,
        { content: message },
        ownerId,
        idempotencyKey('message'),
        onTextDelta,
      );
    },
  });
}
