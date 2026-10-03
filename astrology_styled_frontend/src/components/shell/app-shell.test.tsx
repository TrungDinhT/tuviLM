import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { useChartStore } from "@/store/chart-store";

import { AppShell } from "./app-shell";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

vi.mock("./app-nav", () => ({
  AppNav: () => <nav data-testid="app-nav" />,
}));

vi.mock("./top-bar", () => ({
  TopBar: () => <header data-testid="top-bar" />,
}));

afterEach(() => {
  useChartStore.setState({ hasChart: false, outcome: null, previewOutcome: null, chartId: null });
});

describe("AppShell navigation", () => {
  it("hides navigation and rail spacing before a chart exists", () => {
    const { container } = render(<AppShell>content</AppShell>);

    expect(screen.queryByTestId("app-nav")).toBeNull();
    expect(container.firstElementChild?.className).not.toContain("lg:pl-[var(--rail)]");
  });

  it("shows navigation and rail spacing after casting a chart", () => {
    useChartStore.setState({ hasChart: true });

    const { container } = render(<AppShell>content</AppShell>);

    expect(screen.getByTestId("app-nav")).toBeTruthy();
    expect(container.firstElementChild?.className).toContain("lg:pl-[var(--rail)]");
  });
});
