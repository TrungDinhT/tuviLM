import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AccountRequestContext } from "@/lib/api/account-request";
import { useChartStore } from "@/store/chart-store";

import { AppShell } from "./app-shell";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

vi.mock("./app-nav", () => ({
  AppNav: () => <nav data-testid="app-nav" />,
}));

vi.mock("./top-bar", () => ({
  TopBar: ({ showBrand }: { showBrand?: boolean }) => (
    <header data-testid="top-bar" data-show-brand={String(showBrand)} />
  ),
}));

afterEach(() => {
  useChartStore.setState({ hasChart: false, outcome: null, previewOutcome: null, chartId: null });
});

describe("AppShell navigation", () => {
  it("hides guest navigation before casting but keeps the signed-in sidebar", () => {
    const { container, rerender } = render(<AppShell>content</AppShell>);

    expect(screen.queryByTestId("app-nav")).toBeNull();
    expect(screen.getByTestId("top-bar").getAttribute("data-show-brand")).toBe("true");
    expect(container.firstElementChild?.className).not.toContain("lg:pl-[var(--rail)]");

    rerender(
      <AccountRequestContext.Provider value={{ getSignal: () => undefined, userId: "user-1" }}>
        <AppShell>content</AppShell>
      </AccountRequestContext.Provider>,
    );
    expect(screen.getByTestId("app-nav")).toBeTruthy();
    expect(screen.getByTestId("top-bar").getAttribute("data-show-brand")).toBe("false");
    expect(container.firstElementChild?.className).toContain("lg:pl-[var(--rail)]");
  });

  it("shows navigation and rail spacing after casting a chart", () => {
    useChartStore.setState({ hasChart: true });

    const { container } = render(<AppShell>content</AppShell>);

    expect(screen.getByTestId("app-nav")).toBeTruthy();
    expect(screen.getByTestId("top-bar").getAttribute("data-show-brand")).toBe("false");
    expect(container.firstElementChild?.className).toContain("lg:pl-[var(--rail)]");
  });
});
