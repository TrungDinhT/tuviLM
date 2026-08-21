import { render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useChartStore } from "@/store/chart-store";

import { AccentTheme } from "./accent-theme";

let mockPathname = "/ban-menh";

vi.mock("next/navigation", () => ({
  usePathname: () => mockPathname,
}));

function accent(): string {
  return document.documentElement.style.getPropertyValue("--accent");
}

beforeEach(() => {
  mockPathname = "/ban-menh";
});

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

  // On the casting screen a cached chart must not tint the dials: the accent
  // there belongs to the chart being entered, not the one being replaced.
  it("ignores the persisted cast chart on An sao", () => {
    mockPathname = "/";
    useChartStore.setState({ outcome: { stars: ["thienco"] }, previewOutcome: null });

    render(<AccentTheme>x</AccentTheme>);

    expect(accent()).toBe("");
  });

  it("still follows the live preview on An sao", () => {
    mockPathname = "/";
    useChartStore.setState({
      outcome: { stars: ["thienco"] },
      previewOutcome: { stars: ["thaiduong"] },
    });

    render(<AccentTheme>x</AccentTheme>);

    expect(accent()).toBe("var(--element-hoa)");
  });
});
