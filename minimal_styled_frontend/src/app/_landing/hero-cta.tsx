'use client';

import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

function isInViewport(el: HTMLElement): boolean {
  const rect = el.getBoundingClientRect();
  return rect.top >= 0 && rect.bottom <= (window.innerHeight || document.documentElement.clientHeight);
}

export function HeroCta() {
  return (
    <Button
      type="button"
      size="lg"
      onClick={() => {
        const target = document.getElementById('b-date');
        if (!(target instanceof HTMLElement)) return;
        target.focus({ preventScroll: true });
        if (!isInViewport(target)) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }}
    >
      An lá số ngay <ArrowRight className="size-4" />
    </Button>
  );
}
