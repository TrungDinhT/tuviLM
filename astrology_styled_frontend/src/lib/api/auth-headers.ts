import { authClient } from "@/lib/auth-client";
import { ApiErrorException } from "@/lib/http/errors";

/** Stop reusing a token this long before it expires, so a slow request cannot outlive it. */
const EXPIRY_MARGIN_MS = 60_000;

interface CachedToken {
  token: string;
  subject: unknown;
  expiresAt: number;
}

let cachedToken: Promise<CachedToken> | null = null;

/** Forget the cached token when the account changes or the API rejects it. */
export function clearAuthToken(): void {
  cachedToken = null;
}

export async function getAuthHeaders(
  expectedUserId?: string | null,
): Promise<Record<string, string>> {
  if (expectedUserId === null) throw unauthorized("Authentication required");

  const cached = cachedToken;
  let token = cached === null ? null : await cached;
  if (token === null || !isReusable(token, expectedUserId)) token = await requestToken();

  // This only prevents stale UI requests from switching accounts. The API
  // still verifies the token's signature and active session.
  if (expectedUserId !== undefined && token.subject !== expectedUserId) {
    throw unauthorized("Account changed. Reload to continue.");
  }

  return { Authorization: `Bearer ${token.token}` };
}

/** Concurrent requests share one token request; a failed one is never reused. */
function requestToken(): Promise<CachedToken> {
  const pending = fetchToken();
  cachedToken = pending;
  pending.catch(() => {
    if (cachedToken === pending) cachedToken = null;
  });
  return pending;
}

async function fetchToken(): Promise<CachedToken> {
  const { data, error } = await authClient.token().catch((cause: unknown) => {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    throw new ApiErrorException({ kind: "network" });
  });

  if (error) {
    throw new ApiErrorException({ kind: "http", status: error.status, body: error });
  }
  if (!data?.token) throw unauthorized("Authentication required");

  const claims = readClaims(data.token);
  return {
    token: data.token,
    subject: claims.sub,
    // A token without a readable expiry is used once and never cached.
    expiresAt: typeof claims.exp === "number" ? claims.exp * 1000 : 0,
  };
}

function isReusable(token: CachedToken, expectedUserId: string | undefined): boolean {
  return (
    token.expiresAt - EXPIRY_MARGIN_MS > Date.now() &&
    (expectedUserId === undefined || token.subject === expectedUserId)
  );
}

function readClaims(token: string): { sub?: unknown; exp?: unknown } {
  try {
    const encodedPayload = token.split(".")[1] ?? "";
    const payload: unknown = JSON.parse(atob(encodedPayload.replace(/-/g, "+").replace(/_/g, "/")));
    if (payload !== null && typeof payload === "object") {
      return {
        sub: "sub" in payload ? payload.sub : undefined,
        exp: "exp" in payload ? payload.exp : undefined,
      };
    }
  } catch {
    // Malformed tokens are never reused and fail the account check.
  }
  return {};
}

function unauthorized(detail: string): ApiErrorException {
  return new ApiErrorException({ kind: "http", status: 401, body: { detail } });
}
