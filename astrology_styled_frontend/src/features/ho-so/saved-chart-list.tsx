"use client";

import { useState, useSyncExternalStore } from "react";

import type { ChartProfile } from "@/lib/api/schemas";

import { SavedChartCard } from "./saved-chart-card";

const TABLET_QUERY = "(min-width: 768px)";
const PAGE_BUTTON_CLASS =
  "pill-ghost min-h-11 cursor-pointer rounded-full px-3 text-[13px] disabled:pointer-events-none disabled:opacity-40";

function subscribeWidth(onChange: () => void) {
  const media = window.matchMedia(TABLET_QUERY);
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
}

function normalizeSearch(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/đ/g, "d")
    .replace(/\s+/g, " ");
}

interface SavedChartListProps {
  profiles: ChartProfile[];
}

export function SavedChartList({ profiles }: SavedChartListProps) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pageDraft, setPageDraft] = useState<string | null>(null);
  const isTablet = useSyncExternalStore(
    subscribeWidth,
    () => window.matchMedia(TABLET_QUERY).matches,
    () => false,
  );
  const pageSize = isTablet ? 4 : 3;
  const query = normalizeSearch(search);
  const matches = profiles.filter((profile) => {
    const { day, month, year } = profile.birth_info;
    const date = `${String(day).padStart(2, "0")}/${String(month).padStart(2, "0")}/${year}`;
    return normalizeSearch(`${profile.display_name} ${date}`).includes(query);
  });
  const pageCount = Math.max(1, Math.ceil(matches.length / pageSize));
  const currentPage = Math.min(page, pageCount);
  const offset = (currentPage - 1) * pageSize;
  const visible = matches.slice(offset, offset + pageSize);
  const draftValue = (pageDraft ?? String(currentPage)).trim();
  const targetPage = Number(draftValue);
  const validPage =
    /^\d+$/.test(draftValue) &&
    Number.isSafeInteger(targetPage) &&
    targetPage >= 1 &&
    targetPage <= pageCount;
  const pageError = pageDraft !== null && !validPage;

  function goToPage(nextPage: number) {
    setPage(nextPage);
    setPageDraft(null);
  }

  function submitPage() {
    if (validPage) goToPage(targetPage);
  }

  function changeSearch(value: string) {
    setSearch(value);
    goToPage(1);
  }

  return (
    <div>
      <label htmlFor="saved-chart-search" className="sr-only">
        Tìm lá số
      </label>
      <div className="mb-4 flex min-h-12 items-center gap-2 rounded-[16px] border border-glass-line bg-white/6 px-3.5 focus-within:border-accent focus-within:ring-2 focus-within:ring-accent-glow">
        <svg
          viewBox="0 0 24 24"
          className="h-5 w-5 shrink-0 fill-none stroke-current text-muted"
          aria-hidden="true"
        >
          <circle cx="10.5" cy="10.5" r="6.5" />
          <path d="m16 16 4.5 4.5" />
        </svg>
        <input
          id="saved-chart-search"
          type="search"
          value={search}
          onChange={(event) => changeSearch(event.target.value)}
          placeholder="Tìm tên hoặc ngày sinh…"
          className="min-h-11 min-w-0 flex-1 bg-transparent text-[13px] text-ink outline-none placeholder:text-muted"
        />
        {search && (
          <button
            type="button"
            aria-label="Xóa tìm kiếm"
            onClick={() => changeSearch("")}
            className="min-h-11 min-w-11 cursor-pointer text-xl text-muted"
          >
            ×
          </button>
        )}
      </div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <p className="text-xs text-muted" role="status">
          {matches.length ? `${offset + 1}–${offset + visible.length} / ${matches.length}` : "0"} lá
          số{query ? " phù hợp" : ""}
        </p>
        {pageCount > 1 && (
          <nav
            aria-label="Phân trang lá số"
            className="grid min-w-0 grid-cols-[4.5rem_minmax(0,1fr)_4.5rem] items-center gap-2"
          >
            <button
              type="button"
              aria-label="Trang trước"
              className={PAGE_BUTTON_CLASS}
              disabled={currentPage === 1}
              onClick={() => goToPage(currentPage - 1)}
            >
              Trước
            </button>
            <label
              htmlFor="saved-chart-page"
              className="pill-ghost flex min-h-11 cursor-text items-center justify-center gap-1 rounded-full px-3 text-[13px] tabular-nums focus-within:ring-2 focus-within:ring-accent-glow"
            >
              <input
                id="saved-chart-page"
                type="text"
                inputMode="numeric"
                enterKeyHint="go"
                autoComplete="off"
                aria-label="Số trang"
                aria-invalid={pageError}
                aria-describedby={pageError ? "saved-chart-page-error" : undefined}
                value={pageDraft ?? String(currentPage)}
                onFocus={(event) => event.currentTarget.select()}
                onChange={(event) => setPageDraft(event.target.value)}
                onBlur={submitPage}
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    submitPage();
                  }
                }}
                className="min-h-11 w-7 shrink-0 bg-transparent p-0 text-center text-ink outline-none"
              />
              <span className="text-muted">/</span>
              <span className="w-7 shrink-0 text-center text-muted">{pageCount}</span>
            </label>
            <button
              type="button"
              aria-label="Trang sau"
              className={PAGE_BUTTON_CLASS}
              disabled={currentPage === pageCount}
              onClick={() => goToPage(currentPage + 1)}
            >
              Sau
            </button>
          </nav>
        )}
      </div>
      {pageError && pageCount > 1 && (
        <p id="saved-chart-page-error" role="alert" className="mb-3 text-xs text-fire">
          Nhập số nguyên từ 1 đến {pageCount}.
        </p>
      )}
      <div className="grid min-w-0 gap-3 py-1 md:grid-cols-2 md:gap-[14px] lg:grid-cols-1">
        {visible.map((profile) => (
          <SavedChartCard key={profile.id} profile={profile} />
        ))}
      </div>
      {matches.length === 0 && (
        <p className="py-4 text-[13px] text-muted">
          Không tìm thấy lá số. Thử tên hoặc năm sinh khác.
        </p>
      )}
    </div>
  );
}
