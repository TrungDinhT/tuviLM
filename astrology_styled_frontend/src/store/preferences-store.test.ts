import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { MUTE_BIRTH_CONFIRM_KEY, usePreferencesStore } from "./preferences-store";

const real = globalThis.localStorage;

function restoreStorage() {
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    writable: true,
    value: real,
  });
}

beforeEach(() => {
  restoreStorage();
  localStorage.clear();
  usePreferencesStore.setState({ muteBirthConfirm: false });
});

afterEach(restoreStorage);

describe("birth confirmation mute preference", () => {
  it("defaults to asking", () => {
    expect(usePreferencesStore.getState().muteBirthConfirm).toBe(false);
  });

  it("persists under the documented key", () => {
    usePreferencesStore.getState().setMuteBirthConfirm(true);

    const raw = localStorage.getItem(MUTE_BIRTH_CONFIRM_KEY);
    expect(raw).not.toBeNull();
    expect(JSON.parse(raw!)).toMatchObject({ state: { muteBirthConfirm: true } });
  });

  it("restores a value written by a previous session", async () => {
    // Write storage directly rather than via setState: on a persisted store
    // every setState also writes, so clearing in memory would clear storage
    // too and the test would prove nothing.
    localStorage.setItem(
      MUTE_BIRTH_CONFIRM_KEY,
      JSON.stringify({ state: { muteBirthConfirm: true }, version: 0 }),
    );

    await usePreferencesStore.persist.rehydrate();

    expect(usePreferencesStore.getState().muteBirthConfirm).toBe(true);
  });

  it("keeps asking when storage is blocked, and never throws", async () => {
    usePreferencesStore.getState().setMuteBirthConfirm(true);

    Object.defineProperty(globalThis, "localStorage", {
      configurable: true,
      get() {
        throw new DOMException("Access is denied for this document.", "SecurityError");
      },
    });

    usePreferencesStore.setState({ muteBirthConfirm: false });
    await expect(usePreferencesStore.persist.rehydrate()).resolves.not.toThrow();

    // Blocked storage reads as "no preference stored", so the confirmation
    // still appears — the flow completes rather than failing.
    expect(usePreferencesStore.getState().muteBirthConfirm).toBe(false);
    expect(() => usePreferencesStore.getState().setMuteBirthConfirm(true)).not.toThrow();
  });
});
