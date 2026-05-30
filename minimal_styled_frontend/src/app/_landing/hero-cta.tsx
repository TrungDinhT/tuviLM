import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function HeroCta() {
  return (
    <Button asChild size="lg">
      <a href="#b-date">
        An lá số ngay <ArrowRight className="size-4" />
      </a>
    </Button>
  );
}
