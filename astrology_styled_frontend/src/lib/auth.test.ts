import { parseUserInput } from "better-auth/db";
import { afterEach, describe, expect, it, vi } from "vitest";

import { auth } from "@/lib/auth";

describe("server-managed account fields", () => {
  it("ignores protected fields supplied during signup", () => {
    expect(
      parseUserInput(auth.options, { role: "admin", plan: "full_unlock", balance: 1000 }, "create"),
    ).toEqual({ role: "user", plan: "normal", balance: 0 });
  });

  it("rejects client-supplied plan upgrades", () => {
    expect(() => parseUserInput(auth.options, { plan: "full_unlock" }, "update")).toThrow(
      "plan is not allowed to be set",
    );
  });
});

describe("email verification and password reset", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });

  it("requires a verified email and signs the user in once it is", () => {
    expect(auth.options.emailAndPassword).toMatchObject({
      requireEmailVerification: true,
      revokeSessionsOnPasswordReset: true,
    });
    expect(auth.options.emailVerification?.autoSignInAfterVerification).toBe(true);
  });

  it.each([
    {
      name: "verification",
      send: () => auth.options.emailVerification?.sendVerificationEmail,
      subject: "Xác nhận email · Thiên Hạc",
    },
    {
      name: "password reset",
      send: () => auth.options.emailAndPassword?.sendResetPassword,
      subject: "Đặt lại mật khẩu · Thiên Hạc",
    },
  ])("mails the $name link to the account's address", async ({ send, subject }) => {
    vi.stubEnv("RESEND_API_KEY", "re_test");
    vi.stubEnv("EMAIL_FROM", "no-reply@example.com");
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const user = {
      id: "user-a",
      name: "Lan",
      email: "lan@example.com",
      emailVerified: false,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    await send()?.({ user, url: "http://localhost:3000/link?token=t", token: "t" });

    const body = JSON.parse(String(fetchMock.mock.calls[0]?.[1]?.body)) as Record<string, unknown>;
    expect(body).toMatchObject({ to: ["lan@example.com"], subject });
    expect(body.text).toContain("http://localhost:3000/link?token=t");
  });
});

describe("Google OAuth configuration", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.resetModules();
  });

  it.each([
    { clientId: "stub-client", clientSecret: "stub-secret", enabled: true },
    { clientId: "stub-client", clientSecret: "", enabled: false },
    { clientId: "", clientSecret: "stub-secret", enabled: false },
  ])(
    "requires both Google credentials (enabled: $enabled)",
    async ({ clientId, clientSecret, enabled }) => {
      vi.stubEnv("GOOGLE_CLIENT_ID", clientId);
      vi.stubEnv("GOOGLE_CLIENT_SECRET", clientSecret);
      vi.resetModules();
      const { auth: configuredAuth } = await import("@/lib/auth");

      expect(configuredAuth.options.socialProviders).toEqual(
        enabled ? { google: { clientId, clientSecret, prompt: "select_account" } } : {},
      );
    },
  );
});
