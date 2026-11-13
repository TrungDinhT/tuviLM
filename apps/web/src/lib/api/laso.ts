import { keepPreviousData, mutationOptions, queryOptions } from "@tanstack/react-query";

import { outcomeFromChart } from "@/features/an-sao/outcome";
import { useChartStore } from "@/store/chart-store";

import type { AccountRequestScope } from "./account-request";
import { profileDisplayName, profileIdempotencyKey } from "./chart-profiles";
import { request } from "./client";
import { apiEndpoints } from "./endpoints";
import { mutationKeys, queryKeys } from "./queryKeys";
import {
  type BirthInfo,
  type PreviewLasoRequest,
  buildLasoResponseSchema,
  createChartProfileRequestSchema,
  createChartProfileResponseSchema,
  previewLasoRequestSchema,
  previewLasoResponseSchema,
} from "./schemas";

/**
 * Preview cung Mệnh's chính tinh for the reward reveal.
 *
 * A query keyed by the mapped birth tuple: TanStack Query dedupes and orders
 * the responses, so a dial being spun can never apply a stale preview out of
 * order. `birth` is `null` until every input exists — the caller debounces;
 * this query does not. Failures surface as the normalized `ApiError` so the
 * screen can choose to stay silent.
 */
export const lasoPreviewQueryOptions = ({ birth }: { birth: PreviewLasoRequest | null }) =>
  queryOptions({
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

/**
 * Cast a chart: build it, save it for a signed-in account, then make it the
 * chart being read.
 *
 * One mutation, so the caller does not chain requests by hand. The cache and
 * store writes are in `onSuccess` here and always run; the caller adds UI work
 * only (navigate, show a toast).
 *
 * The build response is written into the query cache under its deterministic
 * id — that entry is the one query the persister keeps across reloads, and
 * what `useLasoChart` and later screens read.
 *
 * `minDurationMs` holds the result back until the loading interlude has had
 * its time. It is here, not in the caller, because the store write changes the
 * shell (navigation, accent) and must not land while the loader is on screen.
 */
export const castChartMutationOptions = ({
  getSignal,
  userId,
  minDurationMs = 0,
}: AccountRequestScope & { minDurationMs?: number }) =>
  mutationOptions({
    mutationKey: mutationKeys.castChart(),
    mutationFn: async (birth: BirthInfo) => {
      const signal = getSignal();
      const minimum = new Promise((resolve) => setTimeout(resolve, minDurationMs));
      const chart = await request(apiEndpoints.buildLaso, {
        method: "POST",
        body: birth,
        schema: buildLasoResponseSchema,
        signal,
      });
      // Auto-save starts only after a valid build. It must never fail the
      // cast, so it resolves to the profile id or null. The idempotency key
      // comes from the birth tuple: casting the same data again reuses the
      // same profile.
      const profileId = userId
        ? await request(apiEndpoints.chartProfiles, {
            method: "POST",
            body: createChartProfileRequestSchema.parse({
              display_name: profileDisplayName(birth),
              birth_info: birth,
            }),
            schema: createChartProfileResponseSchema,
            withAuth: true,
            expectedUserId: userId,
            idempotencyKey: profileIdempotencyKey(birth),
            signal,
          }).then(
            (response) => response.chart_profile.id,
            () => null,
          )
        : null;
      await minimum;
      signal?.throwIfAborted();
      return { chart, profileId };
    },
    onSuccess: ({ chart, profileId }, birth, _onMutateResult, { client }) => {
      getSignal()?.throwIfAborted();
      client.setQueryData(queryKeys.laso.chart(chart.id), chart);
      if (profileId !== null) {
        void client.invalidateQueries({ queryKey: queryKeys.chartProfiles.all() });
      }
      useChartStore.getState().castChart(outcomeFromChart(chart), chart.id, birth, profileId);
    },
  });
