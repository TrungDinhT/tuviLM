import { Effect } from "effect";
import type { HttpClient } from "effect/http";
import { useEffect, useSyncExternalStore } from "react";

import {
  apiRequest,
  makeRequest,
  readBody,
  runApi,
  send,
  withFetchOptions,
} from "@/lib/api/client";
import { sessionResponseSchema, type SessionUser } from "@/lib/api/schemas";

/**
 * Login, through the FastAPI routes under `/api/v1/auth`.
 *
 * The session is an httpOnly cookie that the API sets; the browser sends it
 * with every same-origin `/api` request, so no token is handled here. This
 * module only keeps who is signed in, for rendering. Every call is an Effect
 * program on the API client, run as a promise for the screens.
 *
 * The session lives in a small store outside TanStack Query on purpose: the
 * query client is created per account (see QueryProvider), so it cannot hold
 * the value that decides which account that is.
 */

export type { SessionUser };

export interface Session {
  user: SessionUser;
}

export interface AuthError {
  status: number;
  code?: string;
  message?: string;
}

export interface AuthResult {
  error: AuthError | null;
}

interface SessionState {
  /** `undefined` until the first answer arrives. */
  session: Session | null | undefined;
  googleEnabled: boolean;
}

const SESSION_PATH = "/api/v1/auth/session";

let state: SessionState = { session: undefined, googleEnabled: false };
let pending: Promise<void> | null = null;
const listeners = new Set<() => void>();

function setState(next: SessionState) {
  state = next;
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

const SERVER_STATE: SessionState = { session: undefined, googleEnabled: false };

/**
 * The session the API reports. An error answer means signed out. An
 * unreachable API or an unreadable answer also renders as a guest, but keeps
 * the last known Google setting; the next action asks again.
 */
const loadSession: Effect.Effect<SessionState, never, HttpClient.HttpClient> = apiRequest(
  SESSION_PATH,
  { schema: sessionResponseSchema },
).pipe(
  withFetchOptions({ cache: "no-store" }),
  Effect.match({
    onSuccess: (body) => ({
      session: body.user ? { user: body.user } : null,
      googleEnabled: body.google_enabled,
    }),
    onFailure: (error) => ({
      session: null,
      googleEnabled: error.error.kind === "http" ? false : state.googleEnabled,
    }),
  }),
);

/** Ask the API who is signed in. Concurrent callers share one request. */
export function refreshSession(): Promise<void> {
  pending ??= runApi(loadSession)
    .then(setState)
    .finally(() => {
      pending = null;
    });
  return pending;
}

function useSession() {
  const snapshot = useSyncExternalStore(subscribe, () => state, () => SERVER_STATE);
  useEffect(() => {
    if (state.session === undefined) void refreshSession();
  }, []);
  return {
    data: snapshot.session ?? null,
    isPending: snapshot.session === undefined,
    googleEnabled: snapshot.googleEnabled,
    refetch: refreshSession,
  };
}

/**
 * POST to an auth route. An error answer resolves to an `AuthError`; only an
 * unreachable API rejects, so the screens can show their network message.
 */
const post = (path: string, body?: unknown): Promise<AuthResult> =>
  runApi(
    send(makeRequest(path, { method: "POST", body })).pipe(
      Effect.flatMap((response) =>
        response.status >= 200 && response.status < 300
          ? Effect.succeed<AuthResult>({ error: null })
          : readBody(response).pipe(Effect.map((payload) => toResult(response.status, payload))),
      ),
    ),
  );

/** An error answer as an `AuthResult`. An empty or non-JSON body still has a status. */
const toResult = (status: number, payload: unknown): AuthResult => {
  const detail =
    typeof payload === "object" && payload !== null && "detail" in payload
      ? payload.detail
      : undefined;
  const message = typeof detail === "string" ? detail : undefined;
  return { error: { status, code: codeFor(status, message), message } };
};

/** Stable codes for the answers the screens branch on. */
function codeFor(status: number, message: string | undefined): string | undefined {
  if (status === 403) return "EMAIL_NOT_VERIFIED";
  if (status === 409) return "USER_ALREADY_EXISTS";
  if (status === 400 && message === "INVALID_TOKEN") return "INVALID_TOKEN";
  return undefined;
}

export const authClient = {
  useSession,

  signIn: {
    async email(input: { email: string; password: string }): Promise<AuthResult> {
      const result = await post("/api/v1/auth/login", input);
      if (!result.error) await refreshSession();
      return result;
    },

    /** Leaves the page for Google; comes back to /login signed in, or with ?error=google. */
    async social({ provider }: { provider: "google" }): Promise<AuthResult> {
      if (state.session === undefined) await refreshSession();
      if (!state.googleEnabled) {
        return { error: { status: 404, code: "PROVIDER_NOT_FOUND", message: "Provider not found" } };
      }
      // A full page load, not router.push: the API answers with a redirect to Google.
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination
      window.location.href = `/api/v1/auth/${provider}/start`;
      return { error: null };
    },
  },

  signUp: {
    /** Creates the account and emails a verification link. It does not sign in. */
    async email(input: { name: string; email: string; password: string }): Promise<AuthResult> {
      return post("/api/v1/auth/register", input);
    },
  },

  async signOut(): Promise<AuthResult> {
    const result = await post("/api/v1/auth/logout");
    setState({ session: null, googleEnabled: state.googleEnabled });
    return result;
  },

  async sendVerificationEmail(input: { email: string }): Promise<AuthResult> {
    return post("/api/v1/auth/verification-email", input);
  },

  async requestPasswordReset(input: { email: string }): Promise<AuthResult> {
    return post("/api/v1/auth/forgot-password", input);
  },

  async resetPassword(input: { newPassword: string; token: string }): Promise<AuthResult> {
    return post("/api/v1/auth/reset-password", {
      token: input.token,
      password: input.newPassword,
    });
  },
};
