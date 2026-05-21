'use client';

import { cn } from '@/lib/utils';
import type { Cung } from '@/lib/api/schemas';

interface Props {
  cung: Cung;
  saoLuu?: Cung['saoLuu'];
  selected?: boolean;
  onClick?: () => void;
  style?: React.CSSProperties;
  variant?: 'compact' | 'full';
}

export function CungCell({ cung, saoLuu, selected, onClick, style, variant = 'compact' }: Props) {
  const isFull = variant === 'full';
  return (
    <button
      type="button"
      onClick={onClick}
      style={style}
      className={cn(
        'flex min-w-0 flex-col gap-1 overflow-hidden bg-card p-2 text-left',
        selected && 'ring-2 ring-inset ring-primary',
        isFull && cung.is_cung_than && !selected && 'ring-1 ring-inset ring-primary/40',
      )}
    >
      {isFull && (
        <div className="flex items-start justify-between gap-1">
          <span className="flex items-center gap-1 text-[9px] leading-none text-muted-foreground">
            {cung.is_tuan && <span className="font-medium text-destructive">T</span>}
            {cung.is_triet && <span className="font-medium text-destructive">Tr</span>}
            <span className="whitespace-nowrap">{cung.trang_sinh ?? ''}</span>
          </span>
          {typeof cung.age_daivan === 'number' && (
            <span className="text-[9px] leading-none text-muted-foreground tabular-nums">
              {cung.age_daivan}
            </span>
          )}
        </div>
      )}

      <div className="text-[10px] leading-tight font-medium text-primary">{cung.position}</div>

      {isFull && cung.role && (
        <div className="text-[9px] uppercase tracking-wide leading-none text-muted-foreground">
          {cung.role}
        </div>
      )}

      {cung.chinh_tinh.length > 0 && (
        <div className="mt-0.5 flex flex-col gap-0.5 text-center">
          {cung.chinh_tinh.map((star) => (
            <div
              key={star}
              className="leading-tight font-medium text-foreground"
              style={{ fontSize: '10px' }}
            >
              {star}
            </div>
          ))}
        </div>
      )}

      {isFull && cung.tuhoa.length > 0 && (
        <div className="flex flex-wrap gap-1 text-[9px] text-secondary">
          {cung.tuhoa.map((t) => (
            <span key={t}>{t}</span>
          ))}
        </div>
      )}

      {isFull && cung.phu_tinh.length > 0 && (
        <div className="flex flex-wrap gap-x-1 gap-y-0.5 text-[9px] leading-tight text-muted-foreground">
          {cung.phu_tinh.map((s) => (
            <span key={s.name}>{s.display}</span>
          ))}
        </div>
      )}

      {isFull && saoLuu && saoLuu.length > 0 && (
        <div className="mt-auto flex flex-wrap gap-x-1 border-t border-border pt-1 text-[9px] text-muted-foreground">
          {saoLuu.map((s) => (
            <span key={s.name}>{s.display}</span>
          ))}
        </div>
      )}
    </button>
  );
}
