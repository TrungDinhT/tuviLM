import { QueryClient, dehydrate, hydrate } from "@tanstack/react-query";
import { beforeEach, describe, expect, it } from "vitest";

import { useChartStore } from "@/store/chart-store";

import {
  bindChartResetClearing,
  reconcileChartState,
  shouldPersistQuery,
} from "./chart-persistence";
import { queryKeys } from "./queryKeys";

const CHART_ID = "1996041510M";

function seedChart(client: QueryClient, payload: unknown = { id: CHART_ID }) {
  client.setQueryData(queryKeys.laso.chart(CHART_ID), payload);
}

beforeEach(() => {
  useChartStore.setState({ hasChart: false, outcome: null, previewOutcome: null, chartId: null });
});

describe("shouldPersistQuery", () => {
  it("whitelists only the chart key family", () => {
    const client = new QueryClient();
    seedChart(client);
    client.setQueryData(queryKeys.laso.preview(null), { chinh_tinh: [] });
    client.setQueryData(queryKeys.health(), { status: "ok" });

    const dehydrated = dehydrate(client, { shouldDehydrateQuery: shouldPersistQuery });

    expect(dehydrated.queries).toHaveLength(1);
    expect(dehydrated.queries[0]?.queryKey).toEqual(queryKeys.laso.chart(CHART_ID));
  });
});

describe("persist round-trip", () => {
  it("restores the chart into a fresh client without a network call", () => {
    const writer = new QueryClient();
    seedChart(writer, { id: CHART_ID, summary: "Sinh dương lịch: 15/04/1996 10:00" });

    const snapshot = dehydrate(writer, { shouldDehydrateQuery: shouldPersistQuery });

    const reader = new QueryClient();
    hydrate(reader, snapshot);

    expect(reader.getQueryData(queryKeys.laso.chart(CHART_ID))).toEqual({
      id: CHART_ID,
      summary: "Sinh dương lịch: 15/04/1996 10:00",
    });
  });
});

describe("reconcileChartState", () => {
  it("resets when the store claims a chart the cache does not have", () => {
    const client = new QueryClient();
    useChartStore.setState({ hasChart: true, outcome: { stars: ["tuvi"] }, chartId: CHART_ID });

    reconcileChartState(client);

    expect(useChartStore.getState().hasChart).toBe(false);
    expect(useChartStore.getState().chartId).toBeNull();
  });

  it("leaves the store alone when the chart is cached", () => {
    const client = new QueryClient();
    seedChart(client);
    useChartStore.setState({ hasChart: true, outcome: { stars: ["tuvi"] }, chartId: CHART_ID });

    reconcileChartState(client);

    expect(useChartStore.getState().hasChart).toBe(true);
  });

  it("does nothing when no chart was cast", () => {
    const client = new QueryClient();

    reconcileChartState(client);

    expect(useChartStore.getState().hasChart).toBe(false);
  });
});

describe("bindChartResetClearing", () => {
  it("removes the persisted chart when the chart state resets", () => {
    const client = new QueryClient();
    seedChart(client);
    useChartStore.getState().castChart({ stars: ["tuvi"] }, CHART_ID);

    const unbind = bindChartResetClearing(client);
    useChartStore.getState().reset();
    unbind();

    expect(client.getQueryData(queryKeys.laso.chart(CHART_ID))).toBeUndefined();
  });

  it("keeps the chart across unrelated store updates", () => {
    const client = new QueryClient();
    seedChart(client);
    useChartStore.getState().castChart({ stars: ["tuvi"] }, CHART_ID);

    const unbind = bindChartResetClearing(client);
    useChartStore.getState().setPreviewOutcome({ stars: ["thaiduong"] });
    unbind();

    expect(client.getQueryData(queryKeys.laso.chart(CHART_ID))).toBeDefined();
  });
});
