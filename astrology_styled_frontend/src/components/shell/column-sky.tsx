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
    <div className="column-sky" aria-hidden="true">
      <StarField count={46} minSize={1} maxSize={2.6} className="absolute inset-0" />
      <ShootingStars />
    </div>
  );
}
