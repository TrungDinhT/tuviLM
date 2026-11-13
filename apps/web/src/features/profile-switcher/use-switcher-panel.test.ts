import { act, renderHook } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

import { useSwitcherPanel } from "./use-switcher-panel";

const opening = vi.hoisted(() => vi.fn());
vi.mock("@tanstack/react-query", () => ({ useIsMutating: () => (opening() ? 1 : 0) }));

beforeEach(() => opening.mockReturnValue(false));

it("opens, and clears the filter when it closes", () => {
  const { result } = renderHook(() => useSwitcherPanel());
  act(() => result.current.changeOpen(true));
  act(() => result.current.setSearch("mai"));
  expect(result.current).toMatchObject({ open: true, search: "mai" });
  act(() => result.current.changeOpen(false));
  expect(result.current).toMatchObject({ open: false, search: "" });
});

it("stays open while a chart is being opened, by this panel or another unit", () => {
  const { result, rerender } = renderHook(() => useSwitcherPanel());
  act(() => result.current.changeOpen(true));
  opening.mockReturnValue(true);
  rerender();
  expect(result.current.isOpening).toBe(true);
  act(() => result.current.changeOpen(false));
  expect(result.current.open).toBe(true);
});

it("closes after a switch even before the pending state has cleared", () => {
  const { result, rerender } = renderHook(() => useSwitcherPanel());
  act(() => result.current.changeOpen(true));
  opening.mockReturnValue(true);
  rerender();
  act(() => result.current.close());
  expect(result.current.open).toBe(false);
});
