import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { isApiError } from "@/lib/http/errors";

import { useChartProfiles, useDeleteChartProfile } from "./hooks";
import { OWNER_ID_KEY, resetOwnerIdCache } from "./owner";
import { emptyResponseSchema } from "./schemas";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function noBody(status = 204) {
  return new Response(null, { status });
}

const PROFILE = {
  id: "p1",
  display_name: "Bạn thân · Minh",
  birth_info: { calendar: "solar", year: 1996, month: 4, day: 15, hour: 10, gender: "M" },
  created_at: "2026-08-28T00:00:00+00:00",
  updated_at: "2026-08-28T00:00:00+00:00",
};

function wrapperWith(client: QueryClient) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  };
}

beforeEach(() => {
  localStorage.clear();
  resetOwnerIdCache();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("useChartProfiles", () => {
  it("parses the profile list from the backend", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ chart_profiles: [PROFILE] })));
    const client = new QueryClient();

    const { result } = renderHook(() => useChartProfiles(), {
      wrapper: wrapperWith(client),
    });

    await waitFor(() => expect(result.current.data).toEqual({ chart_profiles: [PROFILE] }));
  });
});

describe("useDeleteChartProfile", () => {
  it("invalidates the list so it refetches after a delete", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (init?.method === "DELETE") return Promise.resolve(noBody(204));
      return Promise.resolve(jsonResponse({ chart_profiles: [PROFILE] }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();

    const { result: list } = renderHook(() => useChartProfiles(), {
      wrapper: wrapperWith(client),
    });
    const { result: del } = renderHook(() => useDeleteChartProfile(), {
      wrapper: wrapperWith(client),
    });

    await waitFor(() => expect(list.current.data).toBeDefined());
    const listFetches = () =>
      fetchMock.mock.calls.filter(
        ([url, init]) =>
          String(url).endsWith("/api/v1/chart-profiles") && init?.method !== "DELETE",
      ).length;
    const before = listFetches();

    await act(async () => {
      await del.current.mutateAsync("p1");
    });

    await waitFor(() => expect(listFetches()).toBeGreaterThan(before));
  });

  it("reports a non-empty delete body as a parse error", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ ok: true }, 200)));
    const client = new QueryClient();

    const { result } = renderHook(() => useDeleteChartProfile(), {
      wrapper: wrapperWith(client),
    });

    let caught: unknown;
    await act(async () => {
      try {
        await result.current.mutateAsync("p1");
      } catch (error) {
        caught = error;
      }
    });

    expect(isApiError(caught)).toBe(true);
    if (isApiError(caught)) {
      expect(caught.error.kind).toBe("parse");
    }
  });
});

describe("emptyResponseSchema", () => {
  it("accepts a null body and rejects any non-null body", () => {
    expect(emptyResponseSchema.safeParse(null).success).toBe(true);
    expect(emptyResponseSchema.safeParse(undefined).success).toBe(false);
    expect(emptyResponseSchema.safeParse({}).success).toBe(false);
    expect(emptyResponseSchema.safeParse("ok").success).toBe(false);
  });
});
