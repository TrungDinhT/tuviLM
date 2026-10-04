import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { queryKeys } from "@/lib/api/queryKeys";
import { authClient } from "@/lib/auth-client";

import { HoSoScreen } from "./ho-so-screen";

const { accountState, replace, refresh } = vi.hoisted(() => ({
  accountState: { data: null as { user: { id: string; name: string } } | null, isPending: false },
  replace: vi.fn(),
  refresh: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ replace, refresh }) }));
vi.mock("@/lib/auth-client", () => ({
  authClient: {
    useSession: () => accountState,
    token: vi.fn(),
    signOut: vi.fn().mockResolvedValue({}),
  },
}));
vi.mock("./settings-list", () => ({ SettingsList: () => null }));

beforeEach(() => {
  vi.clearAllMocks();
  accountState.data = null;
});
afterEach(() => vi.unstubAllGlobals());

describe("HoSoScreen", () => {
  it("asks guests to sign in without requesting private chart profiles", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    render(
      <QueryClientProvider client={new QueryClient()}>
        <HoSoScreen />
      </QueryClientProvider>,
    );

    expect(screen.getByText("Đăng nhập để xem và lưu lá số của bạn.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Đăng nhập" }).getAttribute("href")).toBe("/login");
    expect(screen.queryByRole("button", { name: "Đăng xuất" })).toBeNull();
    expect(screen.queryByLabelText("Mã ưu đãi")).toBeNull();
    expect(authClient.token).not.toHaveBeenCalled();
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("offers mobile and tablet logout under settings and returns home", async () => {
    accountState.data = { user: { id: "user-1", name: "Mai" } };
    const client = new QueryClient({ defaultOptions: { queries: { staleTime: Infinity } } });
    client.setQueryData(queryKeys.chartProfiles.all(), { chart_profiles: [] });
    render(
      <QueryClientProvider client={client}>
        <HoSoScreen />
      </QueryClientProvider>,
    );
    const button = screen.getByRole("button", { name: "Đăng xuất" });
    expect(button.className).toContain("min-h-11");
    expect(button.className).toContain("lg:hidden");
    expect(screen.getByText("Cài đặt").parentElement?.parentElement?.contains(button)).toBe(true);

    fireEvent.click(button);

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/"));
    expect(authClient.signOut).toHaveBeenCalledTimes(1);
    expect(refresh).toHaveBeenCalledTimes(1);
  });
});
