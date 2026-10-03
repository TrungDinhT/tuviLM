import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AuthScreen } from "./auth-screen";

const authMocks = vi.hoisted(() => ({
  signInEmail: vi.fn(),
  signInSocial: vi.fn(),
  signUpEmail: vi.fn(),
}));
const toastMocks = vi.hoisted(() => ({ showToast: vi.fn() }));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    signIn: { email: authMocks.signInEmail, social: authMocks.signInSocial },
    signUp: { email: authMocks.signUpEmail },
  },
}));

vi.mock("@/lib/toast", () => toastMocks);

beforeEach(() => {
  vi.clearAllMocks();
});

describe("AuthScreen registration validation", () => {
  it("uses the Zod message instead of native browser validation for an empty form", () => {
    render(<AuthScreen mode="register" />);

    const submitButton = screen.getByRole("button", { name: "Tạo tài khoản" });
    const form = submitButton.closest("form");

    expect(form?.noValidate).toBe(true);
    fireEvent.submit(form!);

    expect(toastMocks.showToast).toHaveBeenCalledWith("Vui lòng nhập tên hiển thị.");
    expect(authMocks.signUpEmail).not.toHaveBeenCalled();
  });
});
