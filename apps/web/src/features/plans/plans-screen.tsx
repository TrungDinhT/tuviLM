"use client";

import { useState } from "react";
import Link from "next/link";

import { Pill } from "@/components/primitives/pill";
import { useAccountRequestScope } from "@/lib/api/account-request";
import { useAccountAccess } from "@/lib/api/hooks";
import { showToast } from "@/lib/toast";

import styles from "./plans-screen.module.css";

const BUNDLES = [30, 90, 180] as const;

export function PlansScreen() {
  const { userId } = useAccountRequestScope();
  const account = useAccountAccess();
  const [selectedCoins, setSelectedCoins] = useState(30);
  const access =
    userId && account.isSuccess && account.data.user_id === userId ? account.data : undefined;
  const fullUnlock = access?.plan === "full_unlock";
  const comingSoon = () => showToast("Tính năng sẽ được cập nhật");

  return (
    <div className={styles.page}>
      <section className="pt-6 pb-7 lg:pt-8 lg:pb-9">
        <h1 className="max-w-[18ch] font-display text-[34px] leading-[1.12] font-semibold md:text-[46px]">
          Một lời giải đáp, đúng lúc bạn cần.
        </h1>
        <p className="mt-4 max-w-[57ch] text-[14px] leading-relaxed text-muted">
          Dùng xu khi cần hỏi riêng lẻ, hoặc chọn gói Mở khóa toàn bộ để trò chuyện với AI không bị
          trừ xu.
        </p>
      </section>

      <div
        className={`grid items-start gap-5 lg:gap-6 ${fullUnlock ? "max-w-[640px]" : "lg:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)]"}`}
      >
        {!fullUnlock ? (
          <section
            className={`${styles.wallet} min-w-0 overflow-hidden rounded-card border border-glass-line`}
            aria-labelledby="wallet-title"
          >
            <div className={`${styles.balance} p-6 md:p-7`} aria-busy={account.isFetching}>
              <div className="flex items-center justify-between gap-3">
                <h2 id="wallet-title" className="text-[15px] font-medium">
                  Ví của bạn
                </h2>
                {access ? <span className={styles.chip}>Cơ bản</span> : null}
              </div>
              {userId === null ? (
                <div className="mt-6 flex flex-col items-start gap-4">
                  <p className="text-sm text-muted">Đăng nhập để xem số dư của bạn.</p>
                  <Link
                    href="/login"
                    className="pill-ghost rounded-full px-5 py-3 text-sm font-semibold no-underline"
                  >
                    Đăng nhập
                  </Link>
                </div>
              ) : account.isError ? (
                <div className="mt-6 flex flex-col items-start gap-4">
                  <p className="text-sm text-muted" role="alert">
                    Không tải được thông tin tài khoản.
                  </p>
                  <Pill
                    variant="ghost"
                    className="px-5 py-3 text-sm"
                    disabled={account.isFetching}
                    onClick={() => void account.refetch()}
                  >
                    Thử lại
                  </Pill>
                </div>
              ) : access === undefined ? (
                <p className="mt-6 text-sm text-muted" role="status">
                  Đang tải thông tin tài khoản…
                </p>
              ) : (
                <>
                  <div
                    className={`${styles.gold} my-5 flex flex-wrap items-center gap-3`}
                    aria-label="Số dư tài khoản"
                  >
                    <svg
                      viewBox="0 0 48 48"
                      className="size-11 shrink-0"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      aria-hidden="true"
                    >
                      <circle cx="24" cy="24" r="21" />
                      <circle cx="24" cy="24" r="15" />
                      <path d="m24 13 6 11-6 11-6-11 6-11Z" />
                    </svg>
                    <strong className="font-display text-[44px] leading-none font-medium break-all tabular-nums sm:text-[68px]">
                      {access.balance.toLocaleString("vi-VN")}
                    </strong>
                    <span className="mt-5 text-lg">xu</span>
                  </div>
                  <p className="text-[13px] leading-relaxed text-muted">
                    Mỗi câu trả lời AI hoàn tất dùng 3 xu trong gói Cơ bản.
                  </p>
                </>
              )}
            </div>

            <fieldset className="min-w-0 p-6 md:p-7">
              <legend className="sr-only">Chọn thêm xu</legend>
              <h3 className="font-display text-[25px]">Chọn thêm xu</h3>
              <p className="mt-2 mb-5 text-[13px] leading-relaxed text-muted">
                Các mức xu dưới đây chỉ để minh họa, chưa phải gói bán chính thức.
              </p>
              <div className="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-3">
                {BUNDLES.map((amount) => (
                  <label
                    key={amount}
                    className={`${styles.option} flex cursor-pointer flex-col gap-3 rounded-[18px] border border-glass-line p-4`}
                  >
                    <span className="flex items-center justify-between gap-2">
                      <strong className={`${styles.gold} text-[23px] font-semibold`}>
                        {amount} xu
                      </strong>
                      <input
                        type="radio"
                        name="coin-bundle"
                        value={amount}
                        checked={selectedCoins === amount}
                        onChange={() => setSelectedCoins(amount)}
                        aria-label={`${amount} xu`}
                        className="size-4 shrink-0"
                      />
                    </span>
                    <small className="text-[12px] leading-relaxed text-muted">
                      {amount / 3} câu trả lời AI hoàn tất
                    </small>
                    <small className="border-t border-glass-line pt-3 text-[11px] text-muted">
                      Giá sẽ được cập nhật
                    </small>
                  </label>
                ))}
              </div>
              <div className="mt-6 flex flex-wrap items-center justify-between gap-4 border-t border-glass-line pt-6">
                <div aria-live="polite" aria-atomic="true">
                  <p className="text-sm">
                    Bạn chọn <strong className={styles.gold}>{selectedCoins} xu</strong>
                  </p>
                  <p className="mt-1 text-xs text-muted">
                    Tương đương {selectedCoins / 3} câu trả lời AI hoàn tất.
                  </p>
                </div>
                <Pill
                  className={`${styles.coinButton} w-full px-5 py-3 text-sm md:w-auto`}
                  onClick={comingSoon}
                >
                  Chọn gói xu
                </Pill>
              </div>
            </fieldset>
          </section>
        ) : null}

        <aside
          className={`${styles.premium} min-w-0 rounded-card border p-6 md:p-7`}
          aria-labelledby="premium-title"
        >
          <div className="flex items-center justify-between gap-3">
            <span className={styles.chip}>{fullUnlock ? "Đang sử dụng" : "Một lựa chọn khác"}</span>
            <svg
              className={`${styles.gold} size-10 shrink-0`}
              viewBox="0 0 40 40"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.6"
              aria-hidden="true"
            >
              <path d="m5 11 9 6 6-11 6 11 9-6-4 19H9L5 11Z" />
              <path d="M12 35h16" />
            </svg>
          </div>
          <h2
            id="premium-title"
            className={`${styles.gold} mt-7 font-display text-[36px] leading-tight`}
          >
            Mở khóa toàn bộ
          </h2>
          <p className="mt-4 text-[20px] leading-relaxed">
            Trò chuyện cùng AI.
            <br />
            Không cần tính xu.
          </p>
          <p className="mt-5 text-[13px] leading-relaxed text-muted">
            {fullUnlock
              ? "Trò chuyện với AI đã được bao gồm trong gói của bạn."
              : "Dành cho bạn muốn trò chuyện với AI mà không cần nạp xu riêng."}
          </p>
          <ul className="my-7 space-y-3 text-sm leading-relaxed">
            <li className={styles.feature}>Trò chuyện với AI được bao gồm trong gói.</li>
            <li className={styles.feature}>Không trừ xu khi sử dụng trò chuyện với AI.</li>
          </ul>
          {!fullUnlock ? (
            <>
              <Pill
                className={`${styles.unlockButton} w-full px-5 py-3 text-sm`}
                onClick={comingSoon}
              >
                Mở khóa toàn bộ
              </Pill>
              <p className="mt-4 text-center text-xs text-muted">Giá sẽ được cập nhật</p>
            </>
          ) : null}
        </aside>
      </div>

      {!fullUnlock ? (
        <aside
          className="my-6 grid gap-4 rounded-[20px] border border-glass-line p-5 text-[13px] leading-relaxed text-muted md:grid-cols-2 md:gap-6"
          aria-label="Cách tính xu"
        >
          <p>
            <strong className="text-ink">Chỉ tính khi câu trả lời hoàn tất.</strong>
            <br />
            Gói Cơ bản dùng 3 xu cho mỗi câu trả lời AI hoàn tất.
          </p>
          <p>
            <strong className="text-ink">AI lỗi hoặc bạn hủy: không tính xu.</strong>
            <br />
            Hủy trước khi AI trả lời hoàn tất sẽ không bị trừ xu.
          </p>
        </aside>
      ) : null}
      <p className="mt-6 text-xs leading-relaxed text-muted">
        Tính năng mua gói và nạp xu sẽ được cập nhật. Các lựa chọn trên trang không thay đổi gói sử
        dụng hoặc số dư của bạn.
      </p>
    </div>
  );
}
