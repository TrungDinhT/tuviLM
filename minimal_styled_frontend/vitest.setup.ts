import '@testing-library/jest-dom/vitest';

if (typeof window !== 'undefined' && typeof globalThis.localStorage?.clear !== 'function') {
  const store = new Map<string, string>();
  Object.defineProperty(globalThis, 'localStorage', {
    value: {
      clear: () => store.clear(),
      getItem: (key: string) => store.get(key) ?? null,
      removeItem: (key: string) => store.delete(key),
      setItem: (key: string, value: string) => store.set(key, value),
    },
    configurable: true,
  });
}
