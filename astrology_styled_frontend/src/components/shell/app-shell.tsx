import { AppNav } from "./app-nav";
import { TopBar } from "./top-bar";

/**
 * The chrome every screen sits inside.
 *
 * The document itself scrolls — there is no full-height inner scroll container
 * — so the mobile browser's URL bar and the Android navigation bar keep their
 * normal behaviour. The content column is capped at `--col` until the desktop
 * tier, where the rail takes the left edge and the column widens to `--shell`.
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative z-1 min-h-dvh lg:pl-[var(--rail)]">
      <TopBar />
      <div className="mx-auto w-full max-w-[var(--col)] lg:max-w-[var(--shell)]">{children}</div>
      <AppNav />
    </div>
  );
}

/**
 * Standard screen padding: the gutters every tab shares, plus enough bottom
 * room to scroll clear of the tab bar.
 */
export function ScreenPad({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-[22px] pt-[calc(10px+var(--safe-t))] pb-[calc(56px+var(--tabbar-h))] md:px-[30px] lg:px-10 lg:pt-[calc(18px+var(--safe-t))] lg:pb-14">
      {children}
    </div>
  );
}
