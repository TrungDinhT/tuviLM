'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { buildLaso, buildSaoLuu, chat } from './client';
import {
  NO_LASO_SENTINEL,
  type BuildLasoRequest,
  type BuildLasoResponse,
  type BuildSaoLuuRequest,
  type BuildSaoLuuResponse,
  type ChatRequest,
  type ChatResponse,
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

export interface ChatMutateArgs {
  message: string;
  lastInput: BuildLasoRequest | null;
  applyBuildResponse: (resp: BuildLasoResponse) => void;
  onResync?: () => void;
}

export interface ChatWithResyncDeps {
  chat: (req: ChatRequest) => Promise<ChatResponse>;
  buildLaso: (req: BuildLasoRequest) => Promise<BuildLasoResponse>;
}

/**
 * Chat with transparent server-resync. If `/chat` returns the sentinel
 * answer indicating the server has no `la_so`, re-prime the server via
 * `/laso/build` (using the cached `lastInput`) and retry `/chat` once.
 * See [[chat-real-api]] design Decision 1.
 *
 * Server state is single-tenant (one global `app.state.api_state`). A
 * future multi-tenant model would replace this whole helper.
 */
export async function chatWithResync(
  args: ChatMutateArgs,
  deps: ChatWithResyncDeps,
): Promise<ChatResponse> {
  const first = await deps.chat({ message: args.message });
  if (first.answer !== NO_LASO_SENTINEL) return first;

  if (args.lastInput == null) {
    throw { kind: 'no-la-so', requiresRebuild: true } satisfies ApiError;
  }

  args.onResync?.();
  const build = await deps.buildLaso(args.lastInput);
  args.applyBuildResponse(build);

  const second = await deps.chat({ message: args.message });
  if (second.answer === NO_LASO_SENTINEL) {
    throw { kind: 'no-la-so', requiresRebuild: false } satisfies ApiError;
  }
  return second;
}

export function useChat() {
  const [isResyncing, setIsResyncing] = useState(false);
  const mutation = useMutation<ChatResponse, ApiError, ChatMutateArgs>({
    mutationFn: (args) =>
      chatWithResync(
        { ...args, onResync: () => setIsResyncing(true) },
        { chat, buildLaso },
      ),
    onSettled: () => setIsResyncing(false),
  });
  return { ...mutation, isResyncing };
}
