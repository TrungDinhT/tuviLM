import type { NguHanh } from "@/lib/api/schemas";

/**
 * The lucky colour — resolved from the nạp âm bản mệnh's ngũ hành, a
 * different fact from the global accent (the ngũ hành of Mệnh's chính tinh).
 *
 * `hue` is a `var(--element-*)` reference like every colour this side of
 * `globals.css`; the Vận May card writes it to its own scoped `--luck-hue`
 * and never touches the global accent.
 */

export interface LuckColour {
  /** The colour's Vietnamese name, shown beside the orb. */
  readonly name: string;
  /** `var(--element-*)` reference for the card's scoped `--luck-hue`. */
  readonly hue: string;
}

export const LUCK_COLOURS: Record<NguHanh, LuckColour> = {
  Kim: { name: "Vàng kim", hue: "var(--element-kim)" },
  Mộc: { name: "Xanh lục", hue: "var(--element-moc)" },
  Thủy: { name: "Xanh lam", hue: "var(--element-thuy)" },
  Hỏa: { name: "Đỏ san hô", hue: "var(--element-hoa)" },
  Thổ: { name: "Nâu đất", hue: "var(--element-tho)" },
};

export function luckColourFor(nguHanh: NguHanh): LuckColour {
  return LUCK_COLOURS[nguHanh];
}
