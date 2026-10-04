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
        title="Unable to load current balance. Retry."
        disabled={account.isFetching}
        onClick={() => void account.refetch()}
      >
        Retry balance
      </button>
    );
  }

  if (account.data === undefined) {
    return (
      <span className={BADGE_CLASS} role="status">
        Balance…
      </span>
    );
  }

  const unlocked = account.data.plan === "full_unlock";
  const label = unlocked ? "Full unlock" : `${account.data.balance.toLocaleString("en-US")} coins`;
  return (
    <span
      className={`${BADGE_CLASS} ${unlocked ? styles.fullUnlock : styles.coins}`}
      role="status"
      aria-label={unlocked ? "Full unlock" : "Account balance"}
      aria-busy={account.isFetching}
      title={unlocked ? "Full unlock · AI chat included." : `Plan: Normal · ${label}`}
    >
      <svg
        viewBox="0 0 24 24"
        className="size-[18px] shrink-0"
        fill="none"
        stroke="currentColor"
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
          <>
            <circle cx="12" cy="12" r="8.5" />
            <path d="m12 7 3 5-3 5-3-5 3-5Z" />
          </>
        )}
      </svg>
      <span className="max-w-[11ch] truncate tabular-nums lg:max-w-none">{label}</span>
    </span>
  );
}
