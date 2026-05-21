'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { Calendar as CalendarIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { cn } from '@/lib/utils';

interface Props {
  value: Date | undefined;
  onChange: (date: Date | undefined) => void;
  id?: string;
  placeholder?: string;
  className?: string;
}

const START_MONTH = new Date(1900, 0, 1);
const END_MONTH = new Date(2099, 11, 31);
const DEFAULT_MONTH = new Date(1990, 0, 1);

export function DateInput({
  value,
  onChange,
  id,
  placeholder = 'dd/mm/yyyy',
  className,
}: Props) {
  const [open, setOpen] = useState(false);

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          id={id}
          type="button"
          variant="outline"
          className={cn(
            'h-9 w-full justify-start gap-2 px-3 font-normal',
            !value && 'text-muted-foreground',
            className,
          )}
        >
          <CalendarIcon className="size-4 opacity-70" />
          {value ? format(value, 'dd/MM/yyyy') : placeholder}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="single"
          selected={value}
          onSelect={(d) => {
            onChange(d);
            if (d) setOpen(false);
          }}
          captionLayout="dropdown"
          startMonth={START_MONTH}
          endMonth={END_MONTH}
          defaultMonth={value ?? DEFAULT_MONTH}
        />
      </PopoverContent>
    </Popover>
  );
}
