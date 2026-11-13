"use client";

import { useIsMutating, useMutation } from "@tanstack/react-query";

import { useAccountRequestScope } from "@/lib/api/account-request";
import { openChartProfileMutationOptions, profileDisplayName } from "@/lib/api/chart-profiles";
import { useChartProfiles } from "@/lib/api/hooks";
import { mutationKeys } from "@/lib/api/queryKeys";
import type { ChartProfile } from "@/lib/api/schemas";
import { describe, isApiError } from "@/lib/http/errors";
import { showToast } from "@/lib/toast";

import { Avatar, SectionLabel } from "./parts";
import { birthDetail, normalize } from "./profile-format";

/** Below this many saved charts the list is short enough to scan without a filter. */
const SEARCH_THRESHOLD = 6;

/**
 * The saved charts a signed-in user can switch to, without the one on screen.
 *
 * It owns the mutation that opens a chart. The panel around it unmounts this
 * list when it closes, so a failed open leaves no error behind for the next
 * time the panel opens.
 */
export function SavedProfileList({
  currentId,
  search,
  onSearchChange,
  onSwitched,
}: {
  /** The saved profile of the chart on screen, left out of the list. */
  currentId: string | undefined;
  search: string;
  onSearchChange: (value: string) => void;
  /** UI work after a switch, e.g. close the panel. */
  onSwitched: () => void;
}) {
  const scope = useAccountRequestScope();
  const {
    data: profiles,
    isPending: profilesPending,
    isError: profilesFailed,
  } = useChartProfiles();
  const { mutate, isPending, isError, error, variables } = useMutation(
    openChartProfileMutationOptions(scope),
  );
  const isOpening = useIsMutating({ mutationKey: mutationKeys.openChartProfile() }) > 0;

  const others = (profiles?.chart_profiles ?? []).filter((profile) => profile.id !== currentId);
  const query = normalize(search);
  const matches = others.filter((profile) =>
    normalize(`${profile.display_name} ${profileDisplayName(profile.birth_info)}`).includes(query),
  );
  const openingId = isPending ? variables.id : null;

  // The mutation activates the chart. Only UI work is here; if this list is
  // gone by then, there is no panel left to close.
  const switchTo = (profile: ChartProfile) =>
    mutate(profile, {
      onSuccess: () => {
        onSwitched();
        showToast(`Đang xem lá số ${profile.display_name} ✦`);
      },
    });

  return (
    <div className="min-h-0">
      <SectionLabel>Lá số đã lưu</SectionLabel>
      {others.length >= SEARCH_THRESHOLD ? (
        <input
          type="search"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Tìm tên hoặc ngày sinh…"
          aria-label="Tìm lá số đã lưu"
          className="mt-1.5 min-h-11 w-full rounded-[14px] border border-glass-line bg-white/6 px-3.5 text-[13px] text-ink outline-none placeholder:text-muted focus:border-accent"
        />
      ) : null}
      {profilesPending ? (
        <p className="px-1 py-3 text-[13px] text-muted" role="status">
          Đang tải lá số đã lưu…
        </p>
      ) : profilesFailed ? (
        <p className="px-1 py-3 text-[13px] text-muted">Không tải được danh sách lá số.</p>
      ) : others.length === 0 ? (
        <p className="px-1 py-3 text-[13px] text-muted">
          Chưa có lá số nào khác. An thêm lá số cho người thân để đổi qua lại ở đây.
        </p>
      ) : matches.length === 0 ? (
        <p className="px-1 py-3 text-[13px] text-muted">Không tìm thấy lá số phù hợp.</p>
      ) : (
        <ul className="mt-1.5 max-h-[min(264px,36dvh)] overflow-y-auto overscroll-contain">
          {matches.map((profile) => (
            <li key={profile.id}>
              <button
                type="button"
                disabled={isOpening}
                onClick={() => switchTo(profile)}
                className="flex min-h-14 w-full cursor-pointer items-center gap-3 rounded-2xl px-3 py-2 text-left transition-colors hover:bg-white/6 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-accent disabled:cursor-wait disabled:opacity-60"
              >
                <Avatar name={profile.display_name} quiet />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-semibold">
                    {profile.display_name}
                  </span>
                  <span className="block truncate text-xs text-muted">
                    {profileDisplayName(profile.birth_info)} · {birthDetail(profile.birth_info)}
                  </span>
                </span>
                {openingId === profile.id ? (
                  <span className="shrink-0 text-xs text-accent" role="status">
                    Đang mở…
                  </span>
                ) : null}
              </button>
            </li>
          ))}
        </ul>
      )}
      {isError ? (
        <p role="alert" className="px-1 pt-1 text-[13px] text-fire">
          {isApiError(error) ? describe(error.error) : "Không mở được lá số. Bạn thử lại nhé."}
        </p>
      ) : null}
    </div>
  );
}
