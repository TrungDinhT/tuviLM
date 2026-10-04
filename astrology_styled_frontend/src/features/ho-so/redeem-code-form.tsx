"use client";

import { type FormEvent, useState } from "react";

import { Pill } from "@/components/primitives/pill";
import { useRedeemCode } from "@/lib/api/hooks";
import { describe, isApiError } from "@/lib/http/errors";

export function RedeemCodeForm() {
  const [code, setCode] = useState("");
  const redeem = useRedeemCode();

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!code.trim() || redeem.isPending) return;
    redeem.mutate(code, { onSuccess: () => setCode("") });
  }

  return (
    <section className="mt-[26px]" aria-labelledby="redeem-code-heading">
      <h2 id="redeem-code-heading" className="mx-[2px] mb-3 text-[22px] font-semibold">
        Nhập mã nhận xu
      </h2>
      <form className="glass flex flex-col gap-3 p-5" onSubmit={submit}>
        <p className="text-[13px] leading-relaxed text-muted">
          Nhập mã còn hạn để nhận thêm xu vào tài khoản.
        </p>
        <label htmlFor="redeem-code" className="text-sm font-medium">
          Mã ưu đãi
        </label>
        <input
          id="redeem-code"
          name="code"
          type="text"
          autoComplete="off"
          autoCapitalize="characters"
          spellCheck={false}
          maxLength={64}
          required
          disabled={redeem.isPending}
          value={code}
          onChange={(event) => {
            setCode(event.target.value);
            redeem.reset();
          }}
          placeholder="Nhập mã của bạn"
          className="min-h-[50px] w-full min-w-0 rounded-[14px] border border-glass-line bg-white/7 px-3.5 py-3 text-[15px] text-ink outline-none placeholder:text-muted/70 focus:border-accent focus:ring-2 focus:ring-accent-glow disabled:opacity-50"
        />
        <Pill type="submit" disabled={!code.trim() || redeem.isPending}>
          {redeem.isPending ? "Đang kiểm tra…" : "Nhận xu"}
        </Pill>
        {redeem.isSuccess && (
          <p role="status" className="text-[13px] leading-relaxed text-accent">
            Nhập mã thành công! Bạn nhận được {redeem.data.coins.toLocaleString("vi-VN")} xu.
          </p>
        )}
        {redeem.isError && (
          <p role="alert" className="text-[13px] leading-relaxed text-fire">
            Nhập mã thất bại. {redeemErrorMessage(redeem.error)}
          </p>
        )}
      </form>
    </section>
  );
}

function redeemErrorMessage(error: unknown): string {
  if (!isApiError(error)) return "Bạn thử lại nhé.";
  if (error.error.kind === "http") {
    switch (error.error.status) {
      case 401:
        return "Vui lòng đăng nhập lại để nhập mã.";
      case 404:
        return "Mã không hợp lệ hoặc đã hết hạn.";
      case 409: {
        const detail =
          error.error.body !== null &&
          typeof error.error.body === "object" &&
          "detail" in error.error.body
            ? error.error.body.detail
            : undefined;
        if (detail === "Balance limit exceeded.") {
          return "Số dư của bạn đã đạt giới hạn, không thể nhận thêm xu.";
        }
        if (detail === "Chat coins are reserved. Try again when the reply finishes.") {
          return "Vui lòng đợi cuộc trò chuyện hiện tại hoàn tất rồi nhập lại mã.";
        }
        return "Mã này đã được sử dụng.";
      }
      case 422:
        return "Vui lòng kiểm tra lại mã.";
    }
  }
  return describe(error.error);
}
