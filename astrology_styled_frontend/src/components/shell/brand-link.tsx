import Image from "next/image";
import Link from "next/link";

import { cn } from "@/lib/utils";

export function BrandLink({
  className,
  showTagline = false,
}: {
  className?: string;
  showTagline?: boolean;
}) {
  return (
    <Link
      href="/"
      aria-label="Thiên Hạc — về trang chủ"
      className={cn(
        "inline-flex h-11 shrink-0 items-center gap-2 text-ink no-underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent",
        className,
      )}
    >
      <span className="grid h-11 w-10 shrink-0 place-items-center max-[349px]:w-8">
        <Image
          src="/assets/icons/favicon-48x48.png"
          alt=""
          width={48}
          height={48}
          className="size-10 drop-shadow-[0_0_10px_rgba(255,222,143,0.26)] max-[349px]:size-8"
        />
      </span>
      <span className="flex h-11 shrink-0 flex-col justify-center whitespace-nowrap">
        <span className="font-display text-lg font-semibold max-[349px]:text-sm">Thiên Hạc</span>
        {showTagline ? (
          <small className="mt-0.5 text-[9px] font-semibold tracking-[0.16em] text-muted uppercase">
            An sao &amp; luận giải
          </small>
        ) : null}
      </span>
    </Link>
  );
}
