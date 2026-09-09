import type { Query, QueryClient } from "@tanstack/react-query";

import { useChartStore } from "@/store/chart-store";

import { isPersistedQueryKey } from "./queryKeys";
import { buildLasoResponseSchema } from "./schemas";

/**
 * The bridge between the persisted query cache and the chart store.
 *
 * The cast chart lives in the TanStack Query cache under `["laso", chartId]`
 * and is the only query family dehydrated to storage. The chart store holds
 * the matching `chartId`, so the two must never disagree: a flag claiming a
 * chart the cache cannot show is worse than no flag at all.
 */

/** Dehydration filter handed to the query-cache persister. */
export function shouldPersistQuery(query: Query): boolean {
  return isPersistedQueryKey(query.queryKey);
}

/**
 * Favour the safe direction on desync: if the store believes a chart exists
 * but the (restored) cache holds none, reset to the empty chart state rather
 * than render chart-dependent screens without data. Run once the cache has
 * been restored AND the store rehydrated — see the query provider.
 */
export function reconcileChartState(queryClient: QueryClient): void {
  if (!useChartStore.getState().hasChart) return;

  // A persisted payload that fails the current schema — one written by an
  // older build, say — is not a usable chart: the screens reading it would
  // render half a deck. It reconciles to the empty state exactly like a
  // missing one.
  const hasUsableChart = queryClient
    .getQueriesData({ predicate: (query) => isPersistedQueryKey(query.queryKey) })
    .some(([, data]) => buildLasoResponseSchema.safeParse(data).success);

  if (!hasUsableChart) useChartStore.getState().reset();
}

/**
 * Clearing the chart must also clear its persisted payload, or a stale chart
 * would reappear on the next reload. The store stays free of query-client
 * knowledge; this subscription does the coupling. Returns the unsubscribe.
 */
export function bindChartResetClearing(queryClient: QueryClient): () => void {
  return useChartStore.subscribe((state, previous) => {
    if (previous.hasChart && !state.hasChart) {
      queryClient.removeQueries({
        predicate: (query) => isPersistedQueryKey(query.queryKey),
      });
    }
  });
}
