import { render } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { useChartStore } from "@/store/chart-store";

import { AccentTheme } from "./accent-theme";

function accent(): string {
  return document.documentElement.style.getPropertyValue("--accent");
}

afterEach(() => {
  useChartStore.setState({ hasChart: false, outcome: null, previewOutcome: null, chartId: null });
  document.documentElement.style.removeProperty("--accent");
});

describe("AccentTheme", () => {
  it("uses the cast chart when nothing is being previewed", () => {
    useChartStore.setState({ outcome: { stars: ["thienco"] }, previewOutcome: null });

    render(<AccentTheme>x</AccentTheme>);

    expect(accent()).toBe("var(--element-moc)");
  });

  // The regression: after a cast, returning to An sao left the accent frozen
  // on the previous chart while the dials moved.
  it("lets a live preview outrank the cast chart", () => {
    useChartStore.setState({
      outcome: { stars: ["thienco"] },
      previewOutcome: { stars: ["thaiduong"] },
    });

    render(<AccentTheme>x</AccentTheme>);

    expect(accent()).toBe("var(--element-hoa)");
  });

  it("clears the properties when there is neither", () => {
    render(<AccentTheme>x</AccentTheme>);

    expect(accent()).toBe("");
  });
});
