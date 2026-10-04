"use client";

import { useAccountRequestScope } from "@/lib/api/account-request";
import { useAccountAccess } from "@/lib/api/hooks";

import styles from "./balance-badge.module.css";

const BADGE_CLASS = `${styles.badge} inline-flex min-h-9 min-w-0 items-center gap-2 rounded-full px-3 text-xs font-bold`;

export function BalanceBadge() {
  const { userId } = useAccountRequestScope();
  return userId ? <AccountBalance /> : null;
}

function AccountBalance() {
  const account = useAccountAccess();

  if (account.isError) {
    return (
      <button
        type="button"
        className={`${BADGE_CLASS} cursor-pointer border-0 disabled:opacity-50`}
        title="Không tải được số dư. Bấm để thử lại."
        disabled={account.isFetching}
        onClick={() => void account.refetch()}
      >
        <span className="min-w-0 truncate">Thử lại</span>
      </button>
    );
  }

  if (account.data === undefined) {
    return (
      <span className={BADGE_CLASS} role="status">
        <span className="min-w-0 truncate">Số dư…</span>
      </span>
    );
  }

  const unlocked = account.data.plan === "full_unlock";
  const label = unlocked ? "Mở khóa toàn bộ" : `${account.data.balance.toLocaleString("vi-VN")} xu`;
  return (
    <span
      className={`${BADGE_CLASS} ${unlocked ? styles.fullUnlock : styles.coins}`}
      role="status"
      aria-label={unlocked ? "Mở khóa toàn bộ" : "Số dư tài khoản"}
      aria-busy={account.isFetching}
      title={unlocked ? "Mở khóa toàn bộ · Bao gồm trò chuyện với AI." : `Gói Cơ bản · ${label}`}
    >
      <svg
        viewBox="0 0 24 24"
        className={unlocked ? "size-[18px] shrink-0" : "size-3 shrink-0"}
        fill={unlocked ? "none" : "currentColor"}
        stroke={unlocked ? "currentColor" : "none"}
        strokeWidth={1.8}
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        {unlocked ? (
          <>
            <path d="m3 6 4.5 4L12 4l4.5 6L21 6l-2 11H5L3 6Z" />
            <path d="M6 20h12" />
          </>
        ) : (
          <path d="m12 1 9 11-9 11-9-11 9-11Z" />
        )}
      </svg>
      <span className="min-w-0 truncate tabular-nums">{label}</span>
    </span>
  );
}
