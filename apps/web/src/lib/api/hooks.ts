"use client";

import { skipToken, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useChartStore } from "@/store/chart-store";

import { useAccountRequestScope } from "./account-request";
import { request } from "./client";
import { apiEndpoints } from "./endpoints";
import { queryKeys } from "./queryKeys";
import {
  type BuildLasoResponse,
  type CreateRedeemCodeRequest,
  accountAccessSchema,
  createChartProfileResponseSchema,
  createRedeemCodeRequestSchema,
  createRedeemCodeResponseSchema,
  emptyResponseSchema,
  getSessionResponseSchema,
  listChartProfilesResponseSchema,
  listSessionsResponseSchema,
  renameChartProfileRequestSchema,
  redeemCodeRequestSchema,
  redeemCodeResponseSchema,
} from "./schemas";

export function useAccountAccess() {
  const { userId } = useAccountRequestScope();
  return useQuery({
    queryKey: queryKeys.accountAccess(userId ?? null),
    queryFn: ({ signal }) =>
      request(apiEndpoints.accountAccess, {
        schema: accountAccessSchema,
        withAuth: true,
        expectedUserId: userId,
        signal,
      }),
    enabled: Boolean(userId),
    staleTime: 0,
  });
}

export function useRedeemCode() {
  const queryClient = useQueryClient();
  const { getSignal, userId } = useAccountRequestScope();
  return useMutation({
    mutationFn: (code: string) =>
      request(apiEndpoints.redeemCode, {
        method: "POST",
        body: redeemCodeRequestSchema.parse({ code }),
        schema: redeemCodeResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        signal: getSignal(),
      }),
    onSuccess: async () => {
      if (getSignal()?.aborted) return;
      await queryClient.invalidateQueries({
        queryKey: queryKeys.accountAccess(userId ?? null),
        exact: true,
      });
    },
  });
}

export function useCreateRedeemCode() {
  const { getSignal, userId } = useAccountRequestScope();
  return useMutation({
    mutationFn: (input: CreateRedeemCodeRequest) =>
      request(apiEndpoints.createRedeemCode, {
        method: "POST",
        body: createRedeemCodeRequestSchema.parse(input),
        schema: createRedeemCodeResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        signal: getSignal(),
      }),
  });
}

/**
 * The cast chart, read cache-only.
 *
 * Data arrives via `setQueryData` after a cast or via the persisted-cache
 * restore on reload; the query never fetches. Missing data while `chartId` is
 * set is a desync the provider's reconciliation turns into a reset.
 */
export function useLasoChart() {
  const chartId = useChartStore((state) => state.chartId);
  return useQuery<BuildLasoResponse>({
    queryKey: queryKeys.laso.chart(chartId ?? "idle"),
    queryFn: skipToken,
  });
}

/**
 * The owner's saved chart profiles.
 *
 * Authoritative on the backend, so unlike the cast chart this is a real
 * network query with loading and error states. It is not persisted: the
 * query-cache persister whitelists only the cast-chart key family.
 */
export function useChartProfiles(enabled = true) {
  const { userId } = useAccountRequestScope();
  return useQuery({
    queryKey: queryKeys.chartProfiles.all(),
    queryFn: ({ signal }) =>
      request(apiEndpoints.chartProfiles, {
        schema: listChartProfilesResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        signal,
      }),
    enabled,
  });
}

/**
 * Delete one saved chart profile, then refresh the list.
 *
 * The endpoint answers `204` with no body, so the response parses through
 * `emptyResponseSchema`. Deletion is idempotent by nature and creates nothing,
 * so it carries the owner identity but no `Idempotency-Key`.
 */
export function useDeleteChartProfile() {
  const queryClient = useQueryClient();
  const { getSignal, userId } = useAccountRequestScope();
  return useMutation({
    mutationFn: (id: string) =>
      request(apiEndpoints.chartProfile(id), {
        method: "DELETE",
        schema: emptyResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        signal: getSignal(),
      }),
    onSuccess: () => {
      if (getSignal()?.aborted) return;
      void queryClient.invalidateQueries({ queryKey: queryKeys.chartProfiles.all() });
    },
  });
}

export function useRenameChartProfile() {
  const queryClient = useQueryClient();
  const { getSignal, userId } = useAccountRequestScope();
  return useMutation({
    mutationFn: ({ id, display_name }: { id: string; display_name: string }) =>
      request(apiEndpoints.chartProfile(id), {
        method: "PATCH",
        body: renameChartProfileRequestSchema.parse({ display_name }),
        schema: createChartProfileResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        signal: getSignal(),
      }),
    onSuccess: async () => {
      if (getSignal()?.aborted) return;
      await queryClient.invalidateQueries({ queryKey: queryKeys.chartProfiles.all() });
    },
  });
}

/**
 * The sessions under one chart profile, newest first. Disabled while the
 * profile is null — the chat screen resolves its session only after a cast
 * has produced a profile.
 */
export function useListSessions(profileId: string | null) {
  const { userId } = useAccountRequestScope();
  return useQuery({
    queryKey: queryKeys.sessions.byProfile(profileId ?? "idle"),
    queryFn: ({ signal }) =>
      request(apiEndpoints.profileSessions(profileId as string), {
        schema: listSessionsResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        signal,
      }),
    enabled: profileId !== null,
  });
}

/** One session's full message transcript. Disabled while no session is active. */
export function useGetSession(sessionId: string | null) {
  const { userId } = useAccountRequestScope();
  return useQuery({
    queryKey: queryKeys.sessions.detail(sessionId ?? "idle"),
    queryFn: ({ signal }) =>
      request(apiEndpoints.session(sessionId as string), {
        schema: getSessionResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        signal,
      }),
    enabled: sessionId !== null,
  });
}
