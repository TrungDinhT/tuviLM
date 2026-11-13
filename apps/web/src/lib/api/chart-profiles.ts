import { mutationOptions } from "@tanstack/react-query";

import { outcomeFromChart } from "@/features/an-sao/outcome";
import { useChartStore } from "@/store/chart-store";

import type { AccountRequestScope } from "./account-request";
import { request } from "./client";
import { apiEndpoints } from "./endpoints";
import { mutationKeys, queryKeys } from "./queryKeys";
import {
  type BirthInfo,
  type ChartProfile,
  buildLasoResponseSchema,
  getSessionResponseSchema,
  listSessionsResponseSchema,
} from "./schemas";

/**
 * Restore a saved chart and its newest conversation, then make it the chart
 * being read.
 *
 * The cache and store writes are in `onSuccess` here, not in the caller's
 * `mutate` callbacks: those do not run if the caller unmounts before the
 * request ends, and the chart must switch either way. Callers add UI work only
 * (navigate, close a panel, show a toast).
 *
 * To know if any unit is opening a chart, read
 * `useIsMutating({ mutationKey: mutationKeys.openChartProfile() })`.
 */
export const openChartProfileMutationOptions = ({ getSignal, userId }: AccountRequestScope) =>
  mutationOptions({
    mutationKey: mutationKeys.openChartProfile(),
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
    onSuccess: ({ chart, sessions, transcript }, profile, _onMutateResult, { client }) => {
      getSignal()?.throwIfAborted();
      client.setQueryData(queryKeys.laso.chart(chart.id), chart);
      client.setQueryData(queryKeys.sessions.byProfile(profile.id), sessions);
      if (transcript !== null) {
        client.setQueryData(queryKeys.sessions.detail(transcript.session.id), transcript);
      }
      useChartStore
        .getState()
        .castChart(outcomeFromChart(chart), chart.id, profile.birth_info, profile.id);
    },
  });

/** A stable idempotency key for a chart profile, from its birth tuple. */
export const profileIdempotencyKey = (birth: BirthInfo): string =>
  `profile:${birth.year}-${birth.month}-${birth.day}-${birth.hour}-${birth.gender}`;

const pad2 = (n: number) => String(n).padStart(2, "0");

/** A readable label for an auto-saved profile: the cast birth date. */
export const profileDisplayName = (birth: BirthInfo): string =>
  `${pad2(birth.day)}/${pad2(birth.month)}/${birth.year}`;
