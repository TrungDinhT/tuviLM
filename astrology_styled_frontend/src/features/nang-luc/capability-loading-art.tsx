import type { CSSProperties } from "react";
import { CapabilityIcon, CelestialOrb } from "./celestial-art";
import styles from "./capability-loading-art.module.css";

const ICONS = [
  { kind: "shield", x: "27%", y: "15%", dx: "18%", dy: "-24%", duration: "9s", delay: "-2s" },
  { kind: "target", x: "77%", y: "23%", dx: "-16%", dy: "-30%", duration: "11s", delay: "-7s" },
  { kind: "bulb", x: "12%", y: "49%", dx: "12%", dy: "-22%", duration: "10s", delay: "-5s" },
  { kind: "balance", x: "86%", y: "61%", dx: "-20%", dy: "-18%", duration: "12s", delay: "-1s" },
  { kind: "chat", x: "24%", y: "79%", dx: "-14%", dy: "-26%", duration: "11s", delay: "-8s" },
  { kind: "work", x: "66%", y: "87%", dx: "18%", dy: "-20%", duration: "13s", delay: "-6s" },
];

/** Atmosphere while the report is pending; these icons are not model findings. */
export function CapabilityLoadingArt() {
  return (
    <div className={styles.art} aria-hidden="true" data-testid="capability-loading-art">
      <div className={styles.halo} />
      <div className={styles.radiance}>
        <span />
        <span />
        <span />
      </div>
      <div className={styles.core}>
        <CelestialOrb decorativeTrails={false} />
      </div>
      {ICONS.map(({ kind, x, y, dx, dy, duration, delay }) => (
        <div
          key={kind}
          className={styles.floatAnchor}
          style={
            {
              left: x,
              top: y,
              "--drift-x": dx,
              "--drift-y": dy,
              "--duration": duration,
              "--delay": delay,
            } as CSSProperties
          }
        >
          <span className={styles.icon}>
            <CapabilityIcon kind={kind} />
          </span>
        </div>
      ))}
    </div>
  );
}
