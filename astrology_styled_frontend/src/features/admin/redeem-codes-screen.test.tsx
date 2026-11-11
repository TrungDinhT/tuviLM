import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { RedeemCodesScreen } from "./redeem-codes-screen";

const mocks = vi.hoisted(() => ({ access: vi.fn(), scope: vi.fn() }));
vi.mock("@/lib/api/hooks", async (importOriginal) => ({
  ...(await importOriginal<typeof import("@/lib/api/hooks")>()),
  useAccountAccess: mocks.access,
}));
vi.mock("@/lib/api/account-request", () => ({ useAccountRequestScope: mocks.scope }));
vi.mock("@/lib/auth-client", () => ({
  authClient: {
    token: vi.fn().mockResolvedValue({
      data: { token: "header.eyJzdWIiOiJ1c2VyLTEifQ.signature" },
      error: null,
    }),
  },
}));

const QUERY = {
  data: { user_id: "user-1", role: "admin", plan: "normal", balance: 0 },
  isSuccess: true,
  isPending: false,
  isFetching: false,
  isError: false,
};

beforeEach(() => {
  vi.clearAllMocks();
  mocks.scope.mockReturnValue({ userId: "user-1", getSignal: () => undefined });
  mocks.access.mockReturnValue(QUERY);
});
afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

function renderScreen() {
  const client = new QueryClient();
  return render(<RedeemCodesScreen />, {
    wrapper: ({ children }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    ),
  });
}

describe("RedeemCodesScreen", () => {
  it("hides creation for guests, other accounts, non-admins, and unverified cached access", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    mocks.scope.mockReturnValue({ userId: null, getSignal: () => undefined });
    const { rerender } = renderScreen();
    expect(screen.getByRole("link", { name: "đăng nhập" }).getAttribute("href")).toBe("/login");
    expect(screen.queryByLabelText("Số xu")).toBeNull();

    mocks.scope.mockReturnValue({ userId: "user-1", getSignal: () => undefined });
    for (const query of [
      { ...QUERY, data: { ...QUERY.data, role: "user" } },
      { ...QUERY, data: { ...QUERY.data, user_id: "other-user" } },
      { ...QUERY, isError: true, isSuccess: false },
      { ...QUERY, isFetching: true },
    ]) {
      mocks.access.mockReturnValue(query);
      rerender(<RedeemCodesScreen />);
      expect(screen.queryByLabelText("Số xu")).toBeNull();
    }
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("creates the chosen code with a three-day deadline and clears old success on failure", async () => {
    vi.spyOn(Date, "now").mockReturnValue(Date.UTC(2026, 9, 4, 12));
    const created = {
      code: "WELCOME",
      coins: 60,
      kind: "per_account",
      expires_at: "2026-10-07T12:00:00.000Z",
    };
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(created), { status: 201 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "Unavailable" }), { status: 503 }),
      );
    vi.stubGlobal("fetch", fetchMock);
    renderScreen();
    expect((screen.getByLabelText("Thời hạn (ngày)") as HTMLInputElement).value).toBe("3");
    fireEvent.change(screen.getByLabelText("Số xu"), { target: { value: "60" } });
    fireEvent.change(screen.getByLabelText("Loại mã"), { target: { value: "per_account" } });
    fireEvent.click(screen.getByRole("button", { name: "Tạo mã" }));

    await screen.findByText(created.code);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/admin/redeem-codes"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ coins: 60, kind: "per_account", expires_at: created.expires_at }),
      }),
    );
    fireEvent.click(screen.getByRole("button", { name: "Tạo mã" }));
    expect((await screen.findByRole("alert")).textContent).toContain("Tạo mã thất bại.");
    expect(screen.queryByText(created.code)).toBeNull();
  });
});
