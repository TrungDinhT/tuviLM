/**
 * Screen metadata — the single source of truth for navigation.
 *
 * Both navigation presentations (the bottom tab bar below `lg`, the left rail
 * at `lg` and above) and the desktop top bar read from here. Adding a
 * destination means adding a row, not touching two components.
 */

export const NAV_ICONS = [
  "banMenh",
  "vanHan",
  "hoiAi",
  "nangCao",
  "hoSo",
] as const;

export type NavIcon = (typeof NAV_ICONS)[number];

interface ScreenMeta {
  /** Route this screen lives at. */
  readonly href: string;
  /** Group label shown above the title in the desktop top bar. */
  readonly group: string;
  /** Screen title, in the top bar. */
  readonly title: string;
  /** Locked until a chart has been cast. */
  readonly requiresChart: boolean;
}

export interface NavItem extends ScreenMeta {
  /** Label under the tab icon, and beside it in the rail. */
  readonly label: string;
  readonly icon: NavIcon;
  /** Routes that should light this item up, beyond `href` itself. */
  readonly alsoMatches?: readonly string[];
}

const GROUP_CHART = "Lá số của bạn";
const GROUP_DEEP = "Tra cứu chuyên sâu";

/** Casting lives at the root. Reaching it again means casting again. */
export const AN_SAO_ROUTE = "/";

/** The five destinations in the tab bar / rail, in order. */
export const NAV_ITEMS: readonly NavItem[] = [
  {
    href: "/ban-menh",
    label: "Bản mệnh",
    icon: "banMenh",
    group: GROUP_CHART,
    title: "Bản mệnh",
    requiresChart: true,
  },
  {
    href: "/van-han",
    label: "Vận hạn",
    icon: "vanHan",
    group: GROUP_CHART,
    title: "Vận hạn 2026",
    requiresChart: true,
  },
  {
    href: "/hoi-ai",
    label: "Hỏi AI",
    icon: "hoiAi",
    group: GROUP_CHART,
    title: "Hỏi AI · Nghê Sao",
    requiresChart: true,
  },
  {
    href: "/thien-ban",
    label: "Nâng cao",
    icon: "nangCao",
    group: GROUP_DEEP,
    title: "Thiên Bàn",
    requiresChart: true,
    // The full 12-cung chart is reached from Thiên Bàn and shares its tab.
    alsoMatches: ["/la-so"],
  },
  {
    href: "/ho-so",
    label: "Hồ sơ",
    icon: "hoSo",
    group: GROUP_DEEP,
    title: "Hồ sơ",
    requiresChart: false,
  },
];

/** Screens that have no tab of their own but still title the top bar. */
const EXTRA_SCREENS: Record<string, ScreenMeta> = {
  "/": { href: "/", group: GROUP_CHART, title: "An sao", requiresChart: false },
  "/la-so": {
    href: "/la-so",
    group: GROUP_DEEP,
    title: "Lá số gốc · 12 cung",
    requiresChart: true,
  },
};

/** Metadata for a pathname, or `null` if it is not a known screen. */
export function screenFor(pathname: string): ScreenMeta | null {
  const item = NAV_ITEMS.find((entry) => entry.href === pathname);
  if (item) return item;
  return EXTRA_SCREENS[pathname] ?? null;
}

/** Whether a nav item should render as active for the current pathname. */
export function isActive(item: NavItem, pathname: string): boolean {
  if (item.href === pathname) return true;
  return item.alsoMatches?.includes(pathname) ?? false;
}
