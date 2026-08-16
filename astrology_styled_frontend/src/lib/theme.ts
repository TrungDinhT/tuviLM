/**
 * Runtime accent resolution.
 *
 * The accent is not a fixed token: it is derived from the chính tinh sitting
 * in cung Mệnh of the user's chart. Three properties carry it —
 * `--accent`, `--accent-2`, `--accent-glow` — and exactly one module is
 * allowed to write them (see `components/providers/theme-provider.tsx`).
 *
 * Every value returned here is a `var(--star-*)` reference, never a colour.
 * The literals live in `src/app/globals.css`.
 *
 * ## Scoped accents
 *
 * Colours that vary per subtree get their own custom property, set inline on
 * that subtree, and nest *beneath* the global accent rather than replacing it:
 *
 * | Property             | Scope                                 |
 * | -------------------- | ------------------------------------- |
 * | `--theme`            | one of the six Thiên Bàn topics       |
 * | `--t-hue`            | one topic card in the Bản mệnh deck   |
 * | `--focus`            | the highlighted source cung           |
 * | `--star-color`       | one star in a cung list               |
 * | `--star-info-color`  | the star currently open in its popup  |
 *
 * Any new per-subtree colour follows the same shape. Reassigning `--accent`
 * locally is never the answer: every descendant glow, border and gradient
 * would silently inherit the wrong hue.
 */

/** The chính tinh that carry a colour in the design. */
const CHINH_TINH_WITH_PALETTE = [
  "tuvi",
  "thienphu",
  "thatsat",
  "phaquan",
  "thamlang",
  "thaiduong",
  "thaiam",
  "vukhuc",
] as const;

type PalettedChinhTinh = (typeof CHINH_TINH_WITH_PALETTE)[number];

/**
 * The chính tinh of cung Mệnh, as resolved from the backend chart.
 *
 * Empty means vô chính diệu. Two entries mean song tinh. This is never
 * derived from the birth date — see the note in AGENTS.md.
 */
export interface ChartOutcome {
  readonly stars: readonly string[];
}

interface Accent {
  readonly accent: string;
  readonly accent2: string;
  readonly glow: string;
}

const PALETTED: ReadonlySet<string> = new Set(CHINH_TINH_WITH_PALETTE);

function isPaletted(star: string): star is PalettedChinhTinh {
  return PALETTED.has(star);
}

const NEUTRAL: Accent = {
  accent: "var(--star-neutral)",
  accent2: "var(--star-neutral-light)",
  glow: "var(--star-neutral-glow)",
};

/** The pre-chart accent, and what a reset returns to. */
export const DEFAULT_ACCENT: Accent = {
  accent: "var(--accent-default)",
  accent2: "var(--accent-2-default)",
  glow: "var(--accent-glow-default)",
};

/**
 * Resolve an outcome to the three accent values.
 *
 * - no stars (vô chính diệu) → the neutral pair
 * - one star → its colour and its light tint
 * - two stars (song tinh) → the two star colours, glow from the first
 * - any star without a palette entry → the neutral pair, so nothing renders
 *   an undefined colour or a placeholder
 */
export function resolveAccent(outcome: ChartOutcome | null): Accent {
  if (outcome === null) return DEFAULT_ACCENT;

  const stars = outcome.stars;
  if (stars.length === 0) return NEUTRAL;
  if (!stars.every(isPaletted)) return NEUTRAL;

  const [first, second] = stars;
  if (first === undefined) return NEUTRAL;

  const glow = `var(--star-${first}-glow)`;
  if (second === undefined) {
    return { accent: `var(--star-${first})`, accent2: `var(--star-${first}-light)`, glow };
  }
  return { accent: `var(--star-${first})`, accent2: `var(--star-${second})`, glow };
}
