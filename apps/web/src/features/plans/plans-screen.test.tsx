import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import type { AccountAccess } from "@/lib/api/schemas";

import { PlansScreen } from "./plans-screen";

const mocks = vi.hoisted(() => ({
  access: vi.fn(),
  scope: vi.fn(),
  refetch: vi.fn(),
  showToast: vi.fn(),
}));

vi.mock("@/lib/api/hooks", () => ({ useAccountAccess: mocks.access }));
vi.mock("@/lib/api/account-request", () => ({ useAccountRequestScope: mocks.scope }));
vi.mock("@/lib/toast", () => ({ showToast: mocks.showToast }));

const ACCESS: AccountAccess = { user_id: "user-1", role: "user", plan: "normal", balance: 1234 };
const QUERY = {
  data: ACCESS,
  isSuccess: true,
  isError: false,
  isFetching: false,
  refetch: mocks.refetch,
};

beforeEach(() => {
  vi.clearAllMocks();
  mocks.scope.mockReturnValue({ userId: "user-1" });
  mocks.access.mockReturnValue(QUERY);
});
afterEach(() => vi.unstubAllGlobals());

describe("PlansScreen", () => {
  it("shows the real balance and keeps bundle and upgrade actions informational", () => {
    const request = vi.fn();
    vi.stubGlobal("fetch", request);
    render(<PlansScreen />);

    expect(screen.getByLabelText("Số dư tài khoản").textContent).toMatch(/1\.234\s*xu/);
    fireEvent.click(screen.getByRole("radio", { name: "90 xu" }));
    expect((screen.getByRole("radio", { name: "90 xu" }) as HTMLInputElement).checked).toBe(true);
    expect(screen.getByText(/Bạn chọn/).textContent).toContain("90 xu");
    fireEvent.click(screen.getByRole("button", { name: "Chọn gói xu" }));
    fireEvent.click(screen.getByRole("button", { name: "Mở khóa toàn bộ" }));

    expect(mocks.showToast.mock.calls).toEqual([
      ["Tính năng sẽ được cập nhật"],
      ["Tính năng sẽ được cập nhật"],
    ]);
    expect(screen.getByLabelText("Số dư tài khoản").textContent).toMatch(/1\.234\s*xu/);
    expect(ACCESS.balance).toBe(1234);
    expect(request).not.toHaveBeenCalled();
  });

  it("hides the wallet, bundles, and numeric coin amounts for full unlock", () => {
    mocks.access.mockReturnValue({ ...QUERY, data: { ...ACCESS, plan: "full_unlock" } });
    const { container } = render(<PlansScreen />);

    expect(screen.getByRole("heading", { name: "Mở khóa toàn bộ" })).toBeTruthy();
    expect(screen.getByText("Đang sử dụng")).toBeTruthy();
    expect(screen.getByText("Trò chuyện với AI đã được bao gồm trong gói của bạn.")).toBeTruthy();
    expect(screen.queryByRole("heading", { name: "Ví của bạn" })).toBeNull();
    expect(screen.queryByLabelText("Số dư tài khoản")).toBeNull();
    expect(screen.queryAllByRole("radio")).toHaveLength(0);
    expect(screen.queryByRole("button", { name: "Chọn gói xu" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Mở khóa toàn bộ" })).toBeNull();
    expect(container.textContent).not.toMatch(/\d[\d.,]*\s*xu/);
  });

  it("avoids fabricated or stale balances for guest, loading, and error states", () => {
    mocks.scope.mockReturnValue({ userId: null });
    mocks.access.mockReturnValue({ ...QUERY, data: undefined, isSuccess: false });
    const { rerender } = render(<PlansScreen />);
    expect(screen.getByText("Đăng nhập để xem số dư của bạn.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Đăng nhập" }).getAttribute("href")).toBe("/login");
    expect(screen.queryByLabelText("Số dư tài khoản")).toBeNull();

    mocks.scope.mockReturnValue({ userId: "user-1" });
    rerender(<PlansScreen />);
    expect(screen.getByText("Đang tải thông tin tài khoản…")).toBeTruthy();
    expect(screen.queryByLabelText("Số dư tài khoản")).toBeNull();

    mocks.access.mockReturnValue({ ...QUERY, isSuccess: false, isError: true });
    rerender(<PlansScreen />);
    expect(screen.getByRole("alert").textContent).toBe("Không tải được thông tin tài khoản.");
    expect(screen.queryByLabelText("Số dư tài khoản")).toBeNull();
    expect(screen.queryByText("1.234")).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    expect(mocks.refetch).toHaveBeenCalledOnce();

    mocks.access.mockReturnValue(QUERY);
    rerender(<PlansScreen />);
    expect(screen.getByLabelText("Số dư tài khoản").textContent).toMatch(/1\.234\s*xu/);
  });
});
