"use client";

import { type FormEvent, useState } from "react";
import Link from "next/link";

import { Pill } from "@/components/primitives/pill";
import { useAccountRequestScope } from "@/lib/api/account-request";
import { useAccountAccess, useCreateRedeemCode } from "@/lib/api/hooks";
import { describe, isApiError } from "@/lib/http/errors";

const INPUT_CLASS =
  "min-h-[50px] w-full min-w-0 rounded-[14px] border border-glass-line bg-bg-1 px-3.5 py-3 text-[15px] text-ink outline-none focus:border-accent focus:ring-2 focus:ring-accent-glow";

export function RedeemCodesScreen() {
  const { userId } = useAccountRequestScope();
  const account = useAccountAccess();
  const create = useCreateRedeemCode();
  const [validationError, setValidationError] = useState("");

  if (userId === null) {
    return (
      <p className="mt-6 text-sm text-muted">
        Vui lòng <Link href="/login">đăng nhập</Link> để truy cập trang quản trị.
      </p>
    );
  }
  if (userId === undefined || account.isPending || account.isFetching) {
    return (
      <p role="status" className="mt-6 text-sm text-muted">
        Đang kiểm tra quyền truy cập…
      </p>
    );
  }
  if (account.isError) {
    return (
      <div className="mt-6 flex flex-col items-start gap-3">
        <p role="alert" className="text-sm text-muted">
          Không kiểm tra được quyền truy cập.
        </p>
        <Pill variant="ghost" onClick={() => void account.refetch()}>
          Thử lại
        </Pill>
      </div>
    );
  }
  if (!account.isSuccess || account.data.user_id !== userId || account.data.role !== "admin") {
    return (
      <p role="alert" className="mt-6 text-sm text-muted">
        Bạn không có quyền truy cập trang quản trị.
      </p>
    );
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (create.isPending) return;
    create.reset();
    setValidationError("");
    const fields = new FormData(event.currentTarget);
    const coins = Number(fields.get("coins"));
    const days = Number(fields.get("days"));
    const kind = fields.get("kind");
    const expiresAt = new Date(Date.now() + days * 86_400_000);
    if (
      !Number.isSafeInteger(coins) ||
      coins <= 0 ||
      !Number.isSafeInteger(days) ||
      days <= 0 ||
      !Number.isFinite(expiresAt.getTime()) ||
      (kind !== "single_use" && kind !== "per_account")
    ) {
      setValidationError("Số xu và thời hạn phải là số nguyên dương hợp lệ.");
      return;
    }
    create.mutate({ coins, kind, expires_at: expiresAt.toISOString() });
  }

  return (
    <section className="mt-6 max-w-[620px]">
      <form className="glass p-5 sm:p-6" onSubmit={submit}>
        <fieldset disabled={create.isPending} className="flex min-w-0 flex-col gap-4">
          <legend className="mb-4 font-display text-[25px] font-semibold">Thông tin mã</legend>
          <label className="flex flex-col gap-2 text-sm font-medium">
            Số xu
            <input
              name="coins"
              type="number"
              min={1}
              max={Number.MAX_SAFE_INTEGER}
              step={1}
              defaultValue={30}
              required
              className={INPUT_CLASS}
            />
          </label>
          <label className="flex flex-col gap-2 text-sm font-medium">
            Loại mã
            <select name="kind" defaultValue="single_use" className={INPUT_CLASS}>
              <option value="single_use">Chỉ dùng một lần</option>
              <option value="per_account">Một lần cho mỗi tài khoản</option>
            </select>
          </label>
          <p className="text-[13px] leading-relaxed text-muted">
            Mã dùng một lần chỉ dành cho một tài khoản. Mã cho mỗi tài khoản có thể chia sẻ, nhưng
            mỗi tài khoản chỉ được nhận xu một lần.
          </p>
          <label className="flex flex-col gap-2 text-sm font-medium">
            Thời hạn (ngày)
            <input
              name="days"
              type="number"
              min={1}
              step={1}
              defaultValue={3}
              required
              className={INPUT_CLASS}
            />
          </label>
          <p className="text-[13px] leading-relaxed text-muted">Thời hạn bắt đầu từ lúc tạo mã.</p>
          <Pill type="submit" disabled={create.isPending}>
            {create.isPending ? "Đang tạo mã…" : "Tạo mã"}
          </Pill>
        </fieldset>
        {(validationError || create.isError) && (
          <p role="alert" className="mt-4 text-[13px] leading-relaxed text-fire">
            {validationError || `Tạo mã thất bại. ${createErrorMessage(create.error)}`}
          </p>
        )}
      </form>
      {create.isSuccess && (
        <div role="status" className="glass mt-5 p-5 sm:p-6">
          <h2 className="text-lg font-semibold text-accent">Tạo mã thành công</h2>
          <code className="mt-3 block select-all rounded-[14px] border border-glass-line bg-bg-1 p-3 text-base break-all">
            {create.data.code}
          </code>
          <p className="mt-3 text-sm">
            {create.data.coins.toLocaleString("vi-VN")} xu ·{" "}
            {create.data.kind === "single_use" ? "Chỉ dùng một lần" : "Một lần cho mỗi tài khoản"}
          </p>
          <p className="mt-2 text-[13px] text-muted">
            Hết hạn:{" "}
            {new Date(create.data.expires_at).toLocaleString("vi-VN", {
              dateStyle: "medium",
              timeStyle: "short",
            })}
          </p>
        </div>
      )}
    </section>
  );
}

function createErrorMessage(error: unknown): string {
  if (!isApiError(error)) return "Bạn thử lại nhé.";
  if (error.error.kind === "http" && error.error.status === 401) return "Vui lòng đăng nhập lại.";
  if (error.error.kind === "http" && error.error.status === 403)
    return "Bạn không có quyền tạo mã.";
  return describe(error.error);
}
