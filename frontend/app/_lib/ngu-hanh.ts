import starsData from "@/constants/stars.json";

const COLOR_BY_KEY: Record<string, string> = {
  hoa:  "var(--color-nh-hoa)",
  moc:  "var(--color-nh-moc)",
  tho:  "var(--color-nh-tho)",
  kim:  "var(--color-nh-kim)",
  thuy: "var(--color-nh-thuy)",
};

const KEY_BY_VN: Record<string, string> = {
  "Hỏa": "hoa",
  "Mộc": "moc",
  "Thổ": "tho",
  "Kim": "kim",
  "Thủy": "thuy",
};

type StarEntry = { name: string; ngu_hanh: string | null };
const NGU_HANH_BY_NAME: Map<string, string> = (() => {
  const m = new Map<string, string>();
  for (const entry of Object.values(starsData.stars) as StarEntry[]) {
    if (entry.ngu_hanh) m.set(entry.name, entry.ngu_hanh);
  }
  return m;
})();

function stripParen(s: string): string {
  return s.replace(/\s*\([^)]*\)\s*$/, "");
}

export function colorForElement(element: string | null | undefined): string {
  if (!element) return "var(--color-ink)";
  const key = KEY_BY_VN[element] ?? element.toLowerCase();
  return COLOR_BY_KEY[key] ?? "var(--color-ink)";
}

export function colorForStarName(starName: string): string {
  const clean = stripParen(starName);
  const key = NGU_HANH_BY_NAME.get(clean);
  return key ? COLOR_BY_KEY[key] ?? "var(--color-ink)" : "var(--color-ink)";
}
