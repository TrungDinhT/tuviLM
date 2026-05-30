'use client';

import { abbreviateStarStatus, cn } from '@/lib/utils';
import type { Cung } from '@/lib/api/schemas';

interface Props {
  cung: Cung;
  selected?: boolean;
  onClick?: () => void;
  style?: React.CSSProperties;
}

export function CungCellCompact({ cung, selected, onClick, style }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={style}
      className={cn(
        'flex min-w-0 flex-col gap-1 overflow-hidden bg-card p-1 text-left',
        selected && 'ring-2 ring-inset ring-primary',
      )}
    >
      <div className="text-[10px] leading-tight font-medium text-primary">
        {cung.position}
      </div>

      {cung.chinh_tinh.length > 0 && (
        <div className="mt-0.5 flex flex-col gap-0.5 text-center">
          {cung.chinh_tinh.map((star) => (
            <div
              key={star}
              className="leading-tight font-medium text-foreground"
              style={{ fontSize: '9px' }}
            >
              {abbreviateStarStatus(star)}
            </div>
          ))}
        </div>
      )}
    </button>
  );
}
