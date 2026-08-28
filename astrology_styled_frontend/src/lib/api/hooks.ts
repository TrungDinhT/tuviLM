"use client";

import {
  keepPreviousData,
  skipToken,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { useChartStore } from "@/store/chart-store";

import { request } from "./client";
import { queryKeys } from "./queryKeys";
import {
  type BirthInfo,
  type BuildLasoResponse,
  type PreviewLasoRequest,
  buildLasoResponseSchema,
  emptyResponseSchema,
  listChartProfilesResponseSchema,
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
