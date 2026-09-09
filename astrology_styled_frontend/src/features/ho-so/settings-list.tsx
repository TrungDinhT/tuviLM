"use client";

import type { ReactNode } from "react";

import { useRecastGuard } from "@/components/shell/recast-guard";
import { showToast } from "@/lib/toast";

const COMING_SOON = "Tính năng sẽ sớm được cập nhật ✦";

const ICON_CLASS = "h-[22px] w-[22px] shrink-0 fill-none [stroke:var(--accent)] [stroke-width:1.5]";

interface SettingRow {
  title: string;
  subtitle: string;
  icon: ReactNode;
  action: () => void;
}

/**
 * The "Cài đặt" list.
 *
 * Three rows are not built yet and raise the coming-soon toast, matching the
 * Bản mệnh share row. "Nhập lại ngày sinh" runs the shared recast guard, so a
 * cast chart is discarded behind the same confirm as every other recast.
 */
export function SettingsList() {
  const { requestRecast, confirmDialog } = useRecastGuard();

  const rows: SettingRow[] = [
    {
      title: "Giao diện",
      subtitle: "Luminous Twilight · theo hành mệnh",
      action: () => showToast(COMING_SOON),
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className={ICON_CLASS}>
          <path d="M12 3v2M12 19v2M5 12H3M21 12h-2" />
          <circle cx="12" cy="12" r="4" />
        </svg>
      ),
    },
    {
      title: "Nhắc nhở vận hạn",
      subtitle: "Mỗi sáng một lời từ Thiên Hạc",
      action: () => showToast(COMING_SOON),
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className={ICON_CLASS}>
          <path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.7 21a2 2 0 0 1-3.4 0" />
        </svg>
      ),
    },
    {
      title: "Ảnh chia sẻ",
      subtitle: "Xuất lá bài dạng story 9:16",
      action: () => showToast(COMING_SOON),
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className={ICON_CLASS}>
          <path d="M4 4h16v12H4z" />
          <path d="m4 16 5-5 3 3 4-4 4 4" />
        </svg>
      ),
    },
    {
      title: "Nhập lại ngày sinh",
      subtitle: "Xoay lại cỗ máy vũ trụ",
      action: requestRecast,
      icon: (
        <svg viewBox="0 0 24 24" fill="none" className={ICON_CLASS}>
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <path d="m16 17 5-5-5-5M21 12H9" />
        </svg>
      ),
    },
  ];

  return (
    <>
      <div className="glass flex flex-col gap-[2px] overflow-hidden p-[6px]">
        {rows.map((row) => (
          <button
            key={row.title}
            type="button"
            className="flex w-full cursor-pointer items-center gap-[14px] rounded-[16px] border-0 px-[14px] py-[15px] text-left text-ink transition-[background] duration-200 hover:bg-white/4"
            onClick={row.action}
          >
            {row.icon}
            <span className="flex-1">
              <b className="text-[15px] font-medium">{row.title}</b>
              <small className="mt-[2px] block text-xs text-muted">{row.subtitle}</small>
            </span>
            <span className="text-muted" aria-hidden="true">
              ›
            </span>
          </button>
        ))}
      </div>
      {confirmDialog}
    </>
  );
}
