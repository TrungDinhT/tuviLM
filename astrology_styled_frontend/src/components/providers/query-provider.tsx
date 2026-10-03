"use client";

import { createSyncStoragePersister } from "@tanstack/query-sync-storage-persister";
import { QueryClient, useIsRestoring } from "@tanstack/react-query";
import { PersistQueryClientProvider } from "@tanstack/react-query-persist-client";
import { useEffect, useState } from "react";

import { AccountRequestContext } from "@/lib/api/account-request";
import {
  bindChartResetClearing,
  reconcileChartState,
  shouldPersistQuery,
} from "@/lib/api/chart-persistence";
import { queryKeys } from "@/lib/api/queryKeys";
import { authClient } from "@/lib/auth-client";
import { isApiError } from "@/lib/http/errors";
import { safeStorage } from "@/lib/safe-storage";
import { useChartStore } from "@/store/chart-store";

/** The persisted cache's storage key. Only the cast chart ever lands here. */
const QUERY_CACHE_KEY = "tuvi.query-cache";

function createAccountScope() {
  let controller = new AbortController();
  return {
    getSignal: () => controller.signal,
    start: () => {
      if (controller.signal.aborted) controller = new AbortController();
    },
    stop: () => controller.abort(),
    persister: createSyncStoragePersister({
      key: QUERY_CACHE_KEY,
      throttleTime: 0,
      storage: {
        getItem: safeStorage.getItem,
        // Deferred callbacks from a previous account cannot overwrite the new cache.
        setItem: (key, value) => {
          if (!controller.signal.aborted) safeStorage.setItem(key, value);
        },
        removeItem: (key) => {
          if (!controller.signal.aborted) safeStorage.removeItem(key);
        },
      },
    }),
  };
}

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
  const { data: account, isPending } = authClient.useSession();
  if (isPending) return null;

  const accountId = account?.user.id ?? null;
  return (
    <AccountQueryProvider key={accountId ?? "guest"} accountId={accountId}>
      {children}
    </AccountQueryProvider>
  );
}

function AccountQueryProvider({
  accountId,
  children,
}: {
  accountId: string | null;
  children: React.ReactNode;
}) {
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
  const [scope] = useState(createAccountScope);

  useEffect(() => {
    scope.start();
    return () => {
      scope.stop();
      client.clear();
    };
  }, [client, scope]);

  useEffect(() => bindChartResetClearing(client), [client]);

  return (
    <PersistQueryClientProvider
      client={client}
      persistOptions={{
        persister: scope.persister,
        buster: `account:${accountId ?? "guest"}`,
        dehydrateOptions: { shouldDehydrateQuery: shouldPersistQuery },
      }}
      onSuccess={async () => {
        if (scope.getSignal().aborted) return;
        // Reconciliation needs both halves restored: the query cache (just
        // resolved) and the account-tagged chart store.
        await useChartStore.persist.rehydrate();
        if (scope.getSignal().aborted) return;
        useChartStore.getState().setAccount(accountId);
        reconcileChartState(client);
      }}
    >
      <AccountRequestContext.Provider value={{ getSignal: scope.getSignal, userId: accountId }}>
        <RestoredAccount accountId={accountId}>{children}</RestoredAccount>
      </AccountRequestContext.Provider>
    </PersistQueryClientProvider>
  );
}

function RestoredAccount({
  accountId,
  children,
}: {
  accountId: string | null;
  children: React.ReactNode;
}) {
  const isRestoring = useIsRestoring();
  const chartAccountId = useChartStore((state) => state.accountId);
  if (isRestoring || chartAccountId !== accountId) return null;
  return children;
}
