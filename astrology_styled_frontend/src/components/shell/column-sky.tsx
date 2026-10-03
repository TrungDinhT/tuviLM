import { ShootingStars } from "./shooting-stars";
import { StarField } from "./star-field";

/**
 * The twilight canvas sitting directly behind the content column.
 *
 * Fixed rather than scrolling, so the sky stays put while content moves over
 * it. Shooting stars live here rather than in `Cosmos` because on a phone the
 * column *is* the viewport — putting them in the outer layer would fly them
 * past off-screen.
 */
export function ColumnSky() {
  return (
    <div
      className="fixed top-0 bottom-0 left-1/2 z-0 w-full max-w-[var(--col)] -translate-x-1/2 overflow-hidden pointer-events-none bg-[radial-gradient(90%_60%_at_50%_106%,rgba(255,158,125,0.16),transparent_60%),radial-gradient(120%_80%_at_50%_-5%,var(--color-bg-2),var(--color-bg-1)_46%,var(--color-bg-0)_100%)] sm:shadow-[0_0_0_1px_rgba(243,239,250,0.07),0_30px_90px_rgba(8,4,20,0.55)] lg:max-w-none lg:shadow-none"
      aria-hidden="true"
    >
      <StarField count={46} minSize={1} maxSize={2.6} className="absolute inset-0" />
      <ShootingStars />
    </div>
  );
}
