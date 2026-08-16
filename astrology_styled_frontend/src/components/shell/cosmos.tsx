import { StarField } from "./star-field";

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
    <div className="cosmos" aria-hidden="true">
      <div className="neb neb-a" />
      <div className="neb neb-b" />
      <StarField count={70} minSize={1} maxSize={3} bright className="absolute inset-0" />
    </div>
  );
}
