import { cn } from '@/lib/utils';
import type { BuildLasoResponse } from '@/lib/api/schemas';
import type { BirthInput } from '@/store/chart-store';

interface Props {
  response: BuildLasoResponse;
  input: BirthInput | null;
  className?: string;
  variant?: 'compact' | 'full';
}

function formatBirth(input: BirthInput | null): string | null {
  if (!input) return null;
  const dd = input.date.toString().padStart(2, '0');
  const mm = input.month.toString().padStart(2, '0');
  const hh = input.hour.toString().padStart(2, '0');
  return `${dd}.${mm}.${input.year} · ${hh}:00`;
}

export function PersonalInfo({ response, input, className, variant = 'compact' }: Props) {
  const birth = formatBirth(input);
  const isFull = variant === 'full';
  return (
    <div className={cn(
      'flex flex-col justify-center gap-1 overflow-hidden p-3',
      !isFull && 'col-start-2 row-start-2 col-span-2 row-span-2 bg-card',
      className,
    )}>
      <div className="text-[10px] uppercase tracking-wide text-muted-foreground">Lá số tử vi</div>
      {input?.name && (
        <div className="text-sm leading-tight font-medium">{input.name}</div>
      )}
      {birth && (
        <div className="text-[11px] leading-snug text-muted-foreground">{birth}</div>
      )}
      <div className="my-1 h-px bg-border" />
      <Row k="Bản mệnh" v={response.ban_menh_name} />
      <Row k="Cục mệnh" v={response.cuc_name} />
      <Row k="Quan hệ" v={response.menh_cuc_relation_label} />
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex flex-col leading-snug">
      <span className="text-[9px] uppercase tracking-wide whitespace-nowrap text-muted-foreground">
        {k}
      </span>
      <span className="text-[11px] text-foreground">{v}</span>
    </div>
  );
}
