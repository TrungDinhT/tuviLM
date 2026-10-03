import { parseUserInput } from "better-auth/db";
import { describe, expect, it } from "vitest";

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
