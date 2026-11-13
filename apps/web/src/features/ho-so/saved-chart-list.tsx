"use client";

import { useIsMutating, useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { Dialog } from "@/components/primitives/dialog";
import { CastingLoader } from "@/features/an-sao/casting-loader";
import { useMediaQuery } from "@/hooks/use-media-query";
import { useAccountRequestScope } from "@/lib/api/account-request";
import { openChartProfileMutationOptions } from "@/lib/api/chart-profiles";
import { mutationKeys } from "@/lib/api/queryKeys";
import type { ChartProfile } from "@/lib/api/schemas";
import { describe, isApiError } from "@/lib/http/errors";

import { SavedChartCard } from "./saved-chart-card";

const TABLET_QUERY = "(min-width: 768px)";
const PAGE_BUTTON_CLASS =
  "pill-ghost min-h-11 cursor-pointer rounded-full px-3 text-[13px] disabled:pointer-events-none disabled:opacity-40";

const normalizeSearch = (value: string): string =>
  value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/đ/g, "d")
    .replace(/\s+/g, " ");

interface SavedChartListProps {
  profiles: ChartProfile[];
}

export function SavedChartList({ profiles }: SavedChartListProps) {
  const router = useRouter();
  const scope = useAccountRequestScope();
  const { mutate, isPending, isSuccess, isError, error } = useMutation(
    openChartProfileMutationOptions(scope),
  );
  const isOpening = useIsMutating({ mutationKey: mutationKeys.openChartProfile() }) > 0;
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pageDraft, setPageDraft] = useState<string | null>(null);
  const isTablet = useMediaQuery(TABLET_QUERY);
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

  const goToPage = (nextPage: number) => {
    setPage(nextPage);
    setPageDraft(null);
  };

  const submitPage = () => {
    if (validPage) goToPage(targetPage);
  };

  const changeSearch = (value: string) => {
    setSearch(value);
    goToPage(1);
  };

  const openChart = (profile: ChartProfile) => {
    if (isOpening || isSuccess) return;
    // The mutation activates the chart; here only the navigation, which has
    // no meaning once this list is gone.
    mutate(profile, { onSuccess: () => router.push("/ban-menh") });
  };

  return (
    <>
      <Dialog
        open={isPending || isSuccess}
        onOpenChange={() => {}}
        variant="fullscreen"
        title="Đang mở lá số đã lưu"
        description="Đang tải lá số và lịch sử trò chuyện."
      >
        <div role="status" aria-label="Đang mở lá số đã lưu">
          <CastingLoader title="Đang mở lá số" />
        </div>
      </Dialog>
      <div>
        {isError && (
          <p role="alert" className="mb-4 text-[13px] text-fire">
            {isApiError(error) ? describe(error.error) : "Không mở được lá số. Bạn thử lại nhé."}
          </p>
        )}
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
            {matches.length ? `${offset + 1}–${offset + visible.length} / ${matches.length}` : "0"}{" "}
            lá số{query ? " phù hợp" : ""}
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
            <SavedChartCard key={profile.id} profile={profile} onOpen={openChart} />
          ))}
        </div>
        {matches.length === 0 && (
          <p className="py-4 text-[13px] text-muted">
            Không tìm thấy lá số. Thử tên hoặc năm sinh khác.
          </p>
        )}
      </div>
    </>
  );
}
