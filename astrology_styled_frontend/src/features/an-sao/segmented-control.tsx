"use client";

import { cn } from "@/lib/utils";

interface SegmentedControlProps<T extends string> {
  label: string;
  options: readonly { value: T; label: string }[];
  value: T | null;
  onChange: (value: T) => void;
}

/**
 * A two-or-few-option segmented selector inside the casting machine — used
 * for giới tính (Nam/Nữ) and the AM/PM meridiem toggle. The active segment
 * carries the accent gradient, matching the clock's selected hour.
 */
export function SegmentedControl<T extends string>({
  label,
  options,
  value,
  onChange,
}: SegmentedControlProps<T>) {
  return (
    <div role="radiogroup" aria-label={label} className="grid grid-flow-col auto-cols-fr gap-2">
      {options.map((option) => {
        const active = option.value === value;
        return (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(option.value)}
            className={cn(
              "cursor-pointer rounded-full px-3 py-[9px] text-[13px] font-semibold",
              "transition-[background,color,box-shadow] duration-200",
              active
                ? "accent-gradient text-bg-0"
                : "glass text-muted hover:text-ink",
            )}
          >
            {option.label}
          </button>
        );
      })}
    </div>
  );
}
