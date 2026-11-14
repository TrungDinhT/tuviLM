import "server-only";

import { Effect } from "effect";
import { headers } from "next/headers";

import { env } from "@/config/env";
import { apiRequest, runApi, withFetchOptions } from "@/lib/api/client";
import { sessionResponseSchema } from "@/lib/api/schemas";
import type { Session } from "@/lib/auth-client";

/**
 * Who is signed in, for a server component. It asks the API directly with the
 * browser's cookies; the API still checks the account on every request it serves.
 * Any failure renders as signed out.
 */
export async function getServerSession(): Promise<Session | null> {
  const cookie = (await headers()).get("cookie");
  if (!cookie) return null;
  return runApi(
    apiRequest(`${env.API_ORIGIN.replace(/\/$/, "")}/api/v1/auth/session`, {
      schema: sessionResponseSchema,
      headers: { cookie },
    }).pipe(
      withFetchOptions({ cache: "no-store" }),
      Effect.map((body): Session | null => (body.user ? { user: body.user } : null)),
      Effect.orElseSucceed(() => null),
    ),
  );
}
