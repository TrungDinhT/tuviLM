import { QueryClient, dehydrate, useQueryClient } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { useState } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useAccountRequestScope } from "@/lib/api/account-request";
import fixture from "@/lib/api/__fixtures__/build-laso.json";
import { shouldPersistQuery } from "@/lib/api/chart-persistence";
import { useChartProfiles } from "@/lib/api/hooks";
import { queryKeys } from "@/lib/api/queryKeys";
import { safeStorage } from "@/lib/safe-storage";
import { useChartStore } from "@/store/chart-store";

import { QueryProvider } from "./query-provider";

const account = vi.hoisted(() => ({
  data: { user: { id: "account-a" } } as { user: { id: string } } | null,
  isPending: false,
}));

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    useSession: () => account,
    token: vi
      .fn()
      .mockResolvedValue({
        data: { token: "header.eyJzdWIiOiJhY2NvdW50LWEifQ.signature" },
        error: null,
      }),
  },
}));

const clients: QueryClient[] = [];
const signals: AbortSignal[] = [];
const visibleAccounts: (string | null)[] = [];

function Probe({ fetchProfiles = false }: { fetchProfiles?: boolean }) {
  const client = useQueryClient();
  const { getSignal } = useAccountRequestScope();
  const accountId = useChartStore((state) => state.accountId);
  const chartId = useChartStore((state) => state.chartId);
  const [draft, setDraft] = useState("");
  useChartProfiles(fetchProfiles);
  visibleAccounts.push(accountId);
  if (!clients.includes(client)) clients.push(client);
  return (
    <div>
      <span>
        {accountId ?? "guest"}:{chartId ?? "empty"}
      </span>
      <input aria-label="Draft" value={draft} onChange={(event) => setDraft(event.target.value)} />
      <button onClick={() => signals.push(getSignal()!)}>Capture signal</button>
    </div>
  );
}

function persistChart(accountId: string | null) {
  useChartStore.getState().setAccount(accountId);
  useChartStore.getState().castChart({ stars: ["tuvi"] }, fixture.id, null, "profile-a");
  const client = new QueryClient();
  client.setQueryData(queryKeys.laso.chart(fixture.id), fixture);
  safeStorage.setItem(
    "tuvi.query-cache",
    JSON.stringify({
      timestamp: Date.now(),
      buster: `account:${accountId ?? "guest"}`,
      clientState: dehydrate(client, { shouldDehydrateQuery: shouldPersistQuery }),
    }),
  );
  client.clear();
}

beforeEach(() => {
  localStorage.clear();
  useChartStore.getState().reset();
  useChartStore.getState().setAccount(null);
  account.data = { user: { id: "account-a" } };
  account.isPending = false;
  clients.length = 0;
  signals.length = 0;
  visibleAccounts.length = 0;
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("QueryProvider account isolation", () => {
  it("restores a chart only after checking its account", async () => {
    persistChart("account-a");
    account.isPending = true;
    const view = render(
      <QueryProvider>
        <Probe />
      </QueryProvider>,
    );
    expect(screen.queryByLabelText("Draft")).toBeNull();
    expect(visibleAccounts).toEqual([]);

    account.isPending = false;
    view.rerender(
      <QueryProvider>
        <Probe />
      </QueryProvider>,
    );
    await screen.findByText(`account-a:${fixture.id}`);
    expect(useChartStore.getState().chartProfileId).toBe("profile-a");
    expect(clients[0]?.getQueryData(queryKeys.laso.chart(fixture.id))).toEqual(fixture);
    expect(visibleAccounts.every((id) => id === "account-a")).toBe(true);
  });

  it("does not expose a persisted chart to a different account", async () => {
    persistChart("account-a");
    account.data = { user: { id: "account-b" } };
    render(
      <QueryProvider>
        <Probe />
      </QueryProvider>,
    );

    await screen.findByText("account-b:empty");
    expect(useChartStore.getState().chartProfileId).toBeNull();
    expect(clients[0]?.getQueryData(queryKeys.laso.chart(fixture.id))).toBeUndefined();
    expect(visibleAccounts.every((owner) => owner === "account-b")).toBe(true);
  });

  it("remounts local state and aborts old queries and mutations on account changes", async () => {
    let querySignal: AbortSignal | undefined;
    vi.stubGlobal(
      "fetch",
      vi.fn((_url: string, init: RequestInit) => {
        querySignal = init.signal as AbortSignal;
        return new Promise<Response>(() => {});
      }),
    );
    const view = render(
      <QueryProvider>
        <Probe fetchProfiles />
      </QueryProvider>,
    );
    await screen.findByText("account-a:empty");
    await waitFor(() => expect(querySignal).toBeDefined());
    fireEvent.change(screen.getByLabelText("Draft"), { target: { value: "Account A draft" } });
    fireEvent.click(screen.getByText("Capture signal"));
    clients[0]!.setQueryData(queryKeys.sessions.detail("session-a"), { private: "A" });

    account.data = { user: { id: "account-b" } };
    view.rerender(
      <QueryProvider>
        <Probe />
      </QueryProvider>,
    );
    await screen.findByText("account-b:empty");

    expect((screen.getByLabelText("Draft") as HTMLInputElement).value).toBe("");
    expect(querySignal?.aborted).toBe(true);
    expect(signals[0]?.aborted).toBe(true);
    expect(clients[0]!.getQueryCache().getAll()).toEqual([]);
    expect(clients[1]).not.toBe(clients[0]);
    expect(clients[1]!.getQueryData(queryKeys.sessions.detail("session-a"))).toBeUndefined();
  });
});
