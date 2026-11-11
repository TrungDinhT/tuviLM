"use client";

import { useEffect, useState } from "react";

/**
 * A value that trails its source by `delayMs`, for keystroke- and dial-grade
 * inputs that should not fire work on every change. The trailing update is
 * scheduled, never synchronous, so render stays pure.
 */
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
