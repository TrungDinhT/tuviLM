"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { authClient } from "@/lib/auth-client";
import { cn } from "@/lib/utils";

export function SignOutButton({ className }: { className?: string }) {
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);

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

  return (
    <button
      type="button"
      disabled={isSigningOut}
      className={cn(
        "inline-flex cursor-pointer items-center gap-3 border-0 transition-colors disabled:cursor-wait disabled:opacity-50",
        className,
      )}
      onClick={() => void signOut()}
    >
      <svg
        className="hidden size-5 shrink-0 lg:block"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        <path d="M9 5H5v14h4M16 8l4 4-4 4M9 12h11" />
      </svg>
      Đăng xuất
    </button>
  );
}
