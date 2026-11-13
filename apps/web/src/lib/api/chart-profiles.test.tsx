import { QueryClient, useIsMutating, useMutation } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useChartStore } from "@/store/chart-store";

import { useAccountRequestScope } from "./account-request";
import { openChartProfileMutationOptions } from "./chart-profiles";
import { mutationKeys, queryKeys } from "./queryKeys";
import { buildLasoResponseSchema } from "./schemas";
import { PROFILE, jsonResponse, wrapperWith } from "./test-utils";
import buildLasoFixture from "./__fixtures__/build-laso.json";

const useOpenChartProfile = () =>
  useMutation(openChartProfileMutationOptions(useAccountRequestScope()));

beforeEach(() => {
  localStorage.clear();
  useChartStore.getState().reset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("openChartProfileMutationOptions", () => {
  const chart = buildLasoResponseSchema.parse(buildLasoFixture);

  it("rebuilds the chart and freshly loads only the newest conversation", async () => {
    const sessions = [
      { id: "s1", updated_at: "2026-01-01T00:00:00Z" },
      { id: "s2", updated_at: "2026-02-01T00:00:00Z" },
    ].map(({ id, updated_at }) => ({
      id,
      chart_profile_id: PROFILE.id,
      title: null,
      message_count: 1,
      created_at: PROFILE.created_at,
      updated_at,
    }));
    const transcripts = sessions.map((session) => ({
      session: {
        ...session,
        messages: [
          {
            id: `message-${session.id}`,
            role: "user",
            content: session.id,
            status: "confirmed",
            created_at: session.created_at,
            updated_at: session.updated_at,
          },
        ],
      },
    }));
    const fetchMock = vi.fn((url: string) =>
      Promise.resolve(
        jsonResponse(
          url.endsWith("/laso/build")
            ? chart
            : url.endsWith("/p1/sessions")
              ? { sessions }
              : transcripts.find(({ session }) => url.endsWith(`/${session.id}`)),
        ),
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    client.setQueryData(queryKeys.sessions.byProfile(PROFILE.id), { sessions: [] });
    const { result } = renderHook(() => useOpenChartProfile(), {
      wrapper: wrapperWith(client, "user-1"),
    });

    await act(async () => {
      await result.current.mutateAsync(PROFILE);
    });

    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/laso/build"),
      expect.objectContaining({ method: "POST", body: JSON.stringify(PROFILE.birth_info) }),
    );
    expect(client.getQueryData(queryKeys.laso.chart(chart.id))).toEqual(chart);
    expect(client.getQueryData(queryKeys.sessions.byProfile(PROFILE.id))).toEqual({ sessions });
    expect(client.getQueryData(queryKeys.sessions.detail("s2"))).toMatchObject({
      session: { id: "s2", messages: transcripts[1]!.session.messages },
    });
    expect(client.getQueryData(queryKeys.sessions.detail("s1"))).toBeUndefined();
    expect(useChartStore.getState()).toMatchObject({
      hasChart: true,
      chartId: chart.id,
      chartProfileId: PROFILE.id,
      birthInfo: PROFILE.birth_info,
    });
  });

  it("activates the chart even when the caller unmounts before the request ends", async () => {
    let finishBuild: ((response: Response) => void) | null = null;
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) =>
        url.endsWith("/laso/build")
          ? new Promise<Response>((resolve) => {
              finishBuild = resolve;
            })
          : Promise.resolve(jsonResponse({ sessions: [] })),
      ),
    );
    const client = new QueryClient();
    const onSuccess = vi.fn();
    const { result, unmount } = renderHook(() => useOpenChartProfile(), {
      wrapper: wrapperWith(client, "user-1"),
    });

    act(() => result.current.mutate(PROFILE, { onSuccess }));
    await waitFor(() => expect(finishBuild).not.toBeNull());
    unmount();
    finishBuild!(jsonResponse(chart));

    await waitFor(() => expect(useChartStore.getState().chartId).toBe(chart.id));
    expect(useChartStore.getState().chartProfileId).toBe(PROFILE.id);
    // The caller's own callback is UI work, and its UI is gone.
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("lets a second unit see that a chart is being opened", async () => {
    let finishBuild: (response: Response) => void = () => {};
    vi.stubGlobal(
      "fetch",
      vi.fn((url: string) =>
        url.endsWith("/laso/build")
          ? new Promise<Response>((resolve) => {
              finishBuild = resolve;
            })
          : Promise.resolve(jsonResponse({ sessions: [] })),
      ),
    );
    const client = new QueryClient();
    const wrapper = wrapperWith(client, "user-1");
    const { result: opener } = renderHook(() => useOpenChartProfile(), { wrapper });
    const { result: watcher } = renderHook(
      () => useIsMutating({ mutationKey: mutationKeys.openChartProfile() }) > 0,
      { wrapper },
    );
    expect(watcher.current).toBe(false);

    act(() => opener.current.mutate(PROFILE));
    await waitFor(() => expect(watcher.current).toBe(true));
    finishBuild(jsonResponse(chart));
    await waitFor(() => expect(watcher.current).toBe(false));
  });

  it("opens a chart without creating a conversation when its history is empty", async () => {
    const fetchMock = vi.fn((url: string) =>
      Promise.resolve(jsonResponse(url.endsWith("/laso/build") ? chart : { sessions: [] })),
    );
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    const { result } = renderHook(() => useOpenChartProfile(), {
      wrapper: wrapperWith(client, "user-1"),
    });

    await act(async () => {
      await result.current.mutateAsync(PROFILE);
    });

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(client.getQueryData(queryKeys.sessions.byProfile(PROFILE.id))).toEqual({ sessions: [] });
  });

  it("keeps existing data and skips activation when history fails or the account leaves", async () => {
    const session = {
      id: "s1",
      chart_profile_id: PROFILE.id,
      title: null,
      messages: [],
      created_at: PROFILE.created_at,
      updated_at: PROFILE.updated_at,
    };
    for (const cancelled of [false, true]) {
      const controller = new AbortController();
      vi.stubGlobal(
        "fetch",
        vi.fn((url: string) => {
          if (url.endsWith("/laso/build")) return Promise.resolve(jsonResponse(chart));
          if (url.endsWith("/p1/sessions")) {
            return Promise.resolve(jsonResponse({ sessions: [{ ...session, message_count: 0 }] }));
          }
          if (cancelled) controller.abort();
          return Promise.resolve(
            jsonResponse(
              cancelled ? { session } : { detail: "Unavailable" },
              cancelled ? 200 : 503,
            ),
          );
        }),
      );
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
      expect(useChartStore.getState().hasChart).toBe(false);
      unmount();
    }
  });
});
