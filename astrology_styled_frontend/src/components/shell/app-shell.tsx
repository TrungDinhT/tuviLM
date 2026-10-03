"use client";

import { usePathname } from "next/navigation";

import { screenFor } from "@/config/site";
import { cn } from "@/lib/utils";
import { useChartStore } from "@/store/chart-store";

import { AppNav } from "./app-nav";
import { TopBar } from "./top-bar";

const STANDALONE_ROUTES = new Set(["/login", "/register"]);

/**
 * The chrome every screen sits inside.
 *
 * The document itself scrolls — there is no full-height inner scroll container
 * — so the mobile browser's URL bar and the Android navigation bar keep their
 * normal behaviour. The content column is capped at `--col` until the desktop
 * tier, where the rail takes the left edge and the column widens to `--shell`.
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const hasChart = useChartStore((state) => state.hasChart);
  const standalone = STANDALONE_ROUTES.has(pathname) || screenFor(pathname) === null;

  if (standalone) {
    return <div className="relative z-1 min-h-dvh">{children}</div>;
  }

  return (
    <div className={cn("relative z-1 min-h-dvh", hasChart && "lg:pl-[var(--rail)]")}>
      <TopBar />
      <div className="mx-auto w-full max-w-[var(--col)] lg:max-w-[var(--shell)]">{children}</div>
      {hasChart ? <AppNav /> : null}
    </div>
  );
}

/**
 * Standard screen padding: the gutters every tab shares, plus enough bottom
 * room to scroll clear of the tab bar.
 */
export function ScreenPad({
  children,
  reserveTabBar = true,
}: {
  children: React.ReactNode;
  reserveTabBar?: boolean;
}) {
  return (
    <div
      className={cn(
        "px-[22px] pt-[calc(10px+var(--safe-t))] md:px-[30px] lg:px-10 lg:pt-[calc(18px+var(--safe-t))] lg:pb-14",
        reserveTabBar ? "pb-[calc(56px+var(--tabbar-h))]" : "pb-[10px]",
      )}
    >
      {children}
    </div>
  );
}
