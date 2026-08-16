import { safeStorage } from "@/lib/safe-storage";

export const OWNER_ID_KEY = "tuvi.ownerId";

/**
 * The anonymous owner identity every owner-scoped request carries.
 *
 * `POST /api/v1/anonymous` mints a *new* id on every call, so a race between
 * two first requests would strand chart profiles and sessions under separate
 * identities. The in-flight promise is shared: whoever asks first starts the
 * request, everyone else awaits the same one.
 */
let inFlight: Promise<string> | null = null;

function readStoredOwnerId(): string | null {
  return safeStorage.getItem(OWNER_ID_KEY);
}

function storeOwnerId(ownerId: string): void {
  safeStorage.setItem(OWNER_ID_KEY, ownerId);
}

/** Test seam: forget the cached in-flight request. */
export function resetOwnerIdCache(): void {
  inFlight = null;
}

export async function getOwnerId(mint: () => Promise<string>): Promise<string> {
  const stored = readStoredOwnerId();
  if (stored !== null && stored !== "") return stored;

  inFlight ??= mint()
    .then((ownerId) => {
      storeOwnerId(ownerId);
      return ownerId;
    })
    .finally(() => {
      // Clear either way: a failure must not poison every later attempt.
      inFlight = null;
    });

  return inFlight;
}
