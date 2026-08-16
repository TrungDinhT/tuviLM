"use client";

import { useEffect, useState } from "react";

const LOAD_SUBS = [
  "Nghê Sao đang đọc vị trí các vì tinh tú…",
  "Đang xếp 12 cung mệnh của bạn…",
  "Chòm sao bản mệnh đang dần hiện hình…",
] as const;

const SUB_INTERVAL_MS = 900;

/** The Nghê Sao star-spirit, ported from the prototype's mascotSVG. */
function Mascot({ size }: { size: number }) {
  return (
    <svg viewBox="0 0 120 120" width={size} height={size} style={{ overflow: "visible" }}>
      <g
        fill="none"
        stroke="var(--accent)"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ filter: "drop-shadow(0 0 8px var(--accent-glow))" }}
      >
        <path
          d="M30 86 C24 66 34 52 50 50 C40 40 44 26 58 24 C54 32 60 38 68 36 C66 30 72 24 80 26 C76 32 80 38 86 40"
          opacity=".9"
        />
        <path
          d="M50 50 C64 48 78 56 84 70 C88 80 84 92 74 96 C80 86 74 74 64 74 C70 82 64 92 54 90"
          opacity=".9"
        />
        <path d="M30 86 C36 90 46 92 54 90" />
        <path d="M80 26 C86 22 92 24 94 30" opacity=".8" />
        <path d="M86 40 C92 40 96 44 96 50" opacity=".7" />
      </g>
      <g fill="var(--accent)" style={{ filter: "drop-shadow(0 0 6px var(--accent-glow))" }}>
        <circle cx="82" cy="34" r="2.6" />
        <circle cx="50" cy="50" r="2.4" />
        <circle cx="64" cy="74" r="2.2" />
        <circle cx="30" cy="86" r="2.2" />
        <circle cx="94" cy="30" r="1.8" />
        <circle cx="86" cy="40" r="1.6" />
        <circle cx="74" cy="96" r="1.8" />
      </g>
      <circle cx="82" cy="34" r="5.5" fill="none" stroke="var(--accent)" strokeWidth="1" opacity=".5" />
    </svg>
  );
}

/**
 * The "đang luận giải" interlude while the build mutation is in flight. The
 * caller guarantees the ~2.6 s minimum; this component only animates. All
 * motion collapses under prefers-reduced-motion via the global rule.
 */
export function CastingLoader() {
  const [subIndex, setSubIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSubIndex((current) => (current + 1) % LOAD_SUBS.length);
    }, SUB_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-[26px] p-10">
      <div className="relative h-[190px] w-[190px]">
        <div className="orbit-ring absolute inset-0 animate-[spin_22s_linear_infinite_reverse] rounded-full" />
        <div className="orbit-ring absolute inset-[22px] animate-[spin_14s_linear_infinite] rounded-full border-dashed" />
        <div className="orbit-planet absolute top-[-4px] left-1/2 ml-[-6px] h-[12px] w-[12px] animate-[spin_6s_linear_infinite] rounded-full" />
        <div className="absolute inset-0 grid place-items-center">
          <Mascot size={96} />
        </div>
      </div>
      <div className="text-center">
        <div className="font-display text-[26px] font-medium">
          đang luận giải
          <span className="load-dots">
            <span>.</span>
            <span>.</span>
            <span>.</span>
          </span>
        </div>
        <p className="mt-[10px] text-[14px] font-light text-muted">{LOAD_SUBS[subIndex]}</p>
      </div>
    </div>
  );
}
