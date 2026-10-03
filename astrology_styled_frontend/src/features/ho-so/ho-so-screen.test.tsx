import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { authClient } from "@/lib/auth-client";

import { HoSoScreen } from "./ho-so-screen";

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    useSession: () => ({ data: null, isPending: false }),
    token: vi.fn(),
  },
}));
vi.mock("./settings-list", () => ({ SettingsList: () => null }));

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

    expect(screen.getByText("Sign in to view and save your charts.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Sign in" }).getAttribute("href")).toBe("/login");
    expect(authClient.token).not.toHaveBeenCalled();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
