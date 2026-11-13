import { QueryClientProvider, type QueryClient } from "@tanstack/react-query";
import type { ReactNode } from "react";

import { AccountRequestContext } from "./account-request";
import type { ChartProfile } from "./schemas";

export const jsonResponse = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });

export const noBody = (status = 204) => new Response(null, { status });

export const PROFILE = {
  id: "p1",
  display_name: "Bạn thân · Minh",
  birth_info: { calendar: "solar", year: 1996, month: 4, day: 15, hour: 10, gender: "M" },
  created_at: "2026-08-28T00:00:00+00:00",
  updated_at: "2026-08-28T00:00:00+00:00",
} satisfies ChartProfile;

/** A query client and an account scope around a hook under test. */
export const wrapperWith = (client: QueryClient, userId?: string | null, signal?: AbortSignal) =>
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={client}>
        <AccountRequestContext.Provider value={{ getSignal: () => signal, userId }}>
          {children}
        </AccountRequestContext.Provider>
      </QueryClientProvider>
    );
  };
