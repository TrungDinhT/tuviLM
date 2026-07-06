'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  buildLaso,
  buildSaoLuu,
  createAnonymous,
  createChartProfile,
  createSession,
  deleteChartProfile,
  deleteSession,
  getSession,
  listChartProfiles,
  listSessions,
  streamSessionChat,
} from './client';
import { queryKeys } from './queryKeys';
import {
  type BuildLasoRequest,
  type BuildLasoResponse,
  type BuildSaoLuuRequest,
  type BuildSaoLuuResponse,
  type ChartProfile,
  type ChatDebugEvent,
  type ChatResponse,
  type GetSessionResponse,
  type ListChartProfilesResponse,
  type ListSessionsResponse,
} from './schemas';
import type { ApiError } from '@/lib/http/errors';
import type { BirthInput } from '@/store/chart-store';

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

export function useChartProfiles(ownerId: string | null) {
  return useQuery<ListChartProfilesResponse, ApiError>({
    queryKey: queryKeys.chat.chartProfiles(ownerId),
    queryFn: () => listChartProfiles(ownerId!),
    enabled: Boolean(ownerId),
  });
}

export function useSessions(ownerId: string | null, chartProfileId: string | null) {
  return useQuery<ListSessionsResponse, ApiError>({
    queryKey: queryKeys.chat.sessions(ownerId, chartProfileId),
    queryFn: async () => {
      const data = await listSessions(chartProfileId!, ownerId!);
      return {
        sessions: [...data.sessions].sort(
          (a, b) => Date.parse(b.updated_at) - Date.parse(a.updated_at),
        ),
      };
    },
    enabled: Boolean(ownerId && chartProfileId),
  });
}

export interface OpenChartSessionArgs {
  ownerId: string;
  profile: ChartProfile;
  sessionId: string | null;
}

export interface OpenChartSessionResult {
  ownerId: string;
  chartProfileId: string;
  sessionId: string;
  input: BirthInput;
  response: BuildLasoResponse;
}

export function useOpenChartSession() {
  const queryClient = useQueryClient();
  return useMutation<OpenChartSessionResult, ApiError, OpenChartSessionArgs>({
    mutationFn: async ({ ownerId, profile, sessionId }) => {
      const openedSessionId =
        sessionId ??
        (
          await createSession(
            profile.id,
            { title: profile.display_name },
            ownerId,
            idempotencyKey('session'),
          )
        ).session.id;
      const { day, month, year, hour, gender } = profile.birth_info;
      const response = await buildLaso({ day, month, year, hour, gender });

      return {
        ownerId,
        chartProfileId: profile.id,
        sessionId: openedSessionId,
        input: {
          date: day,
          month,
          year,
          hour,
          gender,
          name: profile.display_name,
        },
        response,
      };
    },
    onSuccess: (result) => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.chat.sessions(result.ownerId, result.chartProfileId),
      });
    },
  });
}

export interface DeleteChartProfileArgs {
  ownerId: string;
  chartProfileId: string;
}

export function useDeleteChartProfile() {
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, DeleteChartProfileArgs>({
    mutationFn: ({ ownerId, chartProfileId }) => deleteChartProfile(chartProfileId, ownerId),
    onSuccess: (_data, vars) => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.chat.chartProfiles(vars.ownerId),
      });
      void queryClient.invalidateQueries({
        queryKey: queryKeys.chat.sessions(vars.ownerId, vars.chartProfileId),
      });
    },
  });
}

export interface DeleteSessionArgs {
  ownerId: string;
  chartProfileId: string;
  sessionId: string;
}

export function useDeleteSession() {
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, DeleteSessionArgs>({
    mutationFn: ({ ownerId, sessionId }) => deleteSession(sessionId, ownerId),
    onSuccess: (_data, vars) => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.chat.sessions(vars.ownerId, vars.chartProfileId),
      });
      void queryClient.invalidateQueries({
        queryKey: queryKeys.chat.session(vars.ownerId, vars.sessionId),
      });
    },
  });
}

export function useSession(ownerId: string | null, sessionId: string | null) {
  return useQuery<GetSessionResponse, ApiError>({
    queryKey: queryKeys.chat.session(ownerId, sessionId),
    queryFn: () => getSession(sessionId!, ownerId!),
    enabled: Boolean(ownerId && sessionId),
  });
}

export interface ChatMutateArgs {
  message: string;
  ownerId: string | null;
  chartProfileId: string | null;
  sessionId: string | null;
  onTextDelta?: (delta: string) => void;
  onDebugEvent?: (event: ChatDebugEvent) => void;
}

export function useChat() {
  const queryClient = useQueryClient();
  return useMutation<ChatResponse, ApiError, ChatMutateArgs>({
    mutationFn: ({ message, ownerId, sessionId, onTextDelta, onDebugEvent }) => {
      if (!ownerId || !sessionId) throw { kind: 'no-session' } satisfies ApiError;
      return streamSessionChat(
        sessionId,
        { content: message },
        ownerId,
        idempotencyKey('message'),
        onTextDelta,
        onDebugEvent,
      );
    },
    onSuccess: (_data, vars) => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.chat.session(vars.ownerId, vars.sessionId),
      });
      void queryClient.invalidateQueries({
        queryKey: queryKeys.chat.sessions(vars.ownerId, vars.chartProfileId),
      });
    },
  });
}
