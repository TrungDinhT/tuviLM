import Image from "next/image";
import Link from "next/link";

type StandaloneHeaderProps = {
  actionHref: string;
  actionLabel: string;
  prompt: string;
};

export function StandaloneHeader({ actionHref, actionLabel, prompt }: StandaloneHeaderProps) {
  return (
    <header className="relative z-10 border-b border-glass-line bg-bg-0">
      <div className="mx-auto flex min-h-[calc(72px+var(--safe-t))] w-full max-w-[1200px] items-center justify-between gap-5 px-5 pt-[var(--safe-t)] sm:px-8 md:min-h-[calc(78px+var(--safe-t))] lg:px-14">
        <Link
          href="/"
          className="group inline-flex min-h-11 items-center gap-2.5 font-display text-xl font-semibold text-ink no-underline"
          aria-label="Thiên Hạc — về trang chính"
        >
          <Image
            src="/assets/icons/favicon-48x48.png"
            alt=""
            width={48}
            height={48}
            className="size-9 drop-shadow-[0_0_10px_rgba(255,222,143,0.26)]"
          />
          <span>Thiên Hạc</span>
        </Link>

        <Link
          href={actionHref}
          className="inline-flex min-h-11 items-center text-sm text-muted transition-colors hover:text-ink"
        >
          <span className="hidden md:inline">{prompt}&nbsp;</span>
          <strong className="text-ink">{actionLabel}</strong>
        </Link>
      </div>
    </header>
  );
}
