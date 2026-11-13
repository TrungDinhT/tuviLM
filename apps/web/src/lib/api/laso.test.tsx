import { QueryClient, useMutation } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useChartStore } from "@/store/chart-store";

import { useAccountRequestScope } from "./account-request";
import { useChartProfiles } from "./hooks";
import { castChartMutationOptions } from "./laso";
import { queryKeys } from "./queryKeys";
import { buildLasoResponseSchema } from "./schemas";
import { PROFILE, jsonResponse, wrapperWith } from "./test-utils";
import buildLasoFixture from "./__fixtures__/build-laso.json";

const useCastChart = (minDurationMs?: number) =>
  useMutation(castChartMutationOptions({ ...useAccountRequestScope(), minDurationMs }));

beforeEach(() => {
  localStorage.clear();
  useChartStore.getState().reset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("castChartMutationOptions", () => {
  const chart = buildLasoResponseSchema.parse(buildLasoFixture);
  const birth = PROFILE.birth_info;
  const saved = { chart_profile: PROFILE };
  const isBuild = (url: string) => url.endsWith("/laso/build");

  it("builds, saves and activates the chart for a signed-in account", async () => {
    const fetchMock = vi.fn((url: string, init?: RequestInit) =>
      Promise.resolve(
        jsonResponse(
          isBuild(url) ? chart : init?.method === "POST" ? saved : { chart_profiles: [PROFILE] },
        ),
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    const wrapper = wrapperWith(client, "user-1");
    const { result: list } = renderHook(() => useChartProfiles(), { wrapper });
    await waitFor(() => expect(list.current.data).toBeDefined());
    const { result } = renderHook(() => useCastChart(), { wrapper });

    await act(async () => {
      await result.current.mutateAsync(birth);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/v1/chart-profiles",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ display_name: "15/04/1996", birth_info: birth }),
        headers: expect.objectContaining({ "Idempotency-Key": "profile:1996-4-15-10-M" }),
      }),
    );
    expect(client.getQueryData(queryKeys.laso.chart(chart.id))).toEqual(chart);
    expect(useChartStore.getState()).toMatchObject({
      hasChart: true,
      chartId: chart.id,
      chartProfileId: PROFILE.id,
      birthInfo: birth,
    });
    // The saved-chart list refetches, so the new profile shows up in Hồ sơ.
    const listFetches = () =>
      fetchMock.mock.calls.filter(([url, init]) => !isBuild(url) && init?.method !== "POST").length;
    await waitFor(() => expect(listFetches()).toBe(2));
  });

  it("casts for a guest without saving a profile", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(chart));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useCastChart(), {
      wrapper: wrapperWith(new QueryClient(), null),
    });

    await act(async () => {
      await result.current.mutateAsync(birth);
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(useChartStore.getState()).toMatchObject({ chartId: chart.id, chartProfileId: null });
  });

  it("still casts when the auto-save fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) =>
        Promise.resolve(isBuild(url) ? jsonResponse(chart) : jsonResponse({ detail: "down" }, 503)),
      ),
    );
    const { result } = renderHook(() => useCastChart(), {
      wrapper: wrapperWith(new QueryClient(), "user-1"),
    });

    await act(async () => {
      await result.current.mutateAsync(birth);
    });

    expect(useChartStore.getState()).toMatchObject({ chartId: chart.id, chartProfileId: null });
  });

  it("does not activate the chart before the minimum duration has passed", async () => {
    vi.useFakeTimers();
    try {
      vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(chart)));
      const { result } = renderHook(() => useCastChart(2600), {
        wrapper: wrapperWith(new QueryClient(), null),
      });

      act(() => result.current.mutate(birth));
      await act(async () => vi.advanceTimersByTimeAsync(2599));
      expect(useChartStore.getState().hasChart).toBe(false);
      await act(async () => vi.advanceTimersByTimeAsync(1));
      expect(useChartStore.getState().chartId).toBe(chart.id);
    } finally {
      vi.useRealTimers();
    }
  });

  it("neither saves nor activates when the account leaves during the build", async () => {
    const controller = new AbortController();
    const fetchMock = vi.fn(() => {
      controller.abort();
      return Promise.resolve(jsonResponse(chart));
    });
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    const { result } = renderHook(() => useCastChart(), {
      wrapper: wrapperWith(client, "user-1", controller.signal),
    });

    await act(async () => {
      await expect(result.current.mutateAsync(birth)).rejects.toThrow();
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(client.getQueryData(queryKeys.laso.chart(chart.id))).toBeUndefined();
    expect(useChartStore.getState().hasChart).toBe(false);
  });

  it("does not activate when the account leaves during the auto-save", async () => {
    const controller = new AbortController();
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) => {
        if (isBuild(url)) return Promise.resolve(jsonResponse(chart));
        controller.abort();
        return Promise.resolve(jsonResponse(saved));
      }),
    );
    const client = new QueryClient();
    const { result } = renderHook(() => useCastChart(), {
      wrapper: wrapperWith(client, "user-1", controller.signal),
    });

    await act(async () => {
      await expect(result.current.mutateAsync(birth)).rejects.toThrow();
    });

    expect(client.getQueryData(queryKeys.laso.chart(chart.id))).toBeUndefined();
    expect(useChartStore.getState()).toMatchObject({ hasChart: false, chartProfileId: null });
  });
});
