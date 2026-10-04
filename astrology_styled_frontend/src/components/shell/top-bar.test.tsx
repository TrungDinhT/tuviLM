import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { AccountRequestContext } from "@/lib/api/account-request";
import { queryKeys } from "@/lib/api/queryKeys";
import { authClient } from "@/lib/auth-client";
import { useChartStore } from "@/store/chart-store";

import { AppNav } from "./app-nav";
import { StickyHeader } from "./sticky-header";
import { TopBar } from "./top-bar";

const navigation = vi.hoisted(() => ({ pathname: "/ho-so", replace: vi.fn(), refresh: vi.fn() }));
vi.mock("next/navigation", () => ({
  usePathname: () => navigation.pathname,
  useRouter: () => ({ replace: navigation.replace, refresh: navigation.refresh }),
}));
vi.mock("@/lib/auth-client", () => ({
  authClient: {
    useSession: () => ({ data: { user: { id: "user-1", name: "Test User" } }, isPending: false }),
    token: vi.fn().mockResolvedValue({
      data: { token: "header.eyJzdWIiOiJ1c2VyLTEifQ.signature" },
      error: null,
    }),
    signOut: vi.fn(),
  },
}));

const ACCESS = { user_id: "user-1", role: "user", plan: "normal", balance: 1234 };
function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
function header(client: QueryClient, mobile = false) {
  return (
    <QueryClientProvider client={client}>
      <AccountRequestContext.Provider value={{ getSignal: () => undefined, userId: "user-1" }}>
        {mobile ? (
          <StickyHeader eyebrow="Lá số của bạn" title="Hồ sơ của bạn" />
        ) : (
          <>
            <TopBar />
            <AppNav />
          </>
        )}
      </AccountRequestContext.Provider>
    </QueryClientProvider>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  navigation.pathname = "/ho-so";
  useChartStore.setState({ hasChart: false });
});
afterEach(() => vi.unstubAllGlobals());

describe("TopBar balance", () => {
  it("shows the signed-in account balance in the shared header across pages", async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse(ACCESS)));
    vi.stubGlobal("fetch", fetchMock);
    const client = new QueryClient();
    const view = render(header(client));
    expect(await screen.findByText("1.234 xu")).toBeTruthy();
    expect(screen.getByLabelText("Số dư tài khoản").closest("header")).not.toBeNull();
    expect(screen.getByLabelText("Số dư tài khoản").getAttribute("title")).toContain("Gói Cơ bản");
    navigation.pathname = "/";
    view.rerender(header(client));
    const indexBanner = screen.getByRole("banner");
    expect(within(indexBanner).queryByRole("heading", { name: "An sao" })).toBeNull();
    expect(within(indexBanner).queryByText("Lá số của bạn")).toBeNull();
    expect(within(indexBanner).getByLabelText("Số dư tài khoản")).toBeTruthy();
    expect(within(indexBanner).getByText("Test User")).toBeTruthy();
    navigation.pathname = "/van-han";
    view.rerender(header(client));
    expect(screen.getByRole("heading", { name: "Vận hạn 2026" })).toBeTruthy();
    expect(screen.getByText("1.234 xu")).toBeTruthy();
    expect(screen.queryByLabelText("Account plan and balance")).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(
      within(screen.getByRole("banner")).getByRole("button", { name: "Đăng xuất" }).className,
    ).toContain("lg:hidden");
    const nav = screen.getByRole("navigation");
    expect(nav.className).toContain("hidden lg:flex");
    expect(
      within(nav)
        .getAllByRole("link")
        .map((link) => link.getAttribute("href")),
    ).toEqual(["/", "/ho-so"]);
    const brand = within(nav).getByRole("link", { name: "Thiên Hạc — về trang chủ" });
    expect(brand.getAttribute("href")).toBe("/");
    expect(brand.querySelector("img")?.getAttribute("src")).toContain("favicon-48x48.png");
    const sidebarSignOut = within(nav).getByRole("button", { name: "Đăng xuất" });
    expect(sidebarSignOut.parentElement?.className).toMatch(/hidden.*lg:block/);
    let finishSignOut!: () => void;
    vi.mocked(authClient.signOut).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finishSignOut = () => resolve({ data: { success: true }, error: null });
        }),
    );
    fireEvent.click(sidebarSignOut);
    expect(
      (within(nav).getByRole("button", { name: "Đăng xuất" }) as HTMLButtonElement).disabled,
    ).toBe(true);
    expect(authClient.signOut).toHaveBeenCalledTimes(1);
    expect(navigation.replace).not.toHaveBeenCalled();
    await act(async () => finishSignOut());
    expect(navigation.replace).toHaveBeenCalledWith("/");
    expect(navigation.refresh).toHaveBeenCalledTimes(1);
    view.unmount();
    render(header(client, true));
    expect(await screen.findByText("1.234 xu")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Hồ sơ của bạn" })).toBeTruthy();
  });

  it("does not invent a loading balance and hides stale coins until Retry succeeds", async () => {
    let resolveAccess!: (response: Response) => void;
    const pending = new Promise<Response>((resolve) => {
      resolveAccess = resolve;
    });
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockReturnValueOnce(pending)
        .mockResolvedValueOnce(jsonResponse({}, 503))
        .mockImplementation(() => Promise.resolve(jsonResponse(ACCESS))),
    );
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(header(client));
    expect(screen.getByText("Số dư…")).toBeTruthy();
    expect(screen.queryByText("0 xu")).toBeNull();
    await act(async () => resolveAccess(jsonResponse(ACCESS)));
    await screen.findByText("1.234 xu");
    await act(async () => {
      await client.invalidateQueries({ queryKey: queryKeys.accountAccess("user-1") });
    });
    expect(await screen.findByRole("button", { name: "Thử lại" })).toBeTruthy();
    expect(screen.queryByText("1.234 xu")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    expect(await screen.findByText("1.234 xu")).toBeTruthy();
  });
});
