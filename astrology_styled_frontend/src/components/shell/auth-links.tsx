"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { authClient } from "@/lib/auth-client";
import { cn } from "@/lib/utils";

export function AuthLinks({ className }: { className?: string }) {
  const router = useRouter();
  const { data: session, isPending } = authClient.useSession();
  const [isSigningOut, setIsSigningOut] = useState(false);

  if (session !== null && session !== undefined) {
    const initial = session.user.name.trim().charAt(0).toLocaleUpperCase("vi") || "✦";

    return (
      <div className={cn("flex min-w-0 items-center gap-2", className)} aria-label="Tài khoản">
        <span className="pill-ghost inline-flex min-h-9 min-w-0 items-center gap-2 rounded-full px-2.5 text-[13px] font-semibold">
          <span className="accent-gradient grid size-6 shrink-0 place-items-center rounded-full text-[11px] text-bg-0">
            {initial}
          </span>
          <span className="hidden max-w-28 truncate md:inline">{session.user.name}</span>
        </span>
        <button
          type="button"
          disabled={isSigningOut}
          className="cursor-pointer border-0 px-2 py-2 text-[12px] font-semibold text-muted transition-colors hover:text-ink disabled:cursor-wait disabled:opacity-50"
          onClick={() => void signOut()}
        >
          {isSigningOut ? "Đang thoát…" : "Đăng xuất"}
        </button>
      </div>
    );
  }

  return (
    <div
      className={cn("flex items-center gap-2", isPending && "opacity-70", className)}
      aria-label="Tài khoản"
    >
      <Link
        href="/login"
        className="pill-ghost inline-flex min-h-9 items-center justify-center rounded-full px-4 text-[13px] font-semibold transition-transform active:scale-[0.97] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent-glow)]"
      >
        Đăng nhập
      </Link>
      <Link
        href="/register"
        className="pill-primary inline-flex min-h-9 items-center justify-center rounded-full px-4 text-[13px] font-semibold transition-transform active:scale-[0.97] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--accent-glow)]"
      >
        Đăng ký
      </Link>
    </div>
  );

  async function signOut() {
    setIsSigningOut(true);
    try {
      await authClient.signOut();
      router.replace("/");
      router.refresh();
    } finally {
      setIsSigningOut(false);
    }
  }
}
