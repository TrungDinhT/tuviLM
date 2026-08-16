"use client";

import { useMemo } from "react";

import { useIsHydrated } from "@/hooks/use-is-hydrated";

interface Star {
  readonly size: number;
  readonly left: number;
  readonly top: number;
  readonly twinkle: number;
  readonly drift: number;
  readonly dx: number;
  readonly dy: number;
  readonly twinkleDelay: number;
  readonly driftDelay: number;
}

function between(min: number, max: number) {
  return min + Math.random() * (max - min);
}

function seed(count: number, minSize: number, maxSize: number): Star[] {
  return Array.from({ length: count }, () => ({
    size: between(minSize, maxSize),
    left: between(0, 100),
    top: between(0, 100),
    twinkle: between(3.2, 7),
    drift: between(26, 62),
    dx: between(-46, 46),
    dy: between(-34, 34),
    // Negative delays so the sky is already in motion on the first frame.
    twinkleDelay: -between(0, 7),
    driftDelay: -between(0, 60),
  }));
}

const NO_STARS: readonly Star[] = [];

/**
 * A field of drifting, twinkling stars.
 *
 * Seeding is gated behind hydration, never run during render on the server:
 * `Math.random()` there would produce different markup than the client and
 * break hydration. The server therefore emits an empty layer, which is fine —
 * the backdrop is decorative and the twilight gradient behind it carries the
 * look on its own.
 */
export function StarField({
  count,
  minSize,
  maxSize,
  bright = false,
  className,
}: {
  count: number;
  minSize: number;
  maxSize: number;
  bright?: boolean;
  className?: string;
}) {
  const hydrated = useIsHydrated();
  const stars = useMemo(
    () => (hydrated ? seed(count, minSize, maxSize) : NO_STARS),
    [hydrated, count, minSize, maxSize],
  );

  return (
    <div className={className} aria-hidden="true">
      {stars.map((star, i) => (
        <span
          key={i}
          className={bright ? "sky-star sky-star-bright" : "sky-star"}
          style={
            {
              width: `${star.size.toFixed(1)}px`,
              height: `${star.size.toFixed(1)}px`,
              left: `${star.left.toFixed(2)}%`,
              top: `${star.top.toFixed(2)}%`,
              "--twinkle": `${star.twinkle.toFixed(2)}s`,
              "--drift": `${star.drift.toFixed(1)}s`,
              "--dx": `${star.dx.toFixed(1)}px`,
              "--dy": `${star.dy.toFixed(1)}px`,
              animationDelay: `${star.twinkleDelay.toFixed(2)}s, ${star.driftDelay.toFixed(2)}s`,
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  );
}
