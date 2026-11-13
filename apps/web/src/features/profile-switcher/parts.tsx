import { cn } from "@/lib/utils";

export function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="px-1 text-[10px] font-bold tracking-[0.22em] text-muted uppercase">
      {children}
    </div>
  );
}

/** The name's first letter; auto-named charts start with a digit and get the star. */
export function Avatar({ name, quiet = false }: { name: string; quiet?: boolean }) {
  const first = name.trim().charAt(0);
  const initial = /\p{L}/u.test(first) ? first.toLocaleUpperCase("vi") : "✦";
  return (
    <span
      aria-hidden="true"
      className={cn(
        "grid size-8 shrink-0 place-items-center rounded-full text-[13px] font-semibold",
        quiet ? "bg-white/8 text-ink" : "accent-gradient text-bg-0 shadow-none",
      )}
    >
      {initial}
    </span>
  );
}
