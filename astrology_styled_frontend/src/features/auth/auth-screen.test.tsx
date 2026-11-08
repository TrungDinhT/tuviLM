import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AccountRequestContext } from "@/lib/api/account-request";
import { apiEndpoints } from "@/lib/api/endpoints";

import { AuthScreen } from "./auth-screen";

const authMocks = vi.hoisted(() => ({
  session: null as { user: { id: string } } | null,
  signInEmail: vi.fn(),
  signInSocial: vi.fn(),
  signUpEmail: vi.fn(),
  sendVerificationEmail: vi.fn(),
}));
const toastMocks = vi.hoisted(() => ({ showToast: vi.fn() }));
const router = vi.hoisted(() => ({ replace: vi.fn() }));
const request = vi.hoisted(() => vi.fn());

vi.mock("next/navigation", () => ({
  useRouter: () => router,
}));

vi.mock("@/lib/auth-client", () => ({
  authClient: {
    useSession: () => ({ data: authMocks.session, isPending: false }),
    signIn: { email: authMocks.signInEmail, social: authMocks.signInSocial },
    signUp: { email: authMocks.signUpEmail },
    sendVerificationEmail: authMocks.sendVerificationEmail,
  },
}));

vi.mock("@/lib/toast", () => toastMocks);
vi.mock("@/lib/api/client", () => ({ request }));

function renderAuth(mode: "login" | "register" = "login", callbackError?: string) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const scope = { userId: "account-a", getSignal: () => undefined };
  const element = () => (
    <QueryClientProvider client={client}>
      <AccountRequestContext.Provider value={scope}>
        <AuthScreen mode={mode} callbackError={callbackError} />
      </AccountRequestContext.Provider>
    </QueryClientProvider>
  );
  const view = render(element());
  return { ...view, refreshSession: () => view.rerender(element()) };
}

beforeEach(() => {
  vi.resetAllMocks();
  authMocks.session = null;
  authMocks.signInEmail.mockResolvedValue({ error: null });
  authMocks.signInSocial.mockResolvedValue({ error: null });
  authMocks.signUpEmail.mockResolvedValue({ error: null });
  authMocks.sendVerificationEmail.mockResolvedValue({ error: null });
});

function submitLogin(email = "user@example.com", password = "password123") {
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: email } });
  fireEvent.change(screen.getByLabelText("Mật khẩu"), { target: { value: password } });
  fireEvent.submit(screen.getByRole("button", { name: "Đăng nhập" }).closest("form")!);
}

describe("AuthScreen", () => {
  it("uses the Zod message instead of native browser validation for an empty form", () => {
    renderAuth("register");

    const submitButton = screen.getByRole("button", { name: "Tạo tài khoản" });
    const form = submitButton.closest("form");

    expect(form?.noValidate).toBe(true);
    fireEvent.submit(form!);

    expect(toastMocks.showToast).toHaveBeenCalledWith("Vui lòng nhập tên hiển thị.");
    expect(authMocks.signUpEmail).not.toHaveBeenCalled();
  });

  it("links the register form to the privacy policy in a new tab", () => {
    renderAuth("register");

    const link = screen.getByRole("link", { name: "Chính sách riêng tư" });

    expect(link.getAttribute("href")).toBe("/privacy");
    expect(link.getAttribute("target")).toBe("_blank");
  });

  it.each([
    { profiles: [{ id: "profile-a" }], route: "/ho-so" },
    { profiles: [], route: "/" },
  ])(
    "waits for the signed-in account's saved charts before opening $route",
    async ({ profiles, route }) => {
      let resolveProfiles!: (value: unknown) => void;
      request.mockReturnValue(
        new Promise((resolve) => {
          resolveProfiles = resolve;
        }),
      );
      const view = renderAuth();
      fireEvent.change(screen.getByLabelText("Email"), { target: { value: "user@example.com" } });
      fireEvent.change(screen.getByLabelText("Mật khẩu"), { target: { value: "password123" } });
      fireEvent.submit(screen.getByRole("button", { name: "Đăng nhập" }).closest("form")!);

      await waitFor(() =>
        expect(authMocks.signInEmail).toHaveBeenCalledWith({
          email: "user@example.com",
          password: "password123",
        }),
      );
      expect(request).not.toHaveBeenCalled();
      expect(router.replace).not.toHaveBeenCalled();

      authMocks.session = { user: { id: "account-a" } };
      view.refreshSession();
      expect(screen.getByRole("status").textContent).toContain("Đang kiểm tra");
      await waitFor(() =>
        expect(request).toHaveBeenCalledWith(
          apiEndpoints.chartProfiles,
          expect.objectContaining({
            withAuth: true,
            expectedUserId: "account-a",
          }),
        ),
      );
      expect(router.replace).not.toHaveBeenCalled();

      resolveProfiles({ chart_profiles: profiles });
      await waitFor(() => expect(router.replace).toHaveBeenCalledWith(route));
    },
  );

  it("offers retry instead of treating a failed profile lookup as an empty history", async () => {
    authMocks.session = { user: { id: "account-a" } };
    request
      .mockRejectedValueOnce(new Error("Offline"))
      .mockResolvedValueOnce({ chart_profiles: [] });
    renderAuth();

    await screen.findByRole("alert");
    expect(router.replace).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Thử lại" }));
    await waitFor(() => expect(router.replace).toHaveBeenCalledWith("/"));
  });

  it("returns Google sign-in to the same saved-chart routing flow", async () => {
    renderAuth();
    fireEvent.click(screen.getByRole("button", { name: /Google/ }));
    await waitFor(() =>
      expect(authMocks.signInSocial).toHaveBeenCalledWith({
        provider: "google",
        callbackURL: "/login",
        errorCallbackURL: "/login",
      }),
    );
  });

  it("asks a new account to confirm its email before signing in", async () => {
    renderAuth("register");
    fireEvent.change(screen.getByLabelText("Tên hiển thị"), { target: { value: "Lan" } });
    fireEvent.change(screen.getByLabelText("Email"), { target: { value: "lan@example.com" } });
    fireEvent.change(screen.getByLabelText("Mật khẩu"), { target: { value: "password123" } });
    fireEvent.change(screen.getByLabelText("Nhập lại mật khẩu"), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.submit(screen.getByRole("button", { name: "Tạo tài khoản" }).closest("form")!);

    expect((await screen.findByRole("status")).textContent).toContain("lan@example.com");
    expect(authMocks.signUpEmail).toHaveBeenCalledWith({
      name: "Lan",
      email: "lan@example.com",
      password: "password123",
      callbackURL: "/login",
      fetchOptions: { disableSignal: true },
    });
    expect(authMocks.sendVerificationEmail).not.toHaveBeenCalled();
    expect(screen.getByRole("link", { name: "Đến trang đăng nhập" }).getAttribute("href")).toBe(
      "/login",
    );
  });

  it("resends the confirmation link when an unverified account signs in", async () => {
    authMocks.signInEmail.mockResolvedValue({
      error: { code: "EMAIL_NOT_VERIFIED", status: 403, message: "Email not verified" },
    });
    renderAuth();
    submitLogin();

    await waitFor(() =>
      expect(authMocks.sendVerificationEmail).toHaveBeenCalledWith({
        email: "user@example.com",
        callbackURL: "/login",
      }),
    );
    expect(screen.getByRole("status").textContent).toContain("chưa được xác nhận");
    expect(toastMocks.showToast).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Gửi lại email xác nhận" }));
    await waitFor(() => expect(authMocks.sendVerificationEmail).toHaveBeenCalledTimes(2));
    await waitFor(() =>
      expect(toastMocks.showToast).toHaveBeenCalledWith("Đã gửi lại email xác nhận."),
    );

    fireEvent.click(screen.getByRole("button", { name: "Quay lại đăng nhập" }));
    expect(screen.getByRole("button", { name: "Đăng nhập" })).toBeTruthy();
  });

  it("keeps the wrong-password message for other sign-in failures", async () => {
    authMocks.signInEmail.mockResolvedValue({
      error: { code: "INVALID_EMAIL_OR_PASSWORD", status: 401, message: "Invalid" },
    });
    renderAuth();
    submitLogin();

    await waitFor(() =>
      expect(toastMocks.showToast).toHaveBeenCalledWith("Email hoặc mật khẩu chưa đúng."),
    );
    expect(authMocks.sendVerificationEmail).not.toHaveBeenCalled();
  });

  it.each(["TOKEN_EXPIRED", "INVALID_TOKEN"])(
    "explains an unusable verification link (%s)",
    (error) => {
      renderAuth("login", error);
      expect(toastMocks.showToast).toHaveBeenCalledWith(
        "Link xác nhận đã hết hạn. Hãy đăng nhập để nhận link mới.",
      );
    },
  );

  it("ignores unrelated callback errors", () => {
    renderAuth("login", "state_mismatch");
    expect(toastMocks.showToast).not.toHaveBeenCalled();
  });

  it("links to the forgot-password page", () => {
    renderAuth();
    expect(screen.getByRole("link", { name: "Quên mật khẩu?" }).getAttribute("href")).toBe(
      "/forgot-password",
    );
  });
});
