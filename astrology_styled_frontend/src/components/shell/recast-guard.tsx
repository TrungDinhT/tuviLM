"use client";

import { useRouter } from "next/navigation";
import { useCallback, useState } from "react";

import { Dialog, DialogClose } from "@/components/primitives/dialog";
import { Pill } from "@/components/primitives/pill";
import { AN_SAO_ROUTE } from "@/config/site";
import { useChartStore } from "@/store/chart-store";

/**
 * Guards the route back to An sao.
 *
 * Going back there means casting again, which throws away the current chart —
 * the deck, the Thiên Bàn selection, the 12-cung grid and the conversation.
 * That is worth a question. The question is skipped when there is nothing to
 * lose: no chart yet, or the user is already on An sao.
 *
 * Usage:
 *
 * ```tsx
 * const { requestRecast, confirmDialog } = useRecastGuard();
 * <button onClick={requestRecast}>Nhập lại ngày sinh</button>
 * {confirmDialog}
 * ```
 */
export function useRecastGuard() {
  const router = useRouter();
  const hasChart = useChartStore((state) => state.hasChart);
  const reset = useChartStore((state) => state.reset);
  const [open, setOpen] = useState(false);

  const goToAnSao = useCallback(() => {
    reset();
    router.push(AN_SAO_ROUTE);
  }, [reset, router]);

  const requestRecast = useCallback(() => {
    if (!hasChart) {
      router.push(AN_SAO_ROUTE);
      return;
    }
    setOpen(true);
  }, [hasChart, router]);

  const confirmDialog = (
    <Dialog
      open={open}
      onOpenChange={setOpen}
      variant="center"
      title="An sao lại từ đầu?"
      description="Lá số đang hiển thị sẽ được đặt lại để bạn nhập thông tin sinh khác. Lịch sử trò chuyện đã lưu theo từng bộ thông tin sinh vẫn được giữ."
    >
      <div className="mt-[22px] grid grid-cols-2 gap-2.5">
        <DialogClose asChild>
          <Pill variant="ghost" className="w-full px-2.5 py-[13px] text-[14.5px]">
            Ở lại
          </Pill>
        </DialogClose>
        <Pill
          className="w-full px-2.5 py-[13px] text-[14.5px]"
          onClick={() => {
            setOpen(false);
            goToAnSao();
          }}
        >
          An sao lại
        </Pill>
      </div>
    </Dialog>
  );

  return { requestRecast, confirmDialog };
}
