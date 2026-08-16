"use client";

import { useEffect, useState } from "react";

import { usePrefersReducedMotion } from "@/hooks/use-prefers-reduced-motion";

interface Shot {
  readonly id: number;
  readonly sx: number;
  readonly sy: number;
  readonly angle: number;
  readonly length: number;
  readonly distance: number;
  readonly duration: number;
}

function between(min: number, max: number) {
  return min + Math.random() * (max - min);
}

/**
 * Occasional shooting stars, spawned on a randomized interval.
 *
 * Three rules the prototype establishes and this keeps:
 * - nothing spawns while the tab is hidden
 * - nothing spawns at all under `prefers-reduced-motion: reduce`
 * - every shot removes itself once its animation ends
 */
export function ShootingStars() {
  const reducedMotion = usePrefersReducedMotion();
  const [shots, setShots] = useState<Shot[]>([]);

  useEffect(() => {
    if (reducedMotion) return;

    let nextId = 0;
    let timer: ReturnType<typeof setTimeout>;

    const schedule = () => {
      timer = setTimeout(() => {
        if (!document.hidden) {
          const shot: Shot = {
            id: nextId++,
            sx: between(-6, 52),
            sy: between(2, 44),
            angle: between(14, 42),
            length: between(74, 148),
            distance: between(240, 460),
            duration: between(1.05, 1.9),
          };
          setShots((current) => [...current, shot]);
          setTimeout(
            () => setShots((current) => current.filter((s) => s.id !== shot.id)),
            shot.duration * 1000 + 180,
          );
        }
        schedule();
      }, between(5200, 15000));
    };

    schedule();
    return () => clearTimeout(timer);
  }, [reducedMotion]);

  // Rendering nothing rather than clearing state keeps the effect free of a
  // synchronous setState, and a reduced-motion viewer never sees a stale shot.
  if (reducedMotion) return null;

  return (
    <>
      {shots.map((shot) => (
        <i
          key={shot.id}
          className="shooting-star"
          style={
            {
              "--sx": `${shot.sx.toFixed(1)}%`,
              "--sy": `${shot.sy.toFixed(1)}%`,
              "--sang": `${shot.angle.toFixed(1)}deg`,
              "--slen": `${shot.length.toFixed(0)}px`,
              "--sdist": `${shot.distance.toFixed(0)}px`,
              "--sdur": `${shot.duration.toFixed(2)}s`,
            } as React.CSSProperties
          }
        />
      ))}
    </>
  );
}
