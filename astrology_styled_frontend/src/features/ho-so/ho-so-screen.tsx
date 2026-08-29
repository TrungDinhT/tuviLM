"use client";

import type { ReactNode } from "react";

import { Pill } from "@/components/primitives/pill";
import { useChartProfiles } from "@/lib/api/hooks";
import { describe, isApiError } from "@/lib/http/errors";

import { SavedChartCard } from "./saved-chart-card";
import { SettingsList } from "./settings-list";

/**
 * The Hồ sơ body — saved charts (read + delete) and settings. The header is
 * the shared `StickyHeader` mounted by the page, like every other tab.
 */
export function HoSoScreen() {
  const profiles = useChartProfiles();

  return (
    <div className="lg:grid lg:grid-cols-[minmax(0,1fr)_380px] lg:items-start lg:gap-x-[30px]">
      <div>
        <div className="mx-[2px] mt-[26px] mb-[12px] flex items-baseline justify-between">
          <h2 className="text-[22px] font-semibold">Lá số đã lưu</h2>
        </div>
        {renderSaved()}
      </div>
      <div>
        <div className="mx-[2px] mt-[26px] mb-[12px] flex items-baseline justify-between">
          <h2 className="text-[22px] font-semibold">Cài đặt</h2>
        </div>
        <SettingsList />
      </div>
    </div>
  );

  function renderSaved(): ReactNode {
    if (profiles.isPending) {
      return <p className="text-[13.5px] text-muted">Đang tải lá số đã lưu…</p>;
    }
    if (profiles.isError) {
      const message = isApiError(profiles.error)
        ? describe(profiles.error.error)
        : "Không tải được danh sách lá số.";
      return (
        <div className="flex items-center gap-3">
          <p className="text-[13.5px] text-muted">{message}</p>
          <Pill
            variant="ghost"
            className="px-3.5 py-2 text-[13px]"
            onClick={() => void profiles.refetch()}
          >
            Thử lại
          </Pill>
        </div>
      );
    }
    const data = profiles.data;
    if (data === undefined) return null;
    if (data.chart_profiles.length === 0) {
      return <p className="text-[13.5px] text-muted">Chưa có lá số nào được lưu.</p>;
    }
    return (
      <div className="flex gap-3 overflow-x-auto py-1 lg:grid lg:grid-cols-3 lg:gap-[14px] lg:overflow-visible">
        {data.chart_profiles.map((profile) => (
          <SavedChartCard key={profile.id} profile={profile} />
        ))}
      </div>
    );
  }
}
