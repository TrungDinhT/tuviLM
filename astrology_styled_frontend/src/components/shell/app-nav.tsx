"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { AN_SAO_ROUTE, isActive, NAV_ITEMS, type NavItem } from "@/config/site";

import { NavIconGlyph } from "./nav-icons";

/**
 * The application's only navigation.
 *
 * Below `lg` it is a fixed bottom tab bar capped at the content column. From
 * `lg` it is a full-height left rail with a brand block. One component, one
 * set of markup, one active state — the presentations differ in CSS only, so
 * resizing across the boundary never remounts anything or loses the active
 * item.
 *
 * The brand block is the single desktop-only element: a bottom bar has no room
 * for a product name, a rail needs one.
 */
export function AppNav() {
  const pathname = usePathname();

  // The casting screen is a full-bleed flow: the bottom tab bar never shows
  // there — it appears once the cast lands on Bản mệnh. AppShell only mounts
  // this navigation after a chart exists, so the desktop rail follows the
  // same rule without leaving an empty rail-sized gutter behind.
  const hiddenBelowDesktop = pathname === AN_SAO_ROUTE;

  return (
    <nav
      aria-label="Điều hướng chính"
      className={[
        "bg-[linear-gradient(0deg,rgba(18,10,36,0.82),rgba(18,10,36,0.58)_70%,rgba(18,10,36,0))] fixed z-35 border-glass-line backdrop-blur-[14px] lg:border-r lg:bg-[linear-gradient(180deg,rgba(20,12,40,0.74),rgba(14,8,30,0.88))]",
        hiddenBelowDesktop ? "hidden lg:flex" : "flex",
        // Phone / tablet: a bottom band, capped at the column width.
        "bottom-0 left-1/2 w-full max-w-[var(--col)] -translate-x-1/2 gap-0.5",
        "px-2 pt-[9px] pb-[calc(11px+var(--safe-b))]",
        "max-[349px]:px-1",
        // Desktop: a full-height rail on the left edge.
        "lg:top-0 lg:bottom-0 lg:left-0 lg:h-dvh lg:w-[var(--rail)] lg:max-w-none",
        "lg:translate-x-0 lg:flex-col lg:justify-start lg:gap-1",
        "lg:px-4 lg:pt-[22px] lg:pb-[calc(20px+var(--safe-b))]",
      ].join(" ")}
    >
      <div className="hidden items-center gap-[11px] px-2 pt-0.5 pb-5 lg:flex" aria-hidden="true">
        <span className="accent-gradient grid size-9 flex-none place-items-center rounded-[11px] text-[17px] text-bg-0">
          ✦
        </span>
        <span>
          <b className="font-display text-[17px] font-semibold tracking-[0.18em]">TỬ VI</b>
          <small className="mt-0.5 block text-[9px] font-semibold tracking-[0.16em] text-muted uppercase">
            An sao &amp; luận giải
          </small>
        </span>
      </div>

      {NAV_ITEMS.map((item) => (
        <NavButton key={item.href} item={item} pathname={pathname} />
      ))}
    </nav>
  );
}

function NavButton({ item, pathname }: { item: NavItem; pathname: string }) {
  const active = isActive(item, pathname);

  const shared = [
    "flex min-w-0 flex-1 flex-col items-center gap-1 px-px py-1.5",
    "text-[10px] font-medium tracking-[0.01em] whitespace-nowrap",
    "max-[349px]:text-[9px] max-[349px]:tracking-normal",
    "transition-colors duration-200",
    // Desktop: a row in the rail, not a column in a bar.
    "lg:flex-none lg:flex-row lg:justify-start lg:gap-3 lg:rounded-xl",
    "lg:px-[13px] lg:py-[11px] lg:text-sm lg:tracking-normal",
  ].join(" ");

  const iconClass = [
    "size-[23px] max-[349px]:size-[21px] md:size-[25px] lg:size-5",
    "transition-[transform,filter] duration-300",
    active
      ? "drop-shadow-[0_0_8px_var(--accent-glow)] -translate-y-px lg:translate-y-0 lg:drop-shadow-none"
      : "",
  ].join(" ");

  return (
    <Link
      href={item.href}
      aria-current={active ? "page" : undefined}
      className={[
        shared,
        active
          ? "text-accent lg:accent-gradient lg:text-bg-0"
          : "text-muted lg:hover:bg-white/6 lg:hover:text-ink",
      ].join(" ")}
    >
      <NavIconGlyph name={item.icon} className={iconClass} />
      {item.label}
    </Link>
  );
}
