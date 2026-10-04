import { beforeEach, describe, expect, it, vi } from "vitest";

import { getOwnerId, OWNER_ID_KEY, resetOwnerIdCache } from "./owner";

beforeEach(() => {
  localStorage.clear();
  resetOwnerIdCache();
});

describe("legacy anonymous identity", () => {
  it("returns the stored owner id without minting a new one", async () => {
    localStorage.setItem(OWNER_ID_KEY, "anon_stored");
    const mint = vi.fn();

    expect(await getOwnerId(mint)).toBe("anon_stored");
    expect(mint).not.toHaveBeenCalled();
  });

  it("mints exactly one owner id when two first requests race", async () => {
    const mint = vi.fn().mockResolvedValue("anon_shared");

    expect(await Promise.all([getOwnerId(mint), getOwnerId(mint)])).toEqual([
      "anon_shared",
      "anon_shared",
    ]);
    expect(mint).toHaveBeenCalledTimes(1);
    expect(localStorage.getItem(OWNER_ID_KEY)).toBe("anon_shared");
  });

  it("does not poison later attempts when minting fails", async () => {
    const failure = new Error("Mint failed");
    const mint = vi.fn().mockRejectedValueOnce(failure).mockResolvedValueOnce("anon_second");

    await expect(getOwnerId(mint)).rejects.toBe(failure);
    expect(await getOwnerId(mint)).toBe("anon_second");
    expect(localStorage.getItem(OWNER_ID_KEY)).toBe("anon_second");
  });
});
