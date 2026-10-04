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
