"use client";

import { Popover } from "@base-ui/react/popover";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, useSyncExternalStore } from "react";

import {
  Drawer,
  DrawerBody,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
} from "@/components/primitives/drawer";
import { AN_SAO_ROUTE } from "@/config/site";
import { canhGioOf, MERIDIEM } from "@/features/an-sao/birth-time";
import { useAccountRequestScope } from "@/lib/api/account-request";
import { openChartProfileMutationOptions, profileDisplayName } from "@/lib/api/chart-profiles";
import { useChartProfiles } from "@/lib/api/hooks";
import type { BirthInfo, ChartProfile } from "@/lib/api/schemas";
import { describe, isApiError } from "@/lib/http/errors";
import { showToast } from "@/lib/toast";
import { cn } from "@/lib/utils";
import { useChartStore } from "@/store/chart-store";

const WIDE_QUERY = "(min-width: 768px)";
/** Below this many saved charts the list is short enough to scan without a filter. */
const SEARCH_THRESHOLD = 6;

function subscribeWidth(onChange: () => void) {
  const media = window.matchMedia(WIDE_QUERY);
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
}

function normalize(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/đ/g, "d");
}

function birthDetail(birth: BirthInfo): string {
  const canh = canhGioOf(birth.hour % 12 || 12, birth.hour < 12 ? MERIDIEM.AM : MERIDIEM.PM);
  return `Giờ ${canh.chi} · ${birth.gender === "M" ? "Nam" : "Nữ"}`;
}

function sameBirth(a: BirthInfo, b: BirthInfo): boolean {
  return (
    a.year === b.year &&
    a.month === b.month &&
    a.day === b.day &&
    a.hour === b.hour &&
    a.gender === b.gender
  );
}

/**
 * Shows whose chart is on screen and lets the user change it from any tab.
 *
 * The chart being read is shared by every tab, so the control that changes it
 * sits in the header of every tab instead of inside Hồ sơ. One body, two
 * shells: a bottom drawer on phones and a popover under the chip from `md` up.
 * Renders nothing until a chart exists.
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
  const scope = useAccountRequestScope();
  const signedIn = Boolean(scope.userId);
  const {
    data: profiles,
    isPending: profilesPending,
    isError: profilesFailed,
  } = useChartProfiles(signedIn && hasChart);
  const {
    mutate: openProfile,
    reset: resetOpenProfile,
    isPending: isOpening,
    isError: openFailed,
    error: openError,
    variables: openingProfile,
  } = useMutation(openChartProfileMutationOptions(scope));
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const isWide = useSyncExternalStore(
    subscribeWidth,
    () => window.matchMedia(WIDE_QUERY).matches,
    () => false,
  );

  // Casting is where a chart gets replaced; a switcher there would compete with the form.
  if (!hasChart || birth === null || pathname === AN_SAO_ROUTE) return null;

  const saved = profiles?.chart_profiles ?? [];
  const current =
    saved.find((profile) => profile.id === profileId) ??
    saved.find((profile) => sameBirth(profile.birth_info, birth));
  const dateLabel = profileDisplayName(birth);
  const currentName = current?.display_name ?? dateLabel;
  const chipDetail =
    currentName === dateLabel ? birthDetail(birth) : `${dateLabel} · ${birthDetail(birth)}`;
  const others = saved.filter((profile) => profile.id !== current?.id);
  const query = normalize(search);
  const matches = others.filter((profile) =>
    normalize(`${profile.display_name} ${profileDisplayName(profile.birth_info)}`).includes(query),
  );
  const openingId = isOpening ? openingProfile.id : null;

  const changeOpen = (next: boolean) => {
    if (isOpening) return;
    setOpen(next);
    if (!next) {
      setSearch("");
      resetOpenProfile();
    }
  };

  const switchTo = (profile: ChartProfile) => {
    if (isOpening) return;
    // The mutation activates the chart; here only the UI work.
    openProfile(profile, {
      onSuccess: () => {
        setOpen(false);
        setSearch("");
        resetOpenProfile();
        showToast(`Đang xem lá số ${profile.display_name} ✦`);
      },
    });
  };

  const castAnother = () => {
    setOpen(false);
    router.push(AN_SAO_ROUTE);
  };

  const chip = (
    <button
      type="button"
      aria-haspopup="dialog"
      aria-expanded={open}
      aria-label={`Lá số đang xem: ${currentName}. Đổi lá số`}
      className={cn(
        "pill-ghost inline-flex min-h-11 max-w-full min-w-0 cursor-pointer items-center gap-2 rounded-full py-1 pr-3 pl-1.5 text-left transition-colors hover:border-accent focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent lg:min-h-10",
        className,
      )}
      onClick={isWide ? undefined : () => changeOpen(true)}
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
        <div className="min-h-0">
          <SectionLabel>Lá số đã lưu</SectionLabel>
          {others.length >= SEARCH_THRESHOLD ? (
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Tìm tên hoặc ngày sinh…"
              aria-label="Tìm lá số đã lưu"
              className="mt-1.5 min-h-11 w-full rounded-[14px] border border-glass-line bg-white/6 px-3.5 text-[13px] text-ink outline-none placeholder:text-muted focus:border-accent"
            />
          ) : null}
          {profilesPending ? (
            <p className="px-1 py-3 text-[13px] text-muted" role="status">
              Đang tải lá số đã lưu…
            </p>
          ) : profilesFailed ? (
            <p className="px-1 py-3 text-[13px] text-muted">Không tải được danh sách lá số.</p>
          ) : others.length === 0 ? (
            <p className="px-1 py-3 text-[13px] text-muted">
              Chưa có lá số nào khác. An thêm lá số cho người thân để đổi qua lại ở đây.
            </p>
          ) : matches.length === 0 ? (
            <p className="px-1 py-3 text-[13px] text-muted">Không tìm thấy lá số phù hợp.</p>
          ) : (
            <ul className="mt-1.5 max-h-[min(264px,36dvh)] overflow-y-auto overscroll-contain">
              {matches.map((profile) => (
                <li key={profile.id}>
                  <button
                    type="button"
                    disabled={isOpening}
                    onClick={() => switchTo(profile)}
                    className="flex min-h-14 w-full cursor-pointer items-center gap-3 rounded-2xl px-3 py-2 text-left transition-colors hover:bg-white/6 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent disabled:cursor-wait disabled:opacity-60"
                  >
                    <Avatar name={profile.display_name} quiet />
                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-semibold">
                        {profile.display_name}
                      </span>
                      <span className="block truncate text-xs text-muted">
                        {profileDisplayName(profile.birth_info)} · {birthDetail(profile.birth_info)}
                      </span>
                    </span>
                    {openingId === profile.id ? (
                      <span className="shrink-0 text-xs text-accent" role="status">
                        Đang mở…
                      </span>
                    ) : null}
                  </button>
                </li>
              ))}
            </ul>
          )}
          {openFailed ? (
            <p role="alert" className="px-1 pt-1 text-[13px] text-fire">
              {isApiError(openError)
                ? describe(openError.error)
                : "Không mở được lá số. Bạn thử lại nhé."}
            </p>
          ) : null}
        </div>
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
          onClick={castAnother}
          disabled={isOpening}
          className="pill-primary inline-flex min-h-12 w-full cursor-pointer items-center justify-center gap-2 rounded-full border-0 px-5 text-sm font-semibold transition-transform active:scale-[0.97] disabled:pointer-events-none disabled:opacity-40"
        >
          <span aria-hidden="true">＋</span> An lá số mới
        </button>
        {signedIn ? (
          <Link
            href="/ho-so"
            onClick={() => setOpen(false)}
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
      <Popover.Root open={open} onOpenChange={changeOpen}>
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
      <Drawer open={open} onOpenChange={changeOpen}>
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

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-1 text-[10px] font-bold tracking-[0.22em] text-muted uppercase">
      {children}
    </div>
  );
}

/** The name's first letter; auto-named charts start with a digit and get the star. */
function Avatar({ name, quiet = false }: { name: string; quiet?: boolean }) {
  const first = name.trim().charAt(0);
  const initial = /\p{L}/u.test(first) ? first.toLocaleUpperCase("vi") : "✦";
  return (
    <span
      aria-hidden="true"
      className={cn(
        "grid size-8 shrink-0 place-items-center rounded-full text-[13px] font-semibold",
        quiet ? "bg-white/8 text-ink" : "accent-gradient text-bg-0 shadow-none",
      )}
    >
      {initial}
    </span>
  );
}
