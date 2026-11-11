import "server-only";

import { headers } from "next/headers";

import { env } from "@/config/env";
import type { Session, SessionUser } from "@/lib/auth-client";

/**
 * Who is signed in, for a server component. It asks the API directly with the
 * browser's cookies; the API still checks the account on every request it serves.
 */
export async function getServerSession(): Promise<Session | null> {
  const cookie = (await headers()).get("cookie");
  if (!cookie) return null;
  try {
    const response = await fetch(`${env.API_ORIGIN.replace(/\/$/, "")}/api/v1/auth/session`, {
      headers: { cookie },
      cache: "no-store",
    });
    if (!response.ok) return null;
    const body = (await response.json()) as { user: SessionUser | null };
    return body.user ? { user: body.user } : null;
  } catch {
    return null;
  }
}
