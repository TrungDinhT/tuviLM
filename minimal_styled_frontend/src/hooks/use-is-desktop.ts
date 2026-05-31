import { useEffect, useState } from 'react';

const LG_MQ = '(min-width: 1024px)';

export function useIsDesktop() {
  const [isDesktop, setIsDesktop] = useState(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia(LG_MQ).matches;
  });

  useEffect(() => {
    const mq = window.matchMedia(LG_MQ);
    const handler = (e: MediaQueryListEvent) => setIsDesktop(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  return isDesktop;
}
