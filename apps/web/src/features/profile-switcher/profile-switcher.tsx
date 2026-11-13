"use client";

import { Popover } from "@base-ui/react/popover";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import {
  Drawer,
  DrawerBody,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
} from "@/components/primitives/drawer";
import { AN_SAO_ROUTE } from "@/config/site";
import { useMediaQuery } from "@/hooks/use-media-query";
import { useAccountRequestScope } from "@/lib/api/account-request";
import { profileDisplayName } from "@/lib/api/chart-profiles";
import { useChartProfiles } from "@/lib/api/hooks";
import { cn } from "@/lib/utils";
import { useChartStore } from "@/store/chart-store";

import { Avatar, SectionLabel } from "./parts";
import { birthDetail, findCurrentProfile } from "./profile-format";
import { SavedProfileList } from "./saved-profile-list";
import { useSwitcherPanel } from "./use-switcher-panel";

const WIDE_QUERY = "(min-width: 768px)";

/**
 * Shows whose chart is on screen and lets the user change it from any tab.
 *
 * The chart being read is shared by every tab, so the control that changes it
 * sits in the header of every tab instead of inside Hồ sơ. One body, two
 * shells: a bottom drawer on phones and a popover under the chip from `md` up.
 * Renders nothing until a chart exists.
 *
 * Three units, each with its own hooks: this shell (chip and layout),
 * `useSwitcherPanel` (open state and filter) and `SavedProfileList` (the list
 * and the mutation that opens a chart). Both shells unmount the body when the
 * panel closes.
 */
export function ProfileSwitcher({
  className,
  align = "start",
}: {
  className?: string;
  /** Which edge of the chip the popover lines up with, from `md` up. */
  align?: "start" | "end";
}) {
  const router = useRouter();
  const pathname = usePathname();
  const hasChart = useChartStore((state) => state.hasChart);
  const birth = useChartStore((state) => state.birthInfo);
  const profileId = useChartStore((state) => state.chartProfileId);
  const { userId } = useAccountRequestScope();
  const signedIn = Boolean(userId);
  const { data: profiles } = useChartProfiles(signedIn && hasChart);
  const panel = useSwitcherPanel();
  const isWide = useMediaQuery(WIDE_QUERY);

  // Casting is where a chart gets replaced; a switcher there would compete with the form.
  if (!hasChart || birth === null || pathname === AN_SAO_ROUTE) return null;

  const current = findCurrentProfile(profiles?.chart_profiles ?? [], profileId, birth);
  const dateLabel = profileDisplayName(birth);
  const currentName = current?.display_name ?? dateLabel;
  const chipDetail =
    currentName === dateLabel ? birthDetail(birth) : `${dateLabel} · ${birthDetail(birth)}`;

  const chip = (
    <button
      type="button"
      aria-haspopup="dialog"
      aria-expanded={panel.open}
      aria-label={`Lá số đang xem: ${currentName}. Đổi lá số`}
      className={cn(
        "pill-ghost inline-flex min-h-11 max-w-full min-w-0 cursor-pointer items-center gap-2 rounded-full py-1 pr-3 pl-1.5 text-left transition-colors hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent lg:min-h-10",
        className,
      )}
      onClick={isWide ? undefined : () => panel.changeOpen(true)}
    >
      <Avatar name={currentName} />
      <span className="min-w-0">
        <span className="block truncate text-[13px] leading-tight font-semibold">
          {currentName}
        </span>
        <span className="block truncate text-[11px] leading-tight text-muted">{chipDetail}</span>
      </span>
      <svg
        viewBox="0 0 24 24"
        className="size-4 shrink-0 fill-none stroke-current text-muted"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </button>
  );

  const body = (
    <div className="flex min-h-0 flex-col gap-3">
      <div>
        <SectionLabel>Đang xem</SectionLabel>
        <div className="mt-1.5 flex items-center gap-3 rounded-2xl border border-accent-glow bg-[color-mix(in_srgb,var(--accent)_14%,transparent)] px-3 py-2.5">
          <Avatar name={currentName} />
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-semibold">{currentName}</span>
            <span className="block truncate text-xs text-muted">
              {dateLabel} · {birthDetail(birth)}
            </span>
          </span>
          <span className="shrink-0 text-accent" aria-hidden="true">
            ✓
          </span>
        </div>
      </div>

      {signedIn ? (
        <SavedProfileList
          currentId={current?.id}
          search={panel.search}
          onSearchChange={panel.setSearch}
          onSwitched={panel.close}
        />
      ) : (
        <p className="px-1 text-[13px] leading-relaxed text-muted">
          <Link href="/login" className="font-semibold text-accent">
            Đăng nhập
          </Link>{" "}
          để lưu nhiều lá số và đổi qua lại ở đây.
        </p>
      )}

      <div className="flex flex-col gap-2 border-t border-glass-line pt-3">
        <button
          type="button"
          onClick={() => {
            panel.close();
            router.push(AN_SAO_ROUTE);
          }}
          disabled={panel.isOpening}
          className="pill-primary inline-flex min-h-12 w-full cursor-pointer items-center justify-center gap-2 rounded-full border-0 px-5 text-sm font-semibold transition-transform active:scale-[0.97] disabled:pointer-events-none disabled:opacity-40"
        >
          <span aria-hidden="true">＋</span> An lá số mới
        </button>
        {signedIn ? (
          <Link
            href="/ho-so"
            onClick={panel.close}
            className="inline-flex min-h-11 items-center justify-center rounded-full text-[13px] font-semibold text-muted no-underline hover:text-ink"
          >
            Đổi tên, xoá lá số trong Hồ sơ ›
          </Link>
        ) : null}
      </div>
    </div>
  );

  if (isWide) {
    return (
      <Popover.Root open={panel.open} onOpenChange={panel.changeOpen}>
        <Popover.Trigger render={chip} />
        <Popover.Portal>
          <Popover.Positioner side="bottom" align={align} sideOffset={10} className="z-60">
            <Popover.Popup className="overlay-card w-[360px] max-w-[calc(100vw-32px)] rounded-3xl p-4 outline-none">
              <Popover.Title className="sr-only">Đổi lá số</Popover.Title>
              {body}
            </Popover.Popup>
          </Popover.Positioner>
        </Popover.Portal>
      </Popover.Root>
    );
  }

  return (
    <>
      {chip}
      <Drawer open={panel.open} onOpenChange={panel.changeOpen}>
        <DrawerContent>
          <DrawerHeader className="pb-3">
            <DrawerTitle>Đổi lá số</DrawerTitle>
          </DrawerHeader>
          <DrawerBody className="pb-[max(20px,env(safe-area-inset-bottom))]">{body}</DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  );
}
