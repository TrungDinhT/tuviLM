import { Badge } from '@/components/ui/badge';

/**
 * Marks a UI region whose data is placeholder (not backed by the API).
 * Remove once the corresponding endpoint is implemented.
 */
export function DemoBadge() {
  return (
    <Badge variant="outline" className="text-[10px] uppercase tracking-wide">
      Demo
    </Badge>
  );
}
