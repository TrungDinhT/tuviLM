import starsData from "@/constants/stars.json";

type StarEntry = { name: string; categories: string[]; ngu_hanh: string | null };

const CATEGORIES_BY_NAME: Map<string, string[]> = (() => {
  const m = new Map<string, string[]>();
  for (const entry of Object.values(starsData.stars) as StarEntry[]) {
    m.set(entry.name, entry.categories);
  }
  return m;
})();

export type PhuTinhKind = "cat" | "hung";

export function classifyPhuTinh(name: string): PhuTinhKind {
  const clean = stripParen(name);
  const cats = CATEGORIES_BY_NAME.get(clean);
  if (cats && cats.includes("hung_tinh")) return "hung";
  return "cat";
}

// Strip parenthetical for tight cells: "Phá Quân (Miếu)" → "Phá Quân"
export function stripParen(s: string): string {
  return s.replace(/\s*\([^)]*\)\s*$/, "");
}
