import { cn } from '@/lib/utils';
import type { BuildLasoResponse } from '@/lib/api/schemas';
import type { BirthInput } from '@/store/chart-store';
import { diaChiHourLabel } from '@/features/birth-input/schema';

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
  if (input.calendar === 'lunar') {
    const leap = input.is_leap_month ? ' nhuận' : '';
    return `${dd}.${mm}${leap}.${input.year} âm · giờ ${diaChiHourLabel(input.hour_in_dia_chi)}`;
  }
  const hh = (input.hour ?? 0).toString().padStart(2, '0');
  return `${dd}.${mm}.${input.year} dương · ${hh}:00`;
}

export function PersonalInfo({ response, input, className, variant = 'compact' }: Props) {
  const birth = formatBirth(input);
  const isFull = variant === 'full';
  return (
    <div className={cn(
      'flex flex-col justify-center gap-1 overflow-hidden p-3',
      !isFull && 'cc-personal-info col-start-2 row-start-2 col-span-2 row-span-2 bg-card',
      className,
    )}>
      <div className={cn('uppercase tracking-wide text-muted-foreground', isFull ? 'fc-info-label' : 'cc-info-label')}>
        Lá số tử vi
      </div>
      {input?.name && (
        <div className={cn('leading-tight font-medium', isFull ? 'fc-info-name' : 'cc-info-name')}>
          {input.name}
        </div>
      )}
      {birth && (
        <div className={cn('leading-snug text-muted-foreground', isFull ? 'fc-info-value' : 'cc-info-value')}>
          {birth}
        </div>
      )}
      <div className="my-1 h-px bg-border" />
      <Row k="Bản mệnh" v={response.ban_menh_name} isFull={isFull} />
      <Row k="Cục mệnh" v={response.cuc_name} isFull={isFull} />
      <Row k="Quan hệ" v={response.menh_cuc_relation_label} isFull={isFull} />
    </div>
  );
}

function Row({ k, v, isFull }: { k: string; v: string; isFull: boolean }) {
  return (
    <div className="flex flex-col leading-snug">
      <span className={cn('uppercase tracking-wide whitespace-nowrap text-muted-foreground', isFull ? 'fc-info-label' : 'cc-info-label')}>
        {k}
      </span>
      <span className={cn('text-foreground', isFull ? 'fc-info-value' : 'cc-info-value')}>{v}</span>
    </div>
  );
}
