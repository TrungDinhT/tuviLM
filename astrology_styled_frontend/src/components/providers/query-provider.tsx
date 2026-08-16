"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

import { isApiError } from "@/lib/http/errors";

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
 */
export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
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
      }),
  );

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
