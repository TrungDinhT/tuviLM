"use client";

import { useEffect, useRef } from "react";

import { cn } from "@/lib/utils";

/** One option's height; the spacers center the first/last option. Keep in
 * sync with the classes below. */
const ROW_PX = 46;
const SPACER_PX = 55;

interface WheelPickerProps {
  /** Column label, e.g. "Ngày". */
  label: string;
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
  /** Zero-pad single digits, per the design's day/month columns. */
  pad?: boolean;
}

/**
 * A scroll-snap wheel column from the casting machine. Scrolling settles onto
 * an option (mandatory snap); the value commits after a short settle delay so
 * a fast flick does not fire one change per passed row.
 */
export function WheelPicker({ label, min, max, value, onChange, pad = false }: WheelPickerProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const settleTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const options = Array.from({ length: max - min + 1 }, (_, i) => min + i);

  // Position the wheel on mount and whenever the value is set from outside.
  useEffect(() => {
    const el = scrollRef.current;
    if (el === null) return;
    const target = (value - min) * ROW_PX;
    if (Math.abs(el.scrollTop - target) > 1) el.scrollTop = target;
  }, [value, min]);

  useEffect(() => {
    return () => {
      if (settleTimer.current !== null) clearTimeout(settleTimer.current);
    };
  }, []);

  const handleScroll = () => {
    if (settleTimer.current !== null) clearTimeout(settleTimer.current);
    settleTimer.current = setTimeout(() => {
      const el = scrollRef.current;
      if (el === null) return;
      const index = Math.round(el.scrollTop / ROW_PX);
      const clamped = Math.max(0, Math.min(options.length - 1, index));
      const next = options[clamped];
      if (next !== undefined && next !== value) onChange(next);
    }, 120);
  };

  return (
    <div className="relative">
      <div className="mb-[6px] text-center text-[11px] tracking-[0.24em] text-muted uppercase">
        {label}
      </div>
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        role="listbox"
        aria-label={label}
        aria-activedescendant={`picker-${label}-${value}`}
        className="[mask-image:linear-gradient(180deg,transparent,#000_26%,#000_74%,transparent)] h-[156px] snap-y snap-mandatory overflow-y-scroll"
      >
        <div style={{ height: SPACER_PX }} aria-hidden="true" />
        {options.map((option) => (
          <div
            key={option}
            id={`picker-${label}-${option}`}
            role="option"
            aria-selected={option === value}
            onClick={() => {
              scrollRef.current?.scrollTo({
                top: (option - min) * ROW_PX,
                behavior: "smooth",
              });
            }}
            className={cn(
              "flex snap-center items-center justify-center font-display text-[24px] font-medium",
              "cursor-pointer text-muted transition-[color,transform] duration-200",
              option === value &&
                cn("bg-[linear-gradient(115deg,var(--accent),var(--accent-2))] bg-clip-text text-transparent", "scale-[1.06]"),
            )}
            style={{ height: ROW_PX }}
          >
            {pad && option < 10 ? `0${option}` : option}
          </div>
        ))}
        <div style={{ height: SPACER_PX }} aria-hidden="true" />
      </div>
    </div>
  );
}
