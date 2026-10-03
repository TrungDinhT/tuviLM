"use client";

import { useRouter } from "next/navigation";

export function NotFoundBackButton() {
  const router = useRouter();

  return (
    <button
      type="button"
      className="inline-flex min-h-[50px] w-full cursor-pointer items-center justify-center rounded-[14px] border border-glass-line bg-transparent px-5 font-bold text-ink transition-[transform,background,border-color] hover:border-ink hover:bg-white/[0.07] active:translate-y-px sm:w-auto"
      onClick={() => {
        if (window.history.length > 1) router.back();
        else router.push("/");
      }}
    >
      Quay lại
    </button>
  );
}
