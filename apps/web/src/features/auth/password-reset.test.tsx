import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ForgotPasswordScreen, ResetPasswordScreen } from "./password-reset";

const authMocks = vi.hoisted(() => ({
  requestPasswordReset: vi.fn(),
  resetPassword: vi.fn(),
}));
const toastMocks = vi.hoisted(() => ({ showToast: vi.fn() }));

vi.mock("@/lib/auth-client", () => ({ authClient: authMocks }));
vi.mock("@/lib/toast", () => toastMocks);

beforeEach(() => {
  vi.resetAllMocks();
  authMocks.requestPasswordReset.mockResolvedValue({ error: null });
  authMocks.resetPassword.mockResolvedValue({ error: null });
});

function submit(buttonName: string) {
  fireEvent.submit(screen.getByRole("button", { name: buttonName }).closest("form")!);
}

describe("ForgotPasswordScreen", () => {
  it("requests a reset link that returns to the reset page", async () => {
    render(<ForgotPasswordScreen />);
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: " lan@example.com " } });
    submit("Gửi link đặt lại mật khẩu");

    expect((await screen.findByRole("status")).textContent).toContain("lan@example.com");
    expect(authMocks.requestPasswordReset).toHaveBeenCalledWith({
      email: "lan@example.com",
      redirectTo: "/reset-password",
    });

    fireEvent.click(screen.getByRole("button", { name: "Gửi lại link" }));
    await waitFor(() => expect(authMocks.requestPasswordReset).toHaveBeenCalledTimes(2));
  });

  it("validates the email before calling the server", () => {
    render(<ForgotPasswordScreen />);
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "not-an-email" } });
    submit("Gửi link đặt lại mật khẩu");

    expect(toastMocks.showToast).toHaveBeenCalledWith("Email chưa đúng định dạng.");
    expect(authMocks.requestPasswordReset).not.toHaveBeenCalled();
  });

  it("stays on the form when the request is rate limited", async () => {
    authMocks.requestPasswordReset.mockResolvedValue({ error: { status: 429 } });
    render(<ForgotPasswordScreen />);
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "lan@example.com" } });
    submit("Gửi link đặt lại mật khẩu");

    await waitFor(() =>
      expect(toastMocks.showToast).toHaveBeenCalledWith(
        "Bạn thao tác hơi nhanh. Vui lòng đợi một chút rồi thử lại.",
      ),
    );
    expect(screen.queryByRole("status")).toBeNull();
  });
});

describe("ResetPasswordScreen", () => {
  function fillPasswords(password: string, confirmPassword = password) {
    fireEvent.change(screen.getByLabelText("Mật khẩu mới"), { target: { value: password } });
    fireEvent.change(screen.getByLabelText("Nhập lại mật khẩu"), {
      target: { value: confirmPassword },
    });
  }

  it("offers a new link when the page has no usable token", () => {
    render(<ResetPasswordScreen token={null} />);

    expect(screen.getByRole("alert").textContent).toContain("không hợp lệ");
    expect(screen.getByRole("link", { name: "Gửi link mới" }).getAttribute("href")).toBe(
      "/forgot-password",
    );
  });

  it("saves the new password with the link's token", async () => {
    render(<ResetPasswordScreen token="reset-token" />);
    fillPasswords("new-password-1");
    submit("Lưu mật khẩu mới");

    expect((await screen.findByRole("status")).textContent).toContain("Mật khẩu mới đã được lưu");
    expect(authMocks.resetPassword).toHaveBeenCalledWith({
      newPassword: "new-password-1",
      token: "reset-token",
    });
    expect(screen.getByRole("link", { name: "Đăng nhập" }).getAttribute("href")).toBe("/login");
  });

  it("rejects mismatched passwords locally", () => {
    render(<ResetPasswordScreen token="reset-token" />);
    fillPasswords("new-password-1", "new-password-2");
    submit("Lưu mật khẩu mới");

    expect(toastMocks.showToast).toHaveBeenCalledWith("Hai mật khẩu chưa trùng nhau.");
    expect(authMocks.resetPassword).not.toHaveBeenCalled();
  });

  it("switches to the expired-link state when the server rejects the token", async () => {
    authMocks.resetPassword.mockResolvedValue({
      error: { code: "INVALID_TOKEN", status: 400, message: "Invalid token" },
    });
    render(<ResetPasswordScreen token="used-token" />);
    fillPasswords("new-password-1");
    submit("Lưu mật khẩu mới");

    expect((await screen.findByRole("alert")).textContent).toContain("đã hết hạn");
  });
});
