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
          aria-label="Tử Vi — về trang chính"
        >
          <span className="grid size-[30px] place-items-center rounded-full border border-glass-line transition-colors group-hover:border-ink">
            <BrandGlyph />
          </span>
          <span>Tử Vi</span>
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

function BrandGlyph() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="size-4"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="8" />
      <path d="M12 4c2.5 2.7 3.8 5.3 3.8 8S14.5 17.3 12 20M8 8.5h8M8 15.5h8" />
    </svg>
  );
}
