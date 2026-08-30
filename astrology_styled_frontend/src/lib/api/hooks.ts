"use client";

import {
  keepPreviousData,
  skipToken,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { useChartStore } from "@/store/chart-store";

import { newIdempotencyKey, request } from "./client";
import { queryKeys } from "./queryKeys";
import {
  type BirthInfo,
  type BuildLasoResponse,
  type CreateChartProfileRequest,
  type PreviewLasoRequest,
  buildLasoResponseSchema,
  createChartProfileRequestSchema,
  createChartProfileResponseSchema,
  createSessionRequestSchema,
  createSessionResponseSchema,
  emptyResponseSchema,
  getSessionResponseSchema,
  listChartProfilesResponseSchema,
  listSessionsResponseSchema,
  previewLasoRequestSchema,
  previewLasoResponseSchema,
} from "./schemas";

/**
 * Cast a chart from birth information.
 *
 * A mutation rather than a query: the call is user-initiated and has a side
 * effect on the backend, which stores the built lá số for the sao-lưu and chat
 * endpoints to read.
 *
 * On success the response is also written into the query cache under its
 * deterministic id — that entry is the one query the persister keeps across
 * reloads. Callers still get the mutation result; the cache write is what
 * `useLasoChart` and later screens read.
 */
export function useBuildLaso() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (birth: BirthInfo) =>
      request("/api/v1/laso/build", {
        method: "POST",
        body: birth,
        schema: buildLasoResponseSchema,
      }),
    onSuccess: (data) => {
      queryClient.setQueryData(queryKeys.laso.chart(data.id), data);
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
    queryFn: () =>
      request("/api/v1/laso/preview", {
        method: "POST",
        body: previewLasoRequestSchema.parse(birth),
        schema: previewLasoResponseSchema,
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
export function useChartProfiles() {
  return useQuery({
    queryKey: queryKeys.chartProfiles.all(),
    queryFn: () =>
      request("/api/v1/chart-profiles", {
        schema: listChartProfilesResponseSchema,
        withOwner: true,
      }),
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
  return useMutation({
    mutationFn: (input: CreateChartProfileRequest) =>
      request("/api/v1/chart-profiles", {
        method: "POST",
        body: createChartProfileRequestSchema.parse(input),
        schema: createChartProfileResponseSchema,
        withOwner: true,
        idempotencyKey: profileIdempotencyKey(input.birth_info),
      }),
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
  return useMutation({
    mutationFn: (id: string) =>
      request(`/api/v1/chart-profiles/${id}`, {
        method: "DELETE",
        schema: emptyResponseSchema,
        withOwner: true,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.chartProfiles.all() });
    },
  });
}

/**
 * The sessions under one chart profile, newest first. Disabled while the
 * profile is null — the chat screen resolves its session only after a cast
 * has produced a profile.
 */
export function useListSessions(profileId: string | null) {
  return useQuery({
    queryKey: queryKeys.sessions.byProfile(profileId ?? "idle"),
    queryFn: () =>
      request(`/api/v1/chart-profiles/${profileId as string}/sessions`, {
        schema: listSessionsResponseSchema,
        withOwner: true,
      }),
    enabled: profileId !== null,
  });
}

/** One session's full message transcript. Disabled while no session is active. */
export function useGetSession(sessionId: string | null) {
  return useQuery({
    queryKey: queryKeys.sessions.detail(sessionId ?? "idle"),
    queryFn: () =>
      request(`/api/v1/sessions/${sessionId as string}`, {
        schema: getSessionResponseSchema,
        withOwner: true,
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
  return useMutation({
    mutationFn: () => {
      if (profileId === null) throw new Error("chart profile id required");
      return request(`/api/v1/chart-profiles/${profileId}/sessions`, {
        method: "POST",
        body: createSessionRequestSchema.parse({ title: null }),
        schema: createSessionResponseSchema,
        withOwner: true,
        idempotencyKey: newIdempotencyKey(),
      });
    },
    onSuccess: () => {
      if (profileId === null) return;
      void queryClient.invalidateQueries({ queryKey: queryKeys.sessions.byProfile(profileId) });
    },
  });
}
