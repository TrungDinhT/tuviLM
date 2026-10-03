import { authClient } from "@/lib/auth-client";
import { ApiErrorException } from "@/lib/http/errors";

export async function getAuthHeaders(): Promise<Record<string, string>> {
  const { data, error } = await authClient.token().catch((cause: unknown) => {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    throw new ApiErrorException({ kind: "network" });
  });

  if (error) {
    throw new ApiErrorException({ kind: "http", status: error.status, body: error });
  }
  if (!data?.token) {
    throw new ApiErrorException({
      kind: "http",
      status: 401,
      body: { detail: "Authentication required" },
    });
  }

  return { Authorization: `Bearer ${data.token}` };
}
