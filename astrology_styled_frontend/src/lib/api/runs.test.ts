import { afterEach, beforeEach, expect, it, vi } from "vitest";

import { OWNER_ID_KEY, resetOwnerIdCache } from "./owner";
import { getRun } from "./runs";

beforeEach(() => {
  localStorage.clear();
  resetOwnerIdCache();
  localStorage.setItem(OWNER_ID_KEY, "owner");
});
afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

it("bounds a stalled HTTP request so Query can retry it", async () => {
  const timeout = new AbortController();
  vi.spyOn(AbortSignal, "timeout").mockReturnValueOnce(timeout.signal);
  const fetchMock = vi.fn(
    (_url, init) =>
      new Promise<Response>((_resolve, reject) => {
        init.signal.addEventListener("abort", () => reject(init.signal.reason));
      }),
  );
  vi.stubGlobal("fetch", fetchMock);
  const pending = getRun("r1");
  const assertion = expect(pending).rejects.toMatchObject({ error: { kind: "network" } });
  await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
  timeout.abort(new DOMException("timed out", "TimeoutError"));
  await assertion;
});
