/**
 * Runtime accent resolution.
 *
 * The accent is not a fixed token: it is the ngũ hành of the chính tinh
 * sitting in cung Mệnh of the user's chart. Three properties carry it —
 * `--accent`, `--accent-2`, `--accent-glow` — and exactly one module is
 * allowed to write them (see `components/providers/theme-provider.tsx`).
 *
 * Every value returned here is a `var(--element-*)` reference, never a
 * colour. The literals live in `src/app/globals.css`.
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

/** The five ngũ hành, keyed as the `--element-*` custom properties. */
type NguHanh = "kim" | "moc" | "thuy" | "hoa" | "tho";

/**
 * Chính tinh → ngũ hành, covering all fourteen so every chart gets a real
 * accent. Mirrors `frontend/constants/stars.json`, the table the production
 * app colours stars with.
 */
const CHINH_TINH_ELEMENT: Record<string, NguHanh> = {
  tuvi: "tho",
  thienphu: "tho",
  thatsat: "kim",
  phaquan: "thuy",
  thamlang: "moc",
  thaiduong: "hoa",
  thaiam: "thuy",
  vukhuc: "kim",
  liemtrinh: "hoa",
  thienco: "moc",
  thienluong: "moc",
  thientuong: "thuy",
  thiendong: "thuy",
  cumon: "thuy",
};

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

const NEUTRAL: Accent = {
  accent: "var(--accent-neutral)",
  accent2: "var(--accent-neutral-light)",
  glow: "var(--accent-neutral-glow)",
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
 * - one star → its element colour and that element's light tint
 * - two stars (song tinh) → the two element colours, glow from the first
 * - any star outside the table → the neutral pair, so nothing renders an
 *   undefined colour or a placeholder
 */
export function resolveAccent(outcome: ChartOutcome | null): Accent {
  if (outcome === null) return DEFAULT_ACCENT;

  const elements = outcome.stars.map((star) => CHINH_TINH_ELEMENT[star]);
  const [first, second] = elements;
  if (first === undefined || elements.includes(undefined)) return NEUTRAL;

  const accent = `var(--element-${first})`;
  const glow = `var(--element-${first}-glow)`;
  const accent2 =
    second === undefined ? `var(--element-${first}-light)` : `var(--element-${second})`;
  return { accent, accent2, glow };
}
