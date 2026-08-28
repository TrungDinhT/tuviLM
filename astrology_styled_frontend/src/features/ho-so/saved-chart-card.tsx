"use client";

import { useState } from "react";

import { Dialog, DialogClose } from "@/components/primitives/dialog";
import { Pill } from "@/components/primitives/pill";
import { useDeleteChartProfile } from "@/lib/api/hooks";
import type { ChartProfile } from "@/lib/api/schemas";
import { describe, isApiError } from "@/lib/http/errors";
import { useToastStore } from "@/store/toast-store";

/** The profile's own stored birth data, formatted for display — not a reading. */
function dateLabel(profile: ChartProfile): string {
  const { year, month, day } = profile.birth_info;
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${pad(day)} · ${pad(month)} · ${year}`;
}

/**
 * One saved lá số in the "Lá số đã lưu" rail.
 *
 * The `display_name` is the title and the birth date is a small label. Delete
 * is destructive and unrecoverable until a save flow exists, so it is gated
 * behind the same confirm-dialog treatment as the recast and birth confirm.
 */
export function SavedChartCard({ profile }: { profile: ChartProfile }) {
  const [open, setOpen] = useState(false);
  const deleteProfile = useDeleteChartProfile();
  const showToast = useToastStore((state) => state.show);

  const confirmDelete = () => {
    setOpen(false);
    deleteProfile.mutate(profile.id, {
      onError: (error) => {
        if (isApiError(error)) showToast(describe(error.error));
      },
    });
  };

  return (
    <div className="savecard">
      <button
        type="button"
        className="savecard-delete"
        aria-label={`Xoá lá số ${profile.display_name}`}
        onClick={() => setOpen(true)}
      >
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M4 7h16M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M10 11v6M14 11v6" />
        </svg>
      </button>
      <span className="dt">{dateLabel(profile)}</span>
      <b>{profile.display_name}</b>

      <Dialog
        open={open}
        onOpenChange={setOpen}
        variant="center"
        title="Xoá lá số này?"
        description={`Lá số “${profile.display_name}” sẽ bị xoá khỏi danh sách đã lưu.`}
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
    </div>
  );
}
