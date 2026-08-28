"use client";

import type { ReactNode } from "react";

import { useRecastGuard } from "@/components/shell/recast-guard";
import { useToastStore } from "@/store/toast-store";

const COMING_SOON = "Tính năng sẽ sớm được cập nhật ✦";

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
 * Bản mệnh share row. "Nhập lại ngày sinh" and "Bắt đầu lại từ đầu" both run
 * the recast guard — one path, not two — so a cast chart is discarded behind
 * the same confirm as every other recast.
 */
export function SettingsList() {
  const showToast = useToastStore((state) => state.show);
  const { requestRecast, confirmDialog } = useRecastGuard();

  const rows: SettingRow[] = [
    {
      title: "Giao diện",
      subtitle: "Luminous Twilight · theo hành mệnh",
      action: () => showToast(COMING_SOON),
      icon: (
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 3v2M12 19v2M5 12H3M21 12h-2" />
          <circle cx="12" cy="12" r="4" />
        </svg>
      ),
    },
    {
      title: "Nhắc nhở vận hạn",
      subtitle: "Mỗi sáng một lời từ Nghê Sao",
      action: () => showToast(COMING_SOON),
      icon: (
        <svg viewBox="0 0 24 24" fill="none">
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
        <svg viewBox="0 0 24 24" fill="none">
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
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
          <path d="m16 17 5-5-5-5M21 12H9" />
        </svg>
      ),
    },
  ];

  return (
    <>
      <div className="list glass">
        {rows.map((row) => (
          <button key={row.title} type="button" className="li" onClick={row.action}>
            {row.icon}
            <span className="t">
              <b>{row.title}</b>
              <small>{row.subtitle}</small>
            </span>
            <span className="chev" aria-hidden="true">
              ›
            </span>
          </button>
        ))}
      </div>
      <div className="center mt-5">
        <button type="button" className="skip" onClick={requestRecast}>
          Bắt đầu lại từ đầu
        </button>
      </div>
      {confirmDialog}
    </>
  );
}
