import Link from "next/link";

import { NotFoundBackButton } from "@/features/auth/not-found-back-button";

export default function NotFound() {
  return (
    <div className="min-h-dvh bg-bg-0">
      <main>
        <section className="grid min-h-[calc(100dvh-72px-var(--safe-t))] place-items-center py-[46px] md:min-h-[calc(100dvh-78px-var(--safe-t))] md:py-20 lg:py-8">
          <div className="mx-auto grid w-full max-w-[1120px] items-center gap-[42px] px-5 text-center sm:px-8 md:grid-cols-[.9fr_1.1fr] md:gap-[clamp(56px,8vw,110px)] md:text-left lg:grid-cols-2 lg:px-14">
            <div
              className="relative isolate grid min-h-[220px] place-items-center md:min-h-[430px]"
              aria-hidden="true"
            >
              <div className="absolute aspect-square w-[min(72vw,330px)] -rotate-[14deg] rounded-full border border-glass-line md:w-[min(34vw,380px)]">
                <div className="absolute inset-[16%] rotate-[22deg] rounded-full border border-glass-line" />
                <span className="absolute top-[19%] right-[11%] size-3 rounded-full border border-accent bg-accent shadow-[0_0_28px_var(--accent)]" />
              </div>
              <div className="relative z-1 font-display text-[clamp(104px,30vw,180px)] leading-[0.78] font-semibold tracking-[-0.08em] text-ink md:text-[clamp(160px,18vw,220px)]">
                404
              </div>
            </div>

            <div className="mx-auto max-w-[540px] md:mx-0 lg:pl-2.5">
              <p className="mb-[18px] font-mono text-xs tracking-[0.1em] text-muted uppercase">
                Lạc khỏi quỹ đạo
              </p>
              <h1 className="font-display text-[clamp(40px,8vw,68px)] leading-[1.02] font-semibold tracking-[-0.035em] text-balance">
                Trang không tồn tại
              </h1>
              <p className="mx-auto mt-5 max-w-[46ch] text-base leading-[1.55] text-muted md:mx-0 md:text-[17px]">
                Đường dẫn có thể đã thay đổi hoặc nội dung đã được chuyển. Bạn có thể quay lại màn
                hình trước hoặc bắt đầu từ trang chính.
              </p>

              <div className="mt-[30px] grid gap-3 sm:flex sm:flex-wrap sm:justify-center md:justify-start">
                <Link
                  href="/"
                  className="inline-flex min-h-[50px] w-full items-center justify-center rounded-[14px] border border-accent bg-accent px-5 font-bold text-bg-0 transition-[transform,background,border-color] hover:bg-[color-mix(in_oklch,var(--accent)_86%,var(--color-ink))] active:translate-y-px sm:w-auto"
                >
                  Về trang chính
                </Link>
                <NotFoundBackButton />
              </div>

              <p className="mt-[26px] border-t border-glass-line pt-[22px] text-[13px] text-muted">
                Không tìm thấy tài nguyên theo đường dẫn hiện tại.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
