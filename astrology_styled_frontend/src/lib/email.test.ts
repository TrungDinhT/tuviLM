import { afterEach, describe, expect, it, vi } from "vitest";

import { resetPasswordEmail, sendEmail, verificationEmail } from "@/lib/email";

const message = { to: "user@example.com", subject: "Chủ đề", text: "Nội dung", html: "<p>x</p>" };

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("sendEmail", () => {
  it("posts the message to Resend with the configured sender", async () => {
    vi.stubEnv("RESEND_API_KEY", "re_test");
    vi.stubEnv("EMAIL_FROM", "Thiên Hạc <no-reply@example.com>");
    const fetchMock = vi.fn().mockResolvedValue(new Response("{}", { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);

    await sendEmail(message);

    expect(fetchMock).toHaveBeenCalledWith("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: "Bearer re_test", "Content-Type": "application/json" },
      body: JSON.stringify({
        from: "Thiên Hạc <no-reply@example.com>",
        to: ["user@example.com"],
        subject: "Chủ đề",
        text: "Nội dung",
        html: "<p>x</p>",
      }),
    });
  });

  it("fails when Resend rejects the message", async () => {
    vi.stubEnv("RESEND_API_KEY", "re_test");
    vi.stubEnv("EMAIL_FROM", "no-reply@example.com");
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("domain", { status: 403 })));

    await expect(sendEmail(message)).rejects.toThrow("Resend rejected the email (403): domain");
  });

  it("prints the message instead of sending when unconfigured in development", async () => {
    vi.stubEnv("RESEND_API_KEY", "");
    vi.stubEnv("NODE_ENV", "development");
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    const info = vi.spyOn(console, "info").mockImplementation(() => {});

    await sendEmail(message);

    expect(fetchMock).not.toHaveBeenCalled();
    expect(info).toHaveBeenCalledWith(expect.stringContaining("Nội dung"));
  });

  it("refuses to drop mail silently in production", async () => {
    vi.stubEnv("RESEND_API_KEY", "");
    vi.stubEnv("NODE_ENV", "production");

    await expect(sendEmail(message)).rejects.toThrow("RESEND_API_KEY and EMAIL_FROM");
  });
});

describe("auth emails", () => {
  it.each([
    { build: verificationEmail, subject: "Xác nhận email · Thiên Hạc" },
    { build: resetPasswordEmail, subject: "Đặt lại mật khẩu · Thiên Hạc" },
  ])("carries the link in both parts ($subject)", ({ build, subject }) => {
    const url = "http://localhost:3000/api/auth/verify-email?token=abc&callbackURL=%2Flogin";
    const email = build({ name: "Lan", url });

    expect(email.subject).toBe(subject);
    expect(email.text).toContain("Chào Lan,");
    expect(email.text).toContain(url);
    expect(email.html).toContain(`href="${url.replaceAll("&", "&amp;")}"`);
  });

  it.each([verificationEmail, resetPasswordEmail])(
    "sets no background colour, so it reads on the mail client's own surface",
    (build) => {
      const email = build({ name: "Lan", url: "https://x.test/link" });

      expect(email.html).not.toMatch(/background|bgcolor/i);
    },
  );

  it("escapes the user's name in the HTML part", () => {
    const email = verificationEmail({ name: '<img src=x onerror="1">', url: "https://x.test" });

    expect(email.html).not.toContain("<img src=x");
    expect(email.html).toContain("&lt;img src=x onerror=&quot;1&quot;&gt;");
  });
});
