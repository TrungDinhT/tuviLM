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
  onChange: (minute: number) => void;
  id?: string;
  className?: string;
  placeholder?: string;
  /** Step between minute options. Defaults to 5; common alt values are 1 and 15. */
  step?: 1 | 5 | 15;
}

function pad(n: number): string {
  return n.toString().padStart(2, '0');
}

export function MinuteSelect({
  value,
  onChange,
  id,
  className,
  placeholder = '--',
  step = 5,
}: Props) {
  const options = Array.from({ length: Math.ceil(60 / step) }, (_, i) => i * step);

  return (
    <Select
      value={value === undefined ? undefined : value.toString()}
      onValueChange={(v) => onChange(Number(v))}
    >
      <SelectTrigger id={id} className={cn('h-9 w-full', className)}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {options.map((m) => (
          <SelectItem key={m} value={m.toString()}>
            {pad(m)}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
