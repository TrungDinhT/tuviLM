import { afterEach, describe, expect, it, vi } from "vitest";

import { safeStorage } from "./safe-storage";

const real = globalThis.localStorage;

function breakStorage() {
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    get() {
      throw new DOMException("Access is denied for this document.", "SecurityError");
    },
  });
}

afterEach(() => {
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    writable: true,
    value: real,
  });
  vi.restoreAllMocks();
});

describe("safeStorage", () => {
  it("round-trips a value when storage works", () => {
    safeStorage.setItem("k", "v");
    expect(safeStorage.getItem("k")).toBe("v");
    safeStorage.removeItem("k");
    expect(safeStorage.getItem("k")).toBeNull();
  });

  it("reads as 'nothing stored' when storage throws", () => {
    breakStorage();
    expect(() => safeStorage.getItem("tuvi.muteBirthConfirm")).not.toThrow();
    expect(safeStorage.getItem("tuvi.muteBirthConfirm")).toBeNull();
  });

  it("swallows write failures instead of breaking the flow", () => {
    breakStorage();
    expect(() => safeStorage.setItem("tuvi.muteBirthConfirm", "1")).not.toThrow();
    expect(() => safeStorage.removeItem("tuvi.muteBirthConfirm")).not.toThrow();
  });

  it("swallows a quota error on write", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("QuotaExceededError", "QuotaExceededError");
    });
    expect(() => safeStorage.setItem("k", "v")).not.toThrow();
  });
});
