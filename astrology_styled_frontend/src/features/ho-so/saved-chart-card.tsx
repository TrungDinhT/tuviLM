"use client";

import { type FormEvent, useState } from "react";

import { Dialog, DialogClose } from "@/components/primitives/dialog";
import { Pill } from "@/components/primitives/pill";
import { canhGioOf, MERIDIEM } from "@/features/an-sao/birth-time";
import { useDeleteChartProfile, useRenameChartProfile } from "@/lib/api/hooks";
import type { ChartProfile } from "@/lib/api/schemas";
import { describe, isApiError } from "@/lib/http/errors";
import { showToast } from "@/lib/toast";

const CARD_LAYOUT = "flex min-h-[128px] w-full min-w-0 flex-row items-center gap-3 p-4 lg:gap-4";

/** The profile's own stored birth data, formatted for display — not a reading. */
function dateLabel(profile: ChartProfile): string {
  const { year, month, day } = profile.birth_info;
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(day)}/${pad(month)}/${year}`;
}

interface SavedChartCardProps {
  profile: ChartProfile;
  onOpen: (profile: ChartProfile) => void;
}

export function SavedChartCard({ profile, onOpen }: SavedChartCardProps) {
  const [dialog, setDialog] = useState<"rename" | "delete" | null>(null);
  const [draftName, setDraftName] = useState("");
  const deleteProfile = useDeleteChartProfile();
  const renameProfile = useRenameChartProfile();
  const name = profile.display_name;
  const hour = profile.birth_info.hour;
  const canh = canhGioOf(hour % 12 || 12, hour < 12 ? MERIDIEM.AM : MERIDIEM.PM);
  const pending = deleteProfile.isPending || renameProfile.isPending;

  function saveName(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const displayName = draftName.trim();
    if (!displayName || pending) return;
    renameProfile.mutate(
      { id: profile.id, display_name: displayName },
      { onSuccess: () => setDialog(null) },
    );
  }

  const confirmDelete = () => {
    setDialog(null);
    deleteProfile.mutate(profile.id, {
      onError: (error) => {
        if (isApiError(error)) showToast(describe(error.error));
      },
    });
  };

  return (
    <article
      className={`${CARD_LAYOUT} relative rounded-[20px] border border-accent-glow bg-[linear-gradient(160deg,color-mix(in_srgb,var(--accent)_18%,transparent),rgba(46,26,74,0.5))]`}
    >
      <button
        type="button"
        aria-label={`Mở lá số ${name}`}
        disabled={pending}
        onClick={() => onOpen(profile)}
        className="absolute inset-0 cursor-pointer rounded-[20px] outline-none hover:bg-white/4 focus-visible:ring-2 focus-visible:ring-accent disabled:pointer-events-none"
      />
      <div className="pointer-events-none relative min-w-0 flex-1">
        <h3 className="font-display text-[19px] leading-snug font-semibold [overflow-wrap:anywhere]">
          {name}
        </h3>
        <div className="mt-3 space-y-1 text-[13px] text-muted">
          <p>Ngày sinh: {dateLabel(profile)}</p>
          <p>
            Giờ sinh: {canh.chi} · {canh.range}
          </p>
        </div>
      </div>
      <div className="relative flex shrink-0 flex-col gap-2">
        <button
          type="button"
          className="pill-ghost min-h-11 cursor-pointer rounded-full px-4 text-[13px] font-semibold disabled:pointer-events-none disabled:opacity-40"
          aria-label={`Đổi tên lá số ${name}`}
          disabled={pending}
          onClick={() => {
            setDraftName(name);
            renameProfile.reset();
            setDialog("rename");
          }}
        >
          Đổi tên
        </button>
        <button
          type="button"
          className="pill-ghost min-h-11 cursor-pointer rounded-full px-4 text-[13px] text-muted disabled:pointer-events-none disabled:opacity-40"
          aria-label={`Xoá lá số ${name}`}
          disabled={pending}
          onClick={() => setDialog("delete")}
        >
          Xoá
        </button>
      </div>

      <Dialog
        open={dialog === "rename"}
        onOpenChange={(open) => {
          if (!pending) setDialog(open ? "rename" : null);
        }}
        title="Đổi tên lá số"
        description="Đặt một tên dễ nhớ cho lá số của bạn."
      >
        <form className="mt-5" onSubmit={saveName}>
          <label htmlFor={`chart-name-${profile.id}`} className="text-sm font-medium">
            Tên lá số
          </label>
          <input
            id={`chart-name-${profile.id}`}
            value={draftName}
            onChange={(event) => {
              setDraftName(event.target.value);
              renameProfile.reset();
            }}
            maxLength={80}
            required
            disabled={pending}
            className="mt-2 min-h-[50px] w-full rounded-[14px] border border-glass-line bg-bg-1 px-3.5 py-3 text-[15px] text-ink outline-none focus:border-accent focus:ring-2 focus:ring-accent-glow"
          />
          <p className="mt-2 text-xs leading-relaxed text-muted">
            Tên trùng sẽ được thêm số để dễ phân biệt.
          </p>
          {renameProfile.isError && (
            <p role="alert" className="mt-3 text-[13px] leading-relaxed text-fire">
              {isApiError(renameProfile.error)
                ? describe(renameProfile.error.error)
                : "Không đổi tên được lá số. Bạn thử lại nhé."}
            </p>
          )}
          <div className="mt-5 grid grid-cols-2 gap-2.5">
            <Pill variant="ghost" disabled={pending} onClick={() => setDialog(null)}>
              Hủy
            </Pill>
            <Pill type="submit" disabled={pending || !draftName.trim()}>
              {renameProfile.isPending ? "Đang lưu…" : "Lưu"}
            </Pill>
          </div>
        </form>
      </Dialog>
      <Dialog
        open={dialog === "delete"}
        onOpenChange={(open) => setDialog(open ? "delete" : null)}
        variant="center"
        title="Xoá lá số này?"
        description={
          <span className="[overflow-wrap:anywhere]">
            Lá số “{name}” sẽ bị xoá khỏi danh sách đã lưu.
          </span>
        }
      >
        <div className="mt-[22px] grid grid-cols-2 gap-2.5">
          <DialogClose asChild>
            <Pill variant="ghost" className="w-full px-2.5 py-[13px] text-[14.5px]">
              Giữ lại
            </Pill>
          </DialogClose>
          <Pill className="w-full px-2.5 py-[13px] text-[14.5px]" onClick={confirmDelete}>
            Xoá
          </Pill>
        </div>
      </Dialog>
    </article>
  );
}

/** Loading placeholder with the same footprint as a saved chart card. */
export function SavedChartSkeleton() {
  return (
    <div
      className={`${CARD_LAYOUT} animate-pulse rounded-[20px] border border-glass-line bg-white/6`}
      aria-hidden="true"
    >
      <div className="min-w-0 flex-1">
        <span className="block h-6 w-3/4 rounded-full bg-white/12" />
        <span className="mt-3 block h-4 w-2/3 rounded-full bg-white/10" />
        <span className="mt-2 block h-4 w-1/2 rounded-full bg-white/10" />
      </div>
      <div className="shrink-0 space-y-2">
        <span className="block h-11 w-20 rounded-full bg-white/10" />
        <span className="block h-11 w-20 rounded-full bg-white/10" />
      </div>
    </div>
  );
}
