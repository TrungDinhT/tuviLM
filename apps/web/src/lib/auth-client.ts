import { useEffect, useSyncExternalStore } from "react";

/**
 * Login, through the FastAPI routes under `/api/v1/auth`.
 *
 * The session is an httpOnly cookie that the API sets; the browser sends it
 * with every same-origin `/api` request, so no token is handled here. This
 * module only keeps who is signed in, for rendering.
 *
 * The session lives in a small store outside TanStack Query on purpose: the
 * query client is created per account (see QueryProvider), so it cannot hold
 * the value that decides which account that is.
 */

export interface SessionUser {
  id: string;
  email: string;
  name: string;
  role: "user" | "admin";
}

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

/** Ask the API who is signed in. Concurrent callers share one request. */
export function refreshSession(): Promise<void> {
  pending ??= (async () => {
    try {
      const response = await fetch(SESSION_PATH, { cache: "no-store" });
      const body = response.ok ? ((await response.json()) as SessionBody) : null;
      setState({
        session: body?.user ? { user: body.user } : null,
        googleEnabled: body?.google_enabled ?? false,
      });
    } catch {
      // Unreachable API: render as a guest; the next action asks again.
      setState({ session: null, googleEnabled: state.googleEnabled });
    } finally {
      pending = null;
    }
  })();
  return pending;
}

interface SessionBody {
  user: SessionUser | null;
  google_enabled: boolean;
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

async function post(path: string, body?: unknown): Promise<Response> {
  return fetch(path, {
    method: "POST",
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

async function toResult(response: Response): Promise<AuthResult> {
  if (response.ok) return { error: null };
  let detail: unknown = null;
  try {
    detail = ((await response.json()) as { detail?: unknown }).detail;
  } catch {
    // An empty or non-JSON body still has a status.
  }
  const message = typeof detail === "string" ? detail : undefined;
  return { error: { status: response.status, code: codeFor(response.status, message), message } };
}

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
      const result = await toResult(await post("/api/v1/auth/login", input));
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
      return toResult(await post("/api/v1/auth/register", input));
    },
  },

  async signOut(): Promise<AuthResult> {
    const result = await toResult(await post("/api/v1/auth/logout"));
    setState({ session: null, googleEnabled: state.googleEnabled });
    return result;
  },

  async sendVerificationEmail(input: { email: string }): Promise<AuthResult> {
    return toResult(await post("/api/v1/auth/verification-email", input));
  },

  async requestPasswordReset(input: { email: string }): Promise<AuthResult> {
    return toResult(await post("/api/v1/auth/forgot-password", input));
  },

  async resetPassword(input: { newPassword: string; token: string }): Promise<AuthResult> {
    return toResult(
      await post("/api/v1/auth/reset-password", {
        token: input.token,
        password: input.newPassword,
      }),
    );
  },
};
