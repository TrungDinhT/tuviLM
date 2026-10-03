"use client";

import { useState } from "react";

import { Dialog, DialogClose } from "@/components/primitives/dialog";
import { Pill } from "@/components/primitives/pill";
import { usePreferencesStore } from "@/store/preferences-store";

interface BirthConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** The restated birth data, e.g. "15 · 04 · 1996 · 10:05 AM · Giờ Tỵ". */
  summary: string;
  onConfirm: () => void;
}

/**
 * The last check before casting. Skippable durably via "Không nhắc lại",
 * persisted by the preferences store under `tuvi.muteBirthConfirm`.
 */
export function BirthConfirmDialog({
  open,
  onOpenChange,
  summary,
  onConfirm,
}: BirthConfirmDialogProps) {
  const [muted, setMuted] = useState(false);
  const setMuteBirthConfirm = usePreferencesStore((state) => state.setMuteBirthConfirm);

  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      title="Xác nhận ngày sinh"
      footer={
        <div className="mt-[22px] grid grid-cols-2 gap-[10px]">
          <DialogClose asChild>
            <Pill variant="ghost" className="w-full px-[10px] py-[13px] text-[14.5px]">
              Sửa lại
            </Pill>
          </DialogClose>
          <Pill
            className="w-full px-[10px] py-[13px] text-[14.5px]"
            onClick={() => {
              if (muted) setMuteBirthConfirm(true);
              onConfirm();
            }}
          >
            Đúng rồi, an sao
          </Pill>
        </div>
      }
    >
      <p className="mt-3 text-center font-display text-[21px] font-semibold text-accent">
        {summary}
      </p>
      <p className="mt-[11px] text-[13.5px] leading-relaxed text-muted">
        Lá số sẽ được an theo đúng ngày giờ này. Sau này muốn đổi, bạn vào tab <b>Hồ sơ</b> →{" "}
        <b>Nhập lại ngày sinh</b>.
      </p>
      <label className="mt-4 inline-flex w-full cursor-pointer items-center justify-center gap-[9px] text-[13.5px] text-muted">
        <input
          type="checkbox"
          checked={muted}
          onChange={(event) => setMuted(event.target.checked)}
          className="h-[17px] w-[17px] shrink-0 cursor-pointer accent-(--accent)"
        />
        <span>Không nhắc lại</span>
      </label>
    </Dialog>
  );
}
