"use client";

import { createSyncStoragePersister } from "@tanstack/query-sync-storage-persister";
import { QueryClient } from "@tanstack/react-query";
import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client";
import { useEffect, useState } from "react";

import {
  bindChartResetClearing,
  reconcileChartState,
  shouldPersistQuery,
} from "@/lib/api/chart-persistence";
import { queryKeys } from "@/lib/api/queryKeys";
import { isApiError } from "@/lib/http/errors";
import { safeStorage } from "@/lib/safe-storage";
import { useChartStore } from "@/store/chart-store";

/** The persisted cache's storage key. Only the cast chart ever lands here. */
const QUERY_CACHE_KEY = "tuvi.query-cache";

/**
 * TanStack Query, configured for this backend.
 *
 * The client is created in state rather than at module scope so each render
 * tree owns its own — at module scope a server render would share one client
 * across requests.
 *
 * Retry policy: network failures are worth retrying, a 4xx never is, and a
 * schema drift certainly is not — retrying either just repeats the same
 * failure more slowly.
 *
 * Persistence: exactly one query family — the cast chart — is dehydrated to
 * storage, through the throwing-safe storage wrapper. Everything else stays
 * memory-only. Restore lands after mount, so the first client render still
 * matches the server's.
 */
export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [client] = useState(() => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 60_000,
          retry: (failureCount, error) => {
            if (!isApiError(error)) return false;
            if (error.error.kind !== "network") return false;
            return failureCount < 2;
          },
        },
        mutations: { retry: false },
      },
    });
    // The cast chart must never be garbage-collected: eviction would also
    // drop it from the persisted cache, and the next reload would lose it.
    queryClient.setQueryDefaults(queryKeys.laso.chartAll(), {
      gcTime: Infinity,
      staleTime: Infinity,
    });
    return queryClient;
  });
  const [persister] = useState(() =>
    createSyncStoragePersister({
      key: QUERY_CACHE_KEY,
      // Structurally the Storage subset the persister needs; safeStorage
      // contains every throw.
      storage: safeStorage,
    }),
  );

  useEffect(() => bindChartResetClearing(client), [client]);

  return (
    <PersistQueryClientProvider
      client={client}
      persistOptions={{
        persister,
        dehydrateOptions: { shouldDehydrateQuery: shouldPersistQuery },
      }}
      onSuccess={() => {
        // Reconciliation needs both halves restored: the query cache (just
        // resolved) and the chart store. The rehydrate call is idempotent —
        // StoreHydration may already have done it.
        void Promise.resolve(useChartStore.persist.rehydrate()).then(() => {
          reconcileChartState(client);
        });
      }}
    >
      {children}
    </PersistQueryClientProvider>
  );
}
