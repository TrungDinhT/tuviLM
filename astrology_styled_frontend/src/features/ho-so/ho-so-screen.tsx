"use client";

import type { ReactNode } from "react";
import Link from "next/link";

import { Pill } from "@/components/primitives/pill";
import { SignOutButton } from "@/components/shell/sign-out-button";
import { ADMIN_REDEEM_CODES_ROUTE } from "@/config/site";
import { useAccountAccess, useChartProfiles } from "@/lib/api/hooks";
import { authClient } from "@/lib/auth-client";
import { describe, isApiError } from "@/lib/http/errors";

import styles from "./ho-so-screen.module.css";
import { RedeemCodeForm } from "./redeem-code-form";
import { SavedChartSkeleton } from "./saved-chart-card";
import { SavedChartList } from "./saved-chart-list";
import { SettingsList } from "./settings-list";

const SAVED_RAIL_CLASS = "grid min-w-0 gap-3 py-1 md:grid-cols-2 md:gap-[14px] lg:grid-cols-1";

/**
 * The Hồ sơ body — saved charts and settings. The header is
 * the shared `StickyHeader` mounted by the page, like every other tab.
 */
export function HoSoScreen() {
  const { data: session, isPending } = authClient.useSession();
  const profiles = useChartProfiles(Boolean(session));
  const account = useAccountAccess();
  const isAdmin =
    session &&
    account.isSuccess &&
    !account.isFetching &&
    account.data.user_id === session.user.id &&
    account.data.role === "admin";

  return (
    <div className="lg:grid lg:grid-cols-2 lg:items-start lg:gap-x-[30px]">
      <div className={styles.enterSaved}>
        <div className="mx-[2px] mt-[26px] mb-[12px] flex items-baseline justify-between">
          <h2 className="text-[22px] font-semibold">Lá số đã lưu</h2>
        </div>
        {renderSaved()}
      </div>
      <div className={styles.enterSettings}>
        <div className="mx-[2px] mt-[26px] mb-[12px] flex items-baseline justify-between">
          <h2 className="text-[22px] font-semibold">Cài đặt</h2>
        </div>
        <SettingsList />
        {session && (
          <SignOutButton className="pill-ghost mt-3 min-h-11 w-full justify-center rounded-2xl px-4 py-3 text-sm font-semibold lg:hidden" />
        )}
        {isAdmin && (
          <Link
            href={ADMIN_REDEEM_CODES_ROUTE}
            className="glass mt-5 flex items-center justify-between gap-3 p-4 text-sm no-underline"
          >
            <span className="font-semibold">Tạo mã nhận xu</span>
            <span className="text-xs text-accent">Quản trị ›</span>
          </Link>
        )}
        {session && <RedeemCodeForm />}
      </div>
    </div>
  );

  function renderSaved(): ReactNode {
    if (!session && !isPending) {
      return (
        <div className="flex flex-col items-start gap-3">
          <p className="text-[13.5px] text-muted">Đăng nhập để xem và lưu lá số của bạn.</p>
          <Link
            href="/login"
            className="pill-ghost rounded-full px-4 py-2 text-[13px] font-semibold no-underline"
          >
            Đăng nhập
          </Link>
        </div>
      );
    }
    if (isPending || profiles.isPending) {
      return (
        <div className={SAVED_RAIL_CLASS} role="status" aria-label="Đang tải lá số đã lưu">
          {Array.from({ length: 3 }, (_, index) => (
            <SavedChartSkeleton key={index} />
          ))}
        </div>
      );
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
    return <SavedChartList profiles={data.chart_profiles} />;
  }
}
