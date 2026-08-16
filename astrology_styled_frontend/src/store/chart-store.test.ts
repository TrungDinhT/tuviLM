import { beforeEach, describe, expect, it } from "vitest";

import { useChartStore } from "./chart-store";
import { useToastStore } from "./toast-store";

describe("chart store", () => {
  beforeEach(() => {
    useChartStore.setState({ hasChart: false, outcome: null });
    useToastStore.setState({ message: null });
  });

  it("locks navigation until a chart is cast", () => {
    expect(useChartStore.getState().hasChart).toBe(false);

    useChartStore.getState().castChart({ stars: ["tuvi"] });

    expect(useChartStore.getState().hasChart).toBe(true);
    expect(useChartStore.getState().outcome).toEqual({ stars: ["tuvi"] });
  });

  it("clears the chart and the outcome on reset, so the accent reverts", () => {
    useChartStore.getState().castChart({ stars: ["vukhuc", "thamlang"] });
    useChartStore.getState().reset();

    const state = useChartStore.getState();
    expect(state.hasChart).toBe(false);
    // A null outcome is what makes ThemeProvider restore the :root defaults.
    expect(state.outcome).toBeNull();
  });

  it("dismisses any transient message on reset", () => {
    useChartStore.getState().castChart({ stars: ["tuvi"] });
    useToastStore.getState().show("Đã tạo ảnh story ✦");
    expect(useToastStore.getState().message).not.toBeNull();

    useChartStore.getState().reset();

    expect(useToastStore.getState().message).toBeNull();
  });
});
