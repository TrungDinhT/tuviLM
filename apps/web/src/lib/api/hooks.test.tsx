import { QueryClient } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { isApiError } from "@/lib/http/errors";
import { useChartStore } from "@/store/chart-store";

import {
  useAccountAccess,
  useChartProfiles,
  useDeleteChartProfile,
  useRenameChartProfile,
} from "./hooks";
import { queryKeys } from "./queryKeys";
import { accountAccessSchema, emptyResponseSchema } from "./schemas";
import { PROFILE, jsonResponse, noBody, wrapperWith } from "./test-utils";

beforeEach(() => {
  localStorage.clear();
  useChartStore.getState().reset();
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
      "/api/v1/me",
      expect.objectContaining({ method: "GET", headers: { "X-Expected-User-Id": "user-1" } }),
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
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ display_name: "Gia đình" }),
      }),
    );
    await waitFor(() =>
      expect(list.current.data?.chart_profiles[0]?.display_name).toBe("Gia đình"),
    );
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
