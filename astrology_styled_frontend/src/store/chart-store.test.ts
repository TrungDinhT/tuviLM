import { beforeEach, describe, expect, it } from "vitest";

import { CHART_STORAGE_KEY, useChartStore } from "./chart-store";
import { useToastStore } from "./toast-store";

describe("chart store", () => {
  beforeEach(() => {
    localStorage.clear();
    useChartStore.setState({ hasChart: false, outcome: null, previewOutcome: null, chartId: null });
    useToastStore.setState({ message: null });
  });

  it("locks navigation until a chart is cast", () => {
    expect(useChartStore.getState().hasChart).toBe(false);

    useChartStore.getState().castChart({ stars: ["tuvi"] }, "1996041510M");

    const state = useChartStore.getState();
    expect(state.hasChart).toBe(true);
    expect(state.outcome).toEqual({ stars: ["tuvi"] });
    expect(state.chartId).toBe("1996041510M");
  });

  it("clears the chart and the outcome on reset, so the accent reverts", () => {
    useChartStore.getState().castChart({ stars: ["vukhuc", "thamlang"] }, "1996041510M");
    useChartStore.getState().reset();

    const state = useChartStore.getState();
    expect(state.hasChart).toBe(false);
    // A null outcome is what makes ThemeProvider restore the :root defaults.
    expect(state.outcome).toBeNull();
    expect(state.chartId).toBeNull();
  });

  it("dismisses any transient message on reset", () => {
    useChartStore.getState().castChart({ stars: ["tuvi"] }, "1996041510M");
    useToastStore.getState().show("Đã tạo ảnh story ✦");
    expect(useToastStore.getState().message).not.toBeNull();

    useChartStore.getState().reset();

    expect(useToastStore.getState().message).toBeNull();
  });

  it("replaces the preview outcome when a chart is cast", () => {
    useChartStore.getState().setPreviewOutcome({ stars: ["thaiduong"] });
    expect(useChartStore.getState().previewOutcome).toEqual({ stars: ["thaiduong"] });

    useChartStore.getState().castChart({ stars: ["tuvi"] }, "1996041510M");

    const state = useChartStore.getState();
    expect(state.outcome).toEqual({ stars: ["tuvi"] });
    expect(state.previewOutcome).toBeNull();
  });

  it("clears the preview outcome on reset", () => {
    useChartStore.getState().setPreviewOutcome({ stars: ["thaiduong"] });

    useChartStore.getState().reset();

    expect(useChartStore.getState().previewOutcome).toBeNull();
  });

  it("does not persist the preview outcome", () => {
    useChartStore.getState().setPreviewOutcome({ stars: ["thaiduong"] });

    const raw = localStorage.getItem(CHART_STORAGE_KEY);
    expect(raw).not.toBeNull();
    expect(JSON.parse(raw!)).toMatchObject({ state: { hasChart: false, outcome: null } });
    expect(JSON.parse(raw!).state).not.toHaveProperty("previewOutcome");
  });
});
