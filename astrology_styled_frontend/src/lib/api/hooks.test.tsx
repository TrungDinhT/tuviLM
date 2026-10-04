import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { isApiError } from "@/lib/http/errors";

import { AccountRequestContext } from "./account-request";
import {
  useAccountAccess,
  useChartProfiles,
  useDeleteChartProfile,
  useOpenChartProfile,
  useRenameChartProfile,
} from "./hooks";
import { queryKeys } from "./queryKeys";
import { accountAccessSchema, buildLasoResponseSchema, emptyResponseSchema, type ChartProfile } from "./schemas";
import buildLasoFixture from "./__fixtures__/build-laso.json";

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    token: vi.fn().mockResolvedValue({
      data: { token: "header.eyJzdWIiOiJ1c2VyLTEifQ.signature" },
      error: null,
    }),
  },
}));

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
} satisfies ChartProfile;

function wrapperWith(client: QueryClient, userId?: string | null, signal?: AbortSignal) {
  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={client}>
        <AccountRequestContext.Provider value={{ getSignal: () => signal, userId }}>
          {children}
        </AccountRequestContext.Provider>
      </QueryClientProvider>
    );
  };
}

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("useAccountAccess", () => {
  it("fetches the signed-in account's current plan and balance", async () => {
    const access = { user_id: "user-1", role: "user", plan: "normal", balance: 6 };
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(access));
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    const { result } = renderHook(() => useAccountAccess(), {
      wrapper: wrapperWith(client, "user-1"),
    });

    await waitFor(() => expect(result.current.data).toEqual(access));
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/me"),
      expect.objectContaining({
        headers: { Authorization: "Bearer header.eyJzdWIiOiJ1c2VyLTEifQ.signature" },
      }),
    );
    expect(client.getQueryData(queryKeys.accountAccess("user-1"))).toEqual(access);
  });

  it("does not request account access for guests or unresolved accounts", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    renderHook(() => useAccountAccess(), { wrapper: wrapperWith(client, null) });
    renderHook(() => useAccountAccess(), { wrapper: wrapperWith(client) });
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("rejects invalid account data instead of caching an invented balance", async () => {
    const access = { user_id: "user-1", role: "user", plan: "normal", balance: -3 };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(access)));
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const { result } = renderHook(() => useAccountAccess(), {
      wrapper: wrapperWith(client, "user-1"),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.data).toBeUndefined();
    expect(isApiError(result.current.error) && result.current.error.error.kind).toBe("parse");
    expect(accountAccessSchema.safeParse({ ...access, plan: "vip", balance: 0 }).success).toBe(
      false,
    );
  });
});

describe("useChartProfiles", () => {
  it("parses the profile list from the backend", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({ chart_profiles: [PROFILE] })));
    const client = new QueryClient();

    const { result } = renderHook(() => useChartProfiles(), {
      wrapper: wrapperWith(client),
    });

    await waitFor(() => expect(result.current.data).toEqual({ chart_profiles: [PROFILE] }));
  });
});

describe("useOpenChartProfile", () => {
  const chart = buildLasoResponseSchema.parse(buildLasoFixture);

  it("rebuilds the chart and freshly loads every conversation into its cache", async () => {
    const sessions = ["s1", "s2"].map((id) => ({
      id, chart_profile_id: PROFILE.id, title: null, message_count: 1,
      created_at: PROFILE.created_at, updated_at: PROFILE.updated_at,
    }));
    const transcripts = sessions.map((session) => ({ session: { ...session, messages: [{
      id: `message-${session.id}`, role: "user", content: session.id, status: "confirmed",
      created_at: session.created_at, updated_at: session.updated_at,
    }] } }));
    const fetchMock = vi.fn((url: string) => Promise.resolve(jsonResponse(
      url.endsWith("/laso/build") ? chart : url.endsWith("/p1/sessions") ? { sessions }
        : transcripts.find(({ session }) => url.endsWith(`/${session.id}`)),
    )));
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    client.setQueryData(queryKeys.sessions.byProfile(PROFILE.id), { sessions: [] });
    const { result } = renderHook(() => useOpenChartProfile(), { wrapper: wrapperWith(client, "user-1") });

    await act(async () => { await result.current.mutateAsync(PROFILE); });

    expect(fetchMock).toHaveBeenCalledTimes(4);
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/laso/build"),
      expect.objectContaining({ method: "POST", body: JSON.stringify(PROFILE.birth_info) }));
    expect(client.getQueryData(queryKeys.laso.chart(chart.id))).toEqual(chart);
    expect(client.getQueryData(queryKeys.sessions.byProfile(PROFILE.id))).toEqual({ sessions });
    for (const { session } of transcripts) {
      expect(client.getQueryData(queryKeys.sessions.detail(session.id))).toMatchObject({
        session: { id: session.id, messages: session.messages },
      });
    }
  });

  it("opens a chart without creating a conversation when its history is empty", async () => {
    const fetchMock = vi.fn((url: string) => Promise.resolve(jsonResponse(
      url.endsWith("/laso/build") ? chart : { sessions: [] },
    )));
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    const { result } = renderHook(() => useOpenChartProfile(), { wrapper: wrapperWith(client, "user-1") });

    await act(async () => { await result.current.mutateAsync(PROFILE); });

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(client.getQueryData(queryKeys.sessions.byProfile(PROFILE.id))).toEqual({ sessions: [] });
  });

  it("keeps existing data and skips activation when history fails or the account leaves", async () => {
    const session = {
      id: "s1", chart_profile_id: PROFILE.id, title: null, messages: [],
      created_at: PROFILE.created_at, updated_at: PROFILE.updated_at,
    };
    for (const cancelled of [false, true]) {
      const controller = new AbortController();
      vi.stubGlobal("fetch", vi.fn((url: string) => {
        if (url.endsWith("/laso/build")) return Promise.resolve(jsonResponse(chart));
        if (url.endsWith("/p1/sessions")) {
          return Promise.resolve(jsonResponse({ sessions: [{ ...session, message_count: 0 }] }));
        }
        if (cancelled) controller.abort();
        return Promise.resolve(jsonResponse(
          cancelled ? { session } : { detail: "Unavailable" }, cancelled ? 200 : 503,
        ));
      }));
      const client = new QueryClient();
      client.setQueryData(queryKeys.laso.chart(chart.id), { previous: true });
      const onSuccess = vi.fn();
      const { result, unmount } = renderHook(() => useOpenChartProfile(), {
        wrapper: wrapperWith(client, "user-1", controller.signal),
      });

      await act(async () => {
        await expect(result.current.mutateAsync(PROFILE, { onSuccess })).rejects.toThrow();
      });

      expect(client.getQueryData(queryKeys.laso.chart(chart.id))).toEqual({ previous: true });
      expect(client.getQueryData(queryKeys.sessions.byProfile(PROFILE.id))).toBeUndefined();
      expect(client.getQueryData(queryKeys.sessions.detail(session.id))).toBeUndefined();
      expect(onSuccess).not.toHaveBeenCalled();
      unmount();
    }
  });
});

describe("useRenameChartProfile", () => {
  it("patches the trimmed name and refetches the active saved-chart list", async () => {
    let profile = PROFILE;
    const fetchMock = vi.fn((_: string, init?: RequestInit) => {
      if (init?.method === "PATCH") {
        profile = { ...PROFILE, display_name: "Gia đình" };
        return Promise.resolve(jsonResponse({ chart_profile: profile }));
      }
      return Promise.resolve(jsonResponse({ chart_profiles: [profile] }));
    });
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    const { result: list } = renderHook(() => useChartProfiles(), {
      wrapper: wrapperWith(client, "user-1"),
    });
    const { result: rename } = renderHook(() => useRenameChartProfile(), {
      wrapper: wrapperWith(client, "user-1"),
    });
    await waitFor(() => expect(list.current.data?.chart_profiles[0]).toEqual(PROFILE));
    await act(async () => {
      await rename.current.mutateAsync({ id: PROFILE.id, display_name: "  Gia đình  " });
    });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/chart-profiles/p1"),
      expect.objectContaining({ method: "PATCH", body: JSON.stringify({ display_name: "Gia đình" }) }),
    );
    await waitFor(() => expect(list.current.data?.chart_profiles[0]?.display_name).toBe("Gia đình"));
  });
});

describe("useDeleteChartProfile", () => {
  it("invalidates the list so it refetches after a delete", async () => {
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
