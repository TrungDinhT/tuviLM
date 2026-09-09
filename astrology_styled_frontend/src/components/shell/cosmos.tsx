import { StarField } from "./star-field";

import styles from "./cosmos.module.css";

/**
 * The full-viewport ambient backdrop: twilight gradient, two breathing
 * nebulae, and a wide star field.
 *
 * Server-rendered apart from the stars. Below the `sm` tier the nebulae are
 * hidden and the stars dimmed by CSS — on a phone the content column is the
 * whole page, so the surrounding ambience only costs paint time.
 */
export function Cosmos() {
  return (
    <div
      className="fixed inset-0 z-0 overflow-hidden bg-[radial-gradient(80%_55%_at_50%_108%,rgba(255,158,125,0.22),transparent_60%),radial-gradient(120%_90%_at_50%_0%,#3b2063_0%,#2e1a4a_45%,#160d2c_100%)]"
      aria-hidden="true"
    >
      <div
        className={`${styles.neb} absolute top-[-15vmax] left-[-10vmax] h-[60vmax] w-[60vmax] max-sm:hidden rounded-full bg-[radial-gradient(circle,rgba(123,79,166,0.6),transparent_60%)] opacity-50 blur-[60px]`}
      />
      <div
        className={`${styles.neb} absolute right-[-12vmax] bottom-[-10vmax] h-[50vmax] w-[50vmax] max-sm:hidden rounded-full bg-[radial-gradient(circle,rgba(79,157,224,0.35),transparent_60%)] opacity-50 blur-[60px] [animation-delay:-4s]`}
      />
      <StarField count={70} minSize={1} maxSize={3} bright dim className="absolute inset-0" />
    </div>
  );
}
