'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useChartStore } from '@/store/chart-store';

/**
 * Gates render on the Zustand persist hydration completing. Prevents a flash
 * of the default (null) store state on first paint and avoids SSR/CSR
 * hydration mismatches for client components that read persisted slices.
 */
export function StoreHydrator({ children }: { children: ReactNode }) {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (useChartStore.persist.hasHydrated()) {
      // Set once on mount when hydration already finished before this effect ran.
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setHydrated(true);
      return;
    }
    return useChartStore.persist.onFinishHydration(() => setHydrated(true));
  }, []);

  if (!hydrated) return null;
  return <>{children}</>;
}
