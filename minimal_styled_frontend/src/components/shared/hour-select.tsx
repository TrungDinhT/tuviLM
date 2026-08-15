'use client';

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { cn } from '@/lib/utils';

interface Props {
  value: number | undefined;
  onChange: (hour: number) => void;
  id?: string;
  className?: string;
  placeholder?: string;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);

function formatHour(h: number): string {
  return h.toString();
}

export function HourSelect({ value, onChange, id, className, placeholder = '--' }: Props) {
  return (
    <Select
      value={value === undefined ? undefined : value.toString()}
      onValueChange={(v) => onChange(Number(v))}
    >
      <SelectTrigger id={id} className={cn('h-9 w-full', className)}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {HOURS.map((h) => (
          <SelectItem key={h} value={h.toString()}>
            {formatHour(h)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
