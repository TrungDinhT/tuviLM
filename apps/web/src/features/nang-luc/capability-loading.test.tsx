import { act, cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CapabilityLoading } from "./capability-loading";

afterEach(() => {
  cleanup();
  vi.useRealTimers();
});

describe("estimated capability progress", () => {
  it("advances evenly over 50 seconds and holds at 99 while waiting", () => {
    vi.useFakeTimers();
    render(<CapabilityLoading />);
    const ring = screen.getByRole("progressbar");
    expect(ring.getAttribute("aria-valuenow")).toBe("0");

    act(() => vi.advanceTimersByTime(25_000));
    expect(ring.getAttribute("aria-valuenow")).toBe("49");
    act(() => vi.advanceTimersByTime(25_000));
    expect(ring.getAttribute("aria-valuenow")).toBe("99");
    expect(ring.getAttribute("aria-valuetext")).toContain("đang chờ kết quả");
    act(() => vi.advanceTimersByTime(120_000));
    expect(ring.getAttribute("aria-valuenow")).toBe("99");
    expect(vi.getTimerCount()).toBe(0);
  });

  it("cleans up the timer and starts from zero for a new attempt", () => {
    vi.useFakeTimers();
    const first = render(<CapabilityLoading />);
    act(() => vi.advanceTimersByTime(10_000));
    expect(screen.getByRole("progressbar").getAttribute("aria-valuenow")).toBe("19");
    first.unmount();
    expect(vi.getTimerCount()).toBe(0);

    render(<CapabilityLoading />);
    expect(screen.getByRole("progressbar").getAttribute("aria-valuenow")).toBe("0");
  });
});
