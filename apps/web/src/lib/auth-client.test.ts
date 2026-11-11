import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

function jsonResponse(body: unknown, status = 200) {
  return new Response(body === null ? null : JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const signedIn = {
  user: { id: "user-1", email: "lan@example.com", name: "Lan", role: "user" },
  google_enabled: true,
};

/** The module keeps the session in module state, so each test loads a fresh copy. */
async function loadClient() {
  vi.resetModules();
  return (await import("./auth-client")).authClient;
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("useSession", () => {
  it("starts pending, then shows the account the API reports", async () => {
    vi.mocked(fetch).mockResolvedValue(jsonResponse(signedIn));
    const authClient = await loadClient();

    const { result } = renderHook(() => authClient.useSession());

    expect(result.current.isPending).toBe(true);
    await waitFor(() => expect(result.current.isPending).toBe(false));
    expect(result.current.data?.user.name).toBe("Lan");
    expect(result.current.googleEnabled).toBe(true);
    expect(fetch).toHaveBeenCalledWith("/api/v1/auth/session", { cache: "no-store" });
  });

  it("treats an unreachable API as signed out", async () => {
    vi.mocked(fetch).mockRejectedValue(new TypeError("offline"));
    const authClient = await loadClient();

    const { result } = renderHook(() => authClient.useSession());

    await waitFor(() => expect(result.current.isPending).toBe(false));
    expect(result.current.data).toBeNull();
  });
});

describe("authClient", () => {
  it("signs in, then asks the API for the new session", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse({ user: signedIn.user }))
      .mockResolvedValueOnce(jsonResponse(signedIn));
    const authClient = await loadClient();

    const result = await authClient.signIn.email({ email: "lan@example.com", password: "pw" });

    expect(result.error).toBeNull();
    expect(fetch).toHaveBeenNthCalledWith(1, "/api/v1/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: "lan@example.com", password: "pw" }),
    });
    expect(fetch).toHaveBeenNthCalledWith(2, "/api/v1/auth/session", { cache: "no-store" });
  });

  it.each([
    [403, "Email is not verified.", "EMAIL_NOT_VERIFIED"],
    [409, "Email is already registered.", "USER_ALREADY_EXISTS"],
    [400, "INVALID_TOKEN", "INVALID_TOKEN"],
    [429, "Too many attempts.", undefined],
  ])("maps a %s answer to a code the screens branch on", async (status, detail, code) => {
    vi.mocked(fetch).mockResolvedValue(jsonResponse({ detail }, status));
    const authClient = await loadClient();

    const result = await authClient.resetPassword({ token: "t", newPassword: "password123" });

    expect(result.error).toEqual({ status, code, message: detail });
  });

  it("sends the reset password under the API's field names", async () => {
    vi.mocked(fetch).mockResolvedValue(jsonResponse(null, 204));
    const authClient = await loadClient();

    await authClient.resetPassword({ token: "t", newPassword: "password123" });

    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/auth/reset-password",
      expect.objectContaining({ body: JSON.stringify({ token: "t", password: "password123" }) }),
    );
  });

  it("reports Google as unavailable when the API has no Google config", async () => {
    vi.mocked(fetch).mockResolvedValue(jsonResponse({ user: null, google_enabled: false }));
    const authClient = await loadClient();

    const result = await authClient.signIn.social({ provider: "google" });

    expect(result.error?.message).toBe("Provider not found");
  });

  it("forgets the session on sign-out", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(jsonResponse(signedIn))
      .mockResolvedValueOnce(jsonResponse(null, 204));
    const authClient = await loadClient();
    const { result } = renderHook(() => authClient.useSession());
    await waitFor(() => expect(result.current.data).not.toBeNull());

    await authClient.signOut();

    await waitFor(() => expect(result.current.data).toBeNull());
    expect(fetch).toHaveBeenLastCalledWith("/api/v1/auth/logout", {
      method: "POST",
      headers: undefined,
      body: undefined,
    });
  });
});
