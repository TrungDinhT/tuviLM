"use client";

import { forwardRef, useRef, useState } from "react";

import { cn } from "@/lib/utils";

import { type Meridiem, canhGioOf } from "./birth-time";
import styles from "./time-picker.module.css";

/** Positions on the face; each step is 30°. */
const POSITIONS = 12;
/** Horizontal drag distance that advances one hour. */
const DRAG_STEP_PX = 22;
/** What the face shows before the user has picked anything. */
const DEFAULT_HOUR12 = 12;

function wrap(index: number): number {
  return ((index % POSITIONS) + POSITIONS) % POSITIONS;
}

interface TimePickerProps {
  /** The committed hour, 1–12; null until the face has been touched. */
  value: number | null;
  /** Owned by the parent so AM/PM can be picked before the hour is. */
  meridiem: Meridiem;
  onChange: (hour12: number) => void;
  /** Bumped by the parent to replay the "required" pulse (missing-time guard). */
  pulseKey: number;
}

/**
 * The birth-time picker: one clock face for the hour, wound by swiping left
 * and right. A tap on the ring jumps to the number under the finger and arrow
 * keys step one hour, since the face is a slider.
 *
 * There is no minute face — see `birth-time.ts` for why the hour alone decides
 * the reading. The AM/PM toggle sits above, in the parent.
 *
 * Complex surfaces live in time-picker.module.css (`clockFace` and friends) —
 * here there is only layout and state.
 */
export const TimePicker = forwardRef<HTMLDivElement, TimePickerProps>(function TimePicker(
  { value, meridiem, onChange, pulseKey },
  ref,
) {
  const [handAngle, setHandAngle] = useState(0);
  const [dragging, setDragging] = useState(false);
  const faceRef = useRef<HTMLDivElement>(null);
  const drag = useRef<{
    id: number;
    startX: number;
    startY: number;
    startIndex: number;
    moved: boolean;
  } | null>(null);

  const hour12 = value ?? DEFAULT_HOUR12;
  const index = hour12 % POSITIONS;
  const canhGio = value === null ? null : canhGioOf(hour12, meridiem);

  const select = (next: number) => {
    const wrapped = wrap(next);
    // Wind along the shortest arc, accumulating so the hand never rewinds.
    const target = wrapped * 30;
    setHandAngle((current) => current + ((((target - current) % 360) + 540) % 360) - 180);
    onChange(wrapped === 0 ? 12 : wrapped);
  };

  /** The position under the pointer, or null inside the readout. */
  const indexAtPointer = (event: React.PointerEvent): number | null => {
    const face = faceRef.current;
    if (face === null) return null;
    const rect = face.getBoundingClientRect();
    const x = event.clientX - rect.left - rect.width / 2;
    const y = event.clientY - rect.top - rect.height / 2;
    if (Math.hypot(x, y) < rect.width * 0.24) return null;
    return Math.round((Math.atan2(x, -y) * 6) / Math.PI);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    let next: number | null = null;
    if (event.key === "ArrowRight" || event.key === "ArrowUp") next = index + 1;
    if (event.key === "ArrowLeft" || event.key === "ArrowDown") next = index - 1;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = POSITIONS - 1;
    if (next === null) return;
    event.preventDefault();
    select(next);
  };

  const valueText =
    value === null || canhGio === null
      ? "Chưa chọn giờ sinh"
      : `${hour12} giờ ${meridiem}, giờ ${canhGio.chi}`;

  return (
    <div ref={ref}>
      <div className="relative mt-[10px]">
        {/* Replayable required-pulse: remounting the ring restarts the animation
            without touching the picker's own state. */}
        {pulseKey > 0 ? (
          <span
            key={pulseKey}
            aria-hidden="true"
            className={`${styles.needRing} pointer-events-none absolute inset-0 z-10 mx-auto aspect-square w-[min(218px,66vw)] rounded-full`}
          />
        ) : null}

        <div
          ref={faceRef}
          role="slider"
          tabIndex={0}
          aria-label="Giờ sinh"
          aria-valuemin={0}
          aria-valuemax={POSITIONS - 1}
          aria-valuenow={index}
          aria-valuetext={valueText}
          onPointerDown={(event) => {
            if (event.pointerType === "mouse" && event.button !== 0) return;
            drag.current = {
              id: event.pointerId,
              startX: event.clientX,
              startY: event.clientY,
              startIndex: index,
              moved: false,
            };
            event.currentTarget.setPointerCapture(event.pointerId);
          }}
          onPointerMove={(event) => {
            const active = drag.current;
            if (active === null || event.pointerId !== active.id) return;
            const dx = event.clientX - active.startX;
            const dy = event.clientY - active.startY;
            if (!active.moved && Math.hypot(dx, dy) <= 6) return;
            active.moved = true;
            setDragging(true);
            const next = wrap(active.startIndex + Math.round(dx / DRAG_STEP_PX));
            if (next !== index) select(next);
          }}
          onPointerUp={(event) => {
            const active = drag.current;
            if (active === null || event.pointerId !== active.id) return;
            if (!active.moved) {
              const tapped = indexAtPointer(event);
              if (tapped !== null) select(tapped);
            }
            drag.current = null;
            setDragging(false);
          }}
          onPointerCancel={() => {
            drag.current = null;
            setDragging(false);
          }}
          onKeyDown={handleKeyDown}
          className={cn(
            "relative mx-auto aspect-square w-[min(218px,66vw)]",
            "cursor-grab touch-none rounded-full outline-none select-none",
            "focus-visible:shadow-[0_0_0_2px_var(--accent-glow)]",
            dragging && "cursor-grabbing",
          )}
        >
          {/* Face, rings and ticks */}
          <div aria-hidden="true" className={`${styles.clockFace} absolute inset-0 rounded-full`} />
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-[4px] rounded-full bg-[repeating-conic-gradient(from_-1deg,rgba(243,239,250,0.34)_0_1.5deg,transparent_1.5deg_30deg)] [mask:radial-gradient(circle,transparent_0_88%,#000_88%_94%,transparent_94%)]"
          />

          {/* Hand */}
          <div
            aria-hidden="true"
            style={{ transform: `rotate(${handAngle}deg)` }}
            className={cn(
              `${styles.clockHand} pointer-events-none absolute bottom-1/2 left-[calc(50%-1px)] z-2 h-[31%] w-[2px] origin-bottom rounded-sm`,
              dragging
                ? "transition-none"
                : "transition-[transform,opacity] duration-[240ms] ease-[cubic-bezier(.2,.8,.2,1)]",
              value === null ? "opacity-30" : "opacity-100",
            )}
          />

          {/* The twelve hours */}
          {Array.from({ length: POSITIONS }, (_, position) => {
            const angle = (position * Math.PI) / 6;
            const x = 50 + Math.sin(angle) * 39;
            const y = 50 - Math.cos(angle) * 39;
            const active = value !== null && position === index;
            return (
              <span
                key={position}
                aria-hidden="true"
                style={{ left: `${x.toFixed(2)}%`, top: `${y.toFixed(2)}%` }}
                className={cn(
                  "pointer-events-none absolute z-4 flex h-[34px] w-[34px] -translate-x-1/2 -translate-y-1/2",
                  "items-center justify-center rounded-full font-display text-[13px] font-semibold text-muted",
                  "transition-[color,background,box-shadow,transform] duration-200",
                  active &&
                    cn(
                      "bg-[linear-gradient(135deg,var(--accent-2),var(--accent))] text-bg-0 shadow-[0_0_16px_var(--accent-glow)]",
                      "scale-[1.08]",
                    ),
                )}
              >
                {position === 0 ? 12 : position}
              </span>
            );
          })}

          {/* Pin + readout */}
          <span
            aria-hidden="true"
            className="pointer-events-none absolute top-1/2 left-1/2 z-5 h-[12px] w-[12px] -translate-x-1/2 -translate-y-1/2 rounded-full border-[3px] border-bg-2 bg-accent shadow-[0_0_13px_var(--accent-glow)]"
          />
          <span
            aria-hidden="true"
            className="pointer-events-none absolute top-1/2 left-1/2 z-3 flex w-[104px] -translate-x-1/2 -translate-y-1/2 flex-col items-center text-center"
          >
            <strong
              className={cn(
                "font-display text-[20px] leading-[1.1] font-semibold",
                value === null ? "text-ink" : "text-accent [text-shadow:0_0_12px_var(--accent-glow)]",
              )}
            >
              {value === null ? "Chọn giờ" : `${hour12} ${meridiem}`}
            </strong>
            <span className="mt-[4px] text-[9px] leading-[1.25] whitespace-nowrap text-muted">
              {canhGio === null ? "--" : `Giờ ${canhGio.chi}`}
            </span>
            {canhGio !== null ? (
              <span className="text-[9px] leading-[1.25] whitespace-nowrap text-muted">
                {canhGio.range}
              </span>
            ) : null}
          </span>
        </div>
      </div>

      <div className="mt-[8px] text-center text-[11px] text-muted">
        Vuốt trái phải để chọn giờ sinh
      </div>
    </div>
  );
});
