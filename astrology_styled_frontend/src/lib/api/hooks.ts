"use client";

import {
  keepPreviousData,
  skipToken,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { useChartStore } from "@/store/chart-store";

import { useAccountRequestScope } from "./account-request";
import { newIdempotencyKey, request } from "./client";
import { apiEndpoints } from "./endpoints";
import { queryKeys } from "./queryKeys";
import {
  type BirthInfo,
  type BuildLasoResponse,
  type ChartProfile,
  type CreateChartProfileRequest,
  type CreateRedeemCodeRequest,
  type PreviewLasoRequest,
  accountAccessSchema,
  buildLasoResponseSchema,
  createChartProfileRequestSchema,
  createChartProfileResponseSchema,
  createRedeemCodeRequestSchema,
  createRedeemCodeResponseSchema,
  createSessionRequestSchema,
  createSessionResponseSchema,
  emptyResponseSchema,
  getSessionResponseSchema,
  listChartProfilesResponseSchema,
  listSessionsResponseSchema,
  previewLasoRequestSchema,
  previewLasoResponseSchema,
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
 * Cast a chart from birth information.
 *
 * A mutation rather than a query because casting is user-initiated. The
 * backend builds the chart from this request without storing shared state.
 *
 * On success the response is also written into the query cache under its
 * deterministic id — that entry is the one query the persister keeps across
 * reloads. Callers still get the mutation result; the cache write is what
 * `useLasoChart` and later screens read.
 */
export function useBuildLaso() {
  const queryClient = useQueryClient();
  const { getSignal } = useAccountRequestScope();
  return useMutation({
    mutationFn: (birth: BirthInfo) =>
      request(apiEndpoints.buildLaso, {
        method: "POST",
        body: birth,
        schema: buildLasoResponseSchema,
        signal: getSignal(),
      }),
    onSuccess: (data) => {
      if (getSignal()?.aborted) return;
      queryClient.setQueryData(queryKeys.laso.chart(data.id), data);
    },
  });
}

/** Restore a saved chart and its newest conversation before activating it. */
export function useOpenChartProfile() {
  const queryClient = useQueryClient();
  const { getSignal, userId } = useAccountRequestScope();
  return useMutation({
    mutationFn: async (profile: ChartProfile) => {
      const signal = getSignal();
      const [chart, sessions] = await Promise.all([
        request(apiEndpoints.buildLaso, {
          method: "POST",
          body: profile.birth_info,
          schema: buildLasoResponseSchema,
          signal,
        }),
        request(apiEndpoints.profileSessions(profile.id), {
          schema: listSessionsResponseSchema,
          withAuth: true,
          expectedUserId: userId,
          signal,
        }),
      ]);
      // The chat opens on the newest conversation; the others load when selected.
      const newest = [...sessions.sessions].sort((a, b) =>
        b.updated_at.localeCompare(a.updated_at),
      )[0];
      const transcript =
        newest === undefined
          ? null
          : await request(apiEndpoints.session(newest.id), {
              schema: getSessionResponseSchema,
              withAuth: true,
              expectedUserId: userId,
              signal,
            });
      signal?.throwIfAborted();
      return { chart, sessions, transcript };
    },
    onSuccess: ({ chart, sessions, transcript }, profile) => {
      getSignal()?.throwIfAborted();
      queryClient.setQueryData(queryKeys.laso.chart(chart.id), chart);
      queryClient.setQueryData(queryKeys.sessions.byProfile(profile.id), sessions);
      if (transcript !== null) {
        queryClient.setQueryData(queryKeys.sessions.detail(transcript.session.id), transcript);
      }
    },
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
 * Preview cung Mệnh's chính tinh for the reward reveal.
 *
 * A query keyed by the mapped birth tuple: TanStack Query dedupes and orders
 * the responses, so a dial being spun can never apply a stale preview out of
 * order. `birth` is `null` until every input exists — the caller debounces;
 * this hook does not. Failures surface as the normalized `ApiError` so the
 * screen can choose to stay silent.
 */
export function useLasoPreview(birth: PreviewLasoRequest | null) {
  return useQuery({
    queryKey: queryKeys.laso.preview(birth),
    queryFn: ({ signal }) =>
      request(apiEndpoints.previewLaso, {
        method: "POST",
        body: previewLasoRequestSchema.parse(birth),
        schema: previewLasoResponseSchema,
        signal,
      }),
    enabled: birth !== null,
    // The response is a pure function of the birth tuple — it never goes stale.
    staleTime: Infinity,
    // While a new tuple loads, keep showing the previous preview: a spinning
    // dial must not make the reward flicker off and on.
    placeholderData: keepPreviousData,
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

/** A stable idempotency key for a chart profile, from its birth tuple. */
export function profileIdempotencyKey(birth: BirthInfo): string {
  return `profile:${birth.year}-${birth.month}-${birth.day}-${birth.hour}-${birth.gender}`;
}

/** A readable label for an auto-saved profile: the cast birth date. */
export function profileDisplayName(birth: BirthInfo): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(birth.day)}/${pad(birth.month)}/${birth.year}`;
}

/**
 * Create a chart profile from a birth tuple.
 *
 * The idempotency key is derived from the birth tuple, so re-casting the same
 * data reuses the same profile instead of accumulating duplicates. This is the
 * auto-save path the cast flow fires; the Hồ sơ screen's user-facing save is
 * still a separate change.
 */
export function useCreateChartProfile() {
  const queryClient = useQueryClient();
  const { getSignal, userId } = useAccountRequestScope();
  return useMutation({
    mutationFn: (input: CreateChartProfileRequest) =>
      request(apiEndpoints.chartProfiles, {
        method: "POST",
        body: createChartProfileRequestSchema.parse(input),
        schema: createChartProfileResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        idempotencyKey: profileIdempotencyKey(input.birth_info),
        signal: getSignal(),
      }),
    onSuccess: () => {
      if (getSignal()?.aborted) return;
      void queryClient.invalidateQueries({ queryKey: queryKeys.chartProfiles.all() });
    },
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

/**
 * Create a new session under a chart profile and refresh the session list.
 *
 * Each invocation mints a fresh `Idempotency-Key`; mutations never auto-retry,
 * so a manual retry is a fresh create action with its own key.
 */
export function useCreateSession(profileId: string | null) {
  const queryClient = useQueryClient();
  const { getSignal, userId } = useAccountRequestScope();
  return useMutation({
    mutationFn: () => {
      if (profileId === null) throw new Error("chart profile id required");
      return request(apiEndpoints.profileSessions(profileId), {
        method: "POST",
        body: createSessionRequestSchema.parse({ title: null }),
        schema: createSessionResponseSchema,
        withAuth: true,
        expectedUserId: userId,
        idempotencyKey: newIdempotencyKey(),
        signal: getSignal(),
      });
    },
    onSuccess: () => {
      if (getSignal()?.aborted) return;
      if (profileId === null) return;
      void queryClient.invalidateQueries({ queryKey: queryKeys.sessions.byProfile(profileId) });
    },
  });
}
