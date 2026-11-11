import { act, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AuthLinks } from "./auth-links";
import { BrandLink } from "./brand-link";

vi.mock("@/lib/auth-client", () => ({
  authClient: { useSession: () => ({ data: null, isPending: false }) },
}));

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("AuthLinks responsive registration", () => {
  it("hides only registration when space is tight and restores it when both links fit", () => {
    let availableWidth = 160;
    let notifyResize!: () => void;
    const observe = vi.fn();
    const disconnect = vi.fn();
    vi.stubGlobal(
      "ResizeObserver",
      class {
        observe = observe;
        unobserve = vi.fn();
        disconnect = disconnect;
        constructor(callback: ResizeObserverCallback) {
          notifyResize = () => callback([], this);
        }
      },
    );
    vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(function (
      this: HTMLElement,
    ) {
      const width =
        this.getAttribute("href") === "/login"
          ? 80
          : this.getAttribute("href") === "/register"
            ? 100
            : availableWidth;
      return new DOMRect(0, 0, width, 36);
    });
    const view = render(
      <>
        <BrandLink />
        <AuthLinks />
      </>,
    );
    const login = screen.getByRole("link", { name: "Đăng nhập" });
    const registration = view.container.querySelector<HTMLAnchorElement>('a[href="/register"]')!;
    login.parentElement!.style.columnGap = "8px";
    act(() => notifyResize());
    expect(screen.getByText("Thiên Hạc")).toBeTruthy();
    expect(login.getAttribute("href")).toBe("/login");
    expect(screen.queryByRole("link", { name: "Đăng ký" })).toBeNull();
    expect(registration.getAttribute("aria-hidden")).toBe("true");
    expect(registration.tabIndex).toBe(-1);
    expect(observe.mock.calls.map(([node]) => node)).toEqual([
      login.parentElement,
      login,
      registration,
    ]);

    availableWidth = 188;
    act(() => notifyResize());
    expect(screen.getByRole("link", { name: "Đăng ký" })).toBe(registration);
    expect(registration.tabIndex).toBe(0);
    expect(screen.getByRole("link", { name: "Đăng nhập" })).toBe(login);
    expect(screen.getByText("Thiên Hạc")).toBeTruthy();

    availableWidth = 187;
    act(() => notifyResize());
    expect(screen.queryByRole("link", { name: "Đăng ký" })).toBeNull();
    expect(registration.tabIndex).toBe(-1);
    expect(screen.getByRole("link", { name: "Đăng nhập" })).toBe(login);
    expect(screen.getByText("Thiên Hạc")).toBeTruthy();
    view.unmount();
    expect(disconnect).toHaveBeenCalledOnce();
  });
});
