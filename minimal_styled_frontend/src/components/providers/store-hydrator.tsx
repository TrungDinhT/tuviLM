'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useChartStore } from '@/store/chart-store';

/**
 * Gates render on the Zustand persist hydration completing. Prevents a flash
 * of the default (null) store state on first paint and avoids SSR/CSR
 * hydration mismatches for client components that read persisted slices.
 */
export function StoreHydrator({ children }: { children: ReactNode }) {
  const [hydrated, setHydrated] = useState(() => useChartStore.persist.hasHydrated());

  useEffect(() => {
    if (hydrated) return;
    return useChartStore.persist.onFinishHydration(() => setHydrated(true));
  }, [hydrated]);

  if (!hydrated) return null;
  return <>{children}</>;
}
