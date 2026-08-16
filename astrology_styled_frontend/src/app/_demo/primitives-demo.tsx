"use client";

import { useState } from "react";

import { Dialog, DialogClose } from "@/components/primitives/dialog";
import { Pill } from "@/components/primitives/pill";
import { useToastStore } from "@/store/toast-store";

/**
 * Scaffolding, not product. Exercises every primitive so the foundation can be
 * checked in a browser before any screen exists. Delete alongside `_demo/`.
 */
export function PrimitivesDemo() {
  const [centerOpen, setCenterOpen] = useState(false);
  const [panelOpen, setPanelOpen] = useState(false);
  const showToast = useToastStore((state) => state.show);

  return (
    <section className="mt-8">
      <h2 className="font-display text-xl font-semibold">Primitives</h2>

      <div className="mt-4 flex flex-wrap gap-3">
        <Pill onClick={() => showToast("Đã tạo ảnh story ✦ lá bài của bạn đã sẵn sàng!")}>
          Pill chính
        </Pill>
        <Pill variant="ghost" onClick={() => setCenterOpen(true)}>
          Hộp xác nhận
        </Pill>
        <Pill variant="ghost" onClick={() => setPanelOpen(true)}>
          Panel chi tiết
        </Pill>
        <Pill variant="ghost" disabled>
          Đang khoá
        </Pill>
      </div>

      <div className="glass mt-4 p-5">
        <p className="text-sm text-muted">
          Bề mặt <code className="text-ink">glass</code> — nền, viền tóc, bo góc và blur trong một
          utility.
        </p>
      </div>

      <Dialog
        open={centerOpen}
        onOpenChange={setCenterOpen}
        variant="center"
        title="An sao lại từ đầu?"
        description="Toàn bộ lá số hiện tại sẽ bị xoá — lá bài bản mệnh, vận hạn, thiên bàn, lá số 12 cung và cuộc trò chuyện đều trở lại từ đầu."
      >
        <div className="mt-[22px] grid grid-cols-2 gap-2.5">
          <DialogClose asChild>
            <Pill variant="ghost" className="w-full px-2.5 py-[13px] text-[14.5px]">
              Ở lại
            </Pill>
          </DialogClose>
          <DialogClose asChild>
            <Pill className="w-full px-2.5 py-[13px] text-[14.5px]">An sao lại</Pill>
          </DialogClose>
        </div>
      </Dialog>

      <Dialog
        open={panelOpen}
        onOpenChange={setPanelOpen}
        variant="panel"
        title="Cung Mệnh"
        description="Toàn màn hình ở mobile và tablet; từ lg thành ngăn kéo neo phải, bỏ hẳn lớp che."
        footer={
          <DialogClose asChild>
            <Pill variant="ghost" className="w-full">
              Đóng
            </Pill>
          </DialogClose>
        }
      >
        <div className="mt-4 space-y-3">
          {Array.from({ length: 30 }, (_, i) => (
            <p key={i} className="text-[13px] text-muted">
              Dòng {i + 1} — nội dung dài để kiểm tra cuộn bên trong panel.
            </p>
          ))}
        </div>
      </Dialog>
    </section>
  );
}
