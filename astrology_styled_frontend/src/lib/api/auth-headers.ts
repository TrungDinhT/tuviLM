import { authClient } from "@/lib/auth-client";
import { ApiErrorException } from "@/lib/http/errors";

export async function getAuthHeaders(
  expectedUserId?: string | null,
): Promise<Record<string, string>> {
  const { data, error } = await authClient.token().catch((cause: unknown) => {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    throw new ApiErrorException({ kind: "network" });
  });

  if (error) {
    throw new ApiErrorException({ kind: "http", status: error.status, body: error });
  }
  if (!data?.token || expectedUserId === null) {
    throw new ApiErrorException({
      kind: "http",
      status: 401,
      body: { detail: "Authentication required" },
    });
  }

  if (expectedUserId !== undefined) {
    // This only prevents stale UI requests from switching accounts. The API
    // still verifies the token's signature and active session.
    let subject: unknown;
    try {
      const encodedPayload = data.token.split(".")[1] ?? "";
      const payload: unknown = JSON.parse(
        atob(encodedPayload.replace(/-/g, "+").replace(/_/g, "/")),
      );
      if (payload !== null && typeof payload === "object" && "sub" in payload) {
        subject = payload.sub;
      }
    } catch {
      // Malformed tokens fail the account check below.
    }
    if (subject !== expectedUserId) {
      throw new ApiErrorException({
        kind: "http",
        status: 401,
        body: { detail: "Account changed. Reload to continue." },
      });
    }
  }

  return { Authorization: `Bearer ${data.token}` };
}
